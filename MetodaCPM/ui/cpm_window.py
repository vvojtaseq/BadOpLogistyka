import tkinter as tk
from tkinter import ttk, messagebox
from logic.cpm_solver import calculate_cpm
from utils.graph_drawer import draw_aoa_graph


task_list = []

def open_cpm_window(parent):
    window = tk.Toplevel(parent)
    window.title("Moduł CPM")
    window.geometry("600x500")

    # Formularz danych wejściowych
    tk.Label(window, text="Nazwa czynności:").grid(row=0, column=0)
    entry_name = tk.Entry(window)
    entry_name.grid(row=0, column=1)

    tk.Label(window, text="Czas trwania:").grid(row=1, column=0)
    entry_duration = tk.Entry(window)
    entry_duration.grid(row=1, column=1)

    tk.Label(window, text="Poprzednicy (oddziel przecinkami):").grid(row=2, column=0)
    entry_predecessors = tk.Entry(window)
    entry_predecessors.grid(row=2, column=1)

    def add_task():
        name = entry_name.get().strip()
        duration = int(entry_duration.get().strip())
        predecessors = [p.strip() for p in entry_predecessors.get().split(",") if p.strip()]
        task_list.append({"name": name, "duration": duration, "predecessors": predecessors})
        update_task_view()
        entry_name.delete(0, tk.END)
        entry_duration.delete(0, tk.END)
        entry_predecessors.delete(0, tk.END)

    def update_task_view():
        for i in tree.get_children():
            tree.delete(i)
        for task in task_list:
            tree.insert("", tk.END, values=(task["name"], task["duration"], ", ".join(task["predecessors"])))

    def run_cpm():
        try:
            results = calculate_cpm(task_list)
            messagebox.showinfo("Wyniki CPM", results)
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    # Przycisk dodania czynności
    tk.Button(window, text="Dodaj czynność", command=add_task).grid(row=3, column=1, pady=10)

    # Widok tabeli
    tree = ttk.Treeview(window, columns=("Nazwa", "Czas", "Poprzednicy"), show="headings")
    tree.heading("Nazwa", text="Nazwa")
    tree.heading("Czas", text="Czas trwania")
    tree.heading("Poprzednicy", text="Poprzednicy")
    tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Przycisk obliczenia CPM
    tk.Button(window, text="Oblicz CPM", command=run_cpm).grid(row=5, column=1, pady=10)
    # Przycisk do rysowania grafu AOA
    tk.Button(window, text="Pokaż graf AOA", command=lambda: draw_aoa_graph(task_list)).grid(row=6, column=1, pady=10)

