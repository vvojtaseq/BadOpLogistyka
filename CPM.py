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
        self.entries = []  # Tutaj będziemy przechowywać wszystkie widżety Entry
        self.create_widgets()

    def create_widgets(self):
        frm_mode = ttk.Frame(self.root, padding="5")
        frm_mode.grid(row=0, column=0, sticky="w")
        ttk.Label(frm_mode, text="Tryb wprowadzania:").pack(side="left")
        ttk.Radiobutton(frm_mode, text="Zadania z poprzednikami", variable=self.mode, value="classic", command=self.draw_input_fields).pack(side="left")
        ttk.Radiobutton(frm_mode, text="Relacje", variable=self.mode, value="edge", command=self.draw_input_fields).pack(side="left")

        frm_input = ttk.Frame(self.root, padding="10")
        frm_input.grid(row=1, column=0, sticky="nw")

        self.frm_input = frm_input
        self.draw_input_fields()

        self.btn_calc = ttk.Button(self.root, text="Oblicz CPM", command=self.run_cpm)
        self.btn_calc.grid(row=2, column=0, pady=10)

    def draw_input_fields(self):
        # Usuwamy wszystkie aktualne widżety w tym oknie wejściowym
        for widget in self.frm_input.winfo_children():
            widget.destroy()

        # Tworzymy nagłówki na podstawie wybranego trybu
        if self.mode.get() == "classic":
            ttk.Label(self.frm_input, text="Nazwa").grid(column=0, row=0)
            ttk.Label(self.frm_input, text="Czas trwania").grid(column=1, row=0)
            ttk.Label(self.frm_input, text="Poprzednicy (np. A,B)").grid(column=2, row=0)
        else:
            ttk.Label(self.frm_input, text="Nazwa").grid(column=0, row=0)
            ttk.Label(self.frm_input, text="Czas trwania").grid(column=1, row=0)
            ttk.Label(self.frm_input, text="Relacja (np. 1-2)").grid(column=2, row=0)

        # Zmieniamy liczbę kolumn w zależności od trybu
        cols = 3 if self.mode.get() == "classic" else 3

        # Tworzymy pola wejściowe tylko raz, a później je tylko aktualizujemy
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
            durations = {}

            if mode == "classic":
                for row in self.entries:
                    name = row[0].get().strip()
                    if not name:
                        continue
                    duration = int(row[1].get().strip())
                    preds = row[2].get().strip().split(",") if row[2].get().strip() else []
                    preds = [p.strip() for p in preds if p.strip()]
                    self.activities.append((name, duration, preds))
                    durations[name] = duration
                    if not preds:
                        graph.add_node(name)
                    for pred in preds:
                        graph.add_edge(pred, name)
            else:
                # edge mode: 1-2 style
                nodes_set = set()
                for row in self.entries:
                    rel = row[0].get().strip()
                    if not rel:
                        continue
                    duration = int(row[1].get().strip())
                    start, end = rel.split("-")
                    start, end = start.strip(), end.strip()
                    graph.add_edge(start, end)
                    durations[start] = duration
                    nodes_set.update([start, end])

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

        tree = ttk.Treeview(win_table, columns=list(df.columns), show="headings")
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        tree.pack(expand=True, fill="both")

        try:
            pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
        except:
            pos = nx.spring_layout(graph, k=1.0, iterations=200)

        plt.figure(figsize=(12, 8))
        node_colors = ['red' if node in critical_path else 'lightblue' for node in graph.nodes]
        edge_colors = ['red' if u in critical_path and v in critical_path else 'gray' for u, v in graph.edges]

        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=2200, edgecolors='black')
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, width=2, arrows=True, connectionstyle='arc3,rad=0.1')

        custom_labels = {
            node: f"{node}\nES:{es[node]} EF:{ef[node]}\nLS:{ls[node]} LF:{lf[node]}\nSlack: {slack[node]}"
            for node in graph.nodes
        }
        nx.draw_networkx_labels(graph, pos, labels=custom_labels, font_size=9)

        edge_labels = {(u, v): str(durations.get(u, 0)) for u, v in graph.edges}
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=9)

        plt.title("Sieć CPM – Ścieżka krytyczna (czerwona)")
        plt.axis("off")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = CPMApp(root)
    root.mainloop()
