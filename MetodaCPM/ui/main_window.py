import tkinter as tk
from ui.cpm_window import open_cpm_window
from ui.mediator_window import open_mediator_window

def launch_main_window():
    root = tk.Tk()
    root.title("Aplikacja CPM i Pośrednik")
    root.geometry("300x200")

    tk.Label(root, text="Wybierz moduł:", font=("Arial", 14)).pack(pady=10)

    tk.Button(root, text="Metoda CPM", width=20, command=lambda: open_cpm_window(root)).pack(pady=5)
    tk.Button(root, text="Zagadnienie pośrednika", width=20, command=lambda: open_mediator_window(root)).pack(pady=5)

    root.mainloop()
