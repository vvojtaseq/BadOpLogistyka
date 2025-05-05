import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


class CPMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPM - Critical Path Method")

        self.activities = []
        self.mode = tk.StringVar(value="classic")
        self.entries = []
        self.create_widgets()

    def create_widgets(self):
        frm_mode = ttk.Frame(self.root, padding="5")
        frm_mode.grid(row=0, column=0, sticky="w")
        ttk.Label(frm_mode, text="Tryb wprowadzania:").pack(side="left")
        ttk.Radiobutton(frm_mode, text="Zadania z poprzednikami", variable=self.mode, value="classic", command=self.draw_input_fields).pack(side="left")
        ttk.Radiobutton(frm_mode, text="Relacje", variable=self.mode, value="edge", command=self.draw_input_fields).pack(side="left")

        self.frm_input = ttk.Frame(self.root, padding="10")
        self.frm_input.grid(row=1, column=0, sticky="nw")

        self.draw_input_fields()

        self.btn_calc = ttk.Button(self.root, text="Oblicz CPM", command=self.run_cpm)
        self.btn_calc.grid(row=2, column=0, pady=10)

    def draw_input_fields(self):
        for widget in self.frm_input.winfo_children():
            widget.destroy()

        if self.mode.get() == "classic":
            ttk.Label(self.frm_input, text="Nazwa").grid(column=0, row=0)
            ttk.Label(self.frm_input, text="Czas trwania").grid(column=1, row=0)
            ttk.Label(self.frm_input, text="Poprzednicy (np. A,B)").grid(column=2, row=0)
        else:
            ttk.Label(self.frm_input, text="Relacja (np. 1-2)").grid(column=0, row=0)
            ttk.Label(self.frm_input, text="Czas trwania").grid(column=1, row=0)

        cols = 3 if self.mode.get() == "classic" else 2
        self.entries = []
        for i in range(10):
            row_entries = []
            for j in range(cols):
                entry = ttk.Entry(self.frm_input, width=15)
                entry.grid(column=j, row=i + 1)
                row_entries.append(entry)
            self.entries.append(row_entries)

    def run_cpm(self):
        try:
            self.activities.clear()
            mode = self.mode.get()
            graph = nx.DiGraph()

            if mode == "classic":
                durations = {}
                for row in self.entries:
                    name = row[0].get().strip()
                    if not name:
                        continue
                    duration = int(row[1].get().strip())
                    preds = row[2].get().strip().split(",") if row[2].get().strip() else []
                    preds = [p.strip() for p in preds if p.strip()]
                    durations[name] = duration
                    self.activities.append((name, duration, preds))
                    if not preds:
                        graph.add_node(name)
                    for pred in preds:
                        graph.add_edge(pred, name)

                # CPM classic
                es, ef = {}, {}
                for node in nx.topological_sort(graph):
                    es[node] = max([ef.get(pred, 0) for pred in graph.predecessors(node)], default=0)
                    ef[node] = es[node] + durations.get(node, 0)

                lf, ls = {}, {}
                max_time = max(ef.values())
                for node in reversed(list(nx.topological_sort(graph))):
                    lf[node] = min([ls.get(succ, max_time) for succ in graph.successors(node)], default=max_time)
                    ls[node] = lf[node] - durations.get(node, 0)

                slack = {node: ls[node] - es[node] for node in graph.nodes}
                critical_path = [node for node in graph.nodes if slack[node] == 0]

            else:
                for row in self.entries:
                    rel = row[0].get().strip()
                    if not rel:
                        continue
                    duration = int(row[1].get().strip())
                    start, end = [x.strip() for x in rel.split("-")]
                    graph.add_edge(start, end, weight=duration)

                durations = {node: 0 for node in graph.nodes}
                es, ef = {}, {}
                for node in nx.topological_sort(graph):
                    max_ef = 0
                    for pred in graph.predecessors(node):
                        edge_duration = graph[pred][node]['weight']
                        pred_ef = ef[pred]
                        max_ef = max(max_ef, pred_ef + edge_duration)
                    es[node] = max_ef
                    ef[node] = es[node]

                max_time = max(ef.values())
                lf, ls = {}, {}
                for node in reversed(list(nx.topological_sort(graph))):
                    min_ls = max_time
                    for succ in graph.successors(node):
                        edge_duration = graph[node][succ]['weight']
                        succ_ls = ls[succ] - edge_duration
                        min_ls = min(min_ls, succ_ls)
                    lf[node] = min_ls if list(graph.successors(node)) else max_time
                    ls[node] = lf[node]

                slack = {node: ls[node] - es[node] for node in graph.nodes}
                critical_path = [node for node in graph.nodes if slack[node] == 0]

            # Create DataFrame
            table_data = []
            for node in graph.nodes:
                table_data.append({
                    "Zadanie": node,
                    "ES": es[node],
                    "EF": ef[node],
                    "LS": ls[node],
                    "LF": lf[node],
                    "Rezerwa": slack[node],
                    "Krytyczna": "TAK" if node in critical_path else ""
                })

            df = pd.DataFrame(table_data)
            self.show_results(df, graph, critical_path, es, ef, ls, lf, slack, durations)

        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def show_results(self, df, graph, critical_path, es, ef, ls, lf, slack, durations):
        win_table = tk.Toplevel(self.root)
        win_table.title("Wyniki CPM - Tabela")
        win_table.geometry("600x200")

        tree = ttk.Treeview(win_table, columns=list(df.columns), show="headings", height=20)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        tree.pack(expand=True, fill="both")

        try:
            pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
        except:
            pos = nx.spring_layout(graph, k=1.0, iterations=200)

        plt.figure(figsize=(10, 10))
        node_colors = ['lightcoral' if node in critical_path else 'lightblue' for node in graph.nodes]
        edge_colors = ['lightcoral' if u in critical_path and v in critical_path else 'gray' for u, v in graph.edges]

        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=4000, edgecolors='black', linewidths=1.5)
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, width=2, arrows=True)

        custom_labels = {
            node: f"{node}\nES:{es[node]} EF:{ef[node]}\nLS:{ls[node]} LF:{lf[node]}\nSlack: {slack[node]}"
            for node in graph.nodes
        }
        nx.draw_networkx_labels(graph, pos, labels=custom_labels, font_size=10)

        if self.mode.get() == "edge":
            edge_labels = {(u, v): str(graph[u][v]['weight']) for u, v in graph.edges}
        else:
            edge_labels = {(u, v): "" for u, v in graph.edges}

        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=9)

        plt.title("Sieć CPM – Ścieżka krytyczna (jasnoczerwona)", fontsize=14)
        plt.axis("off")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = CPMApp(root)
    root.mainloop()
