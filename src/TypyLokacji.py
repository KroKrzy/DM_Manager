
import os
import json
import tkinter as tk
from tkinter import Toplevel, Label, Button, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk

class TypyLokacji:
    def __init__(self, master, save_data, save_filename, resources_path):
        self.save_data = save_data
        self.save_filename = save_filename
        self.resources_path = resources_path
        self.selected_index = None

        self.window = Toplevel(master)
        self.window.title("Typy lokacji")
        self.window.geometry("400x500")

        self.frame = tk.Frame(self.window)
        self.frame.pack(fill=tk.BOTH, expand=True)

        if "location_types" not in self.save_data:
            self.save_data["location_types"] = []
            self.save()

        # Scrollable area
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.display_location_types()

        # Przyciski na dole
        self.buttons_frame = tk.Frame(self.window)
        self.buttons_frame.pack(pady=10)

        Button(self.buttons_frame, text="Dodaj typ", command=self.add_location_type).pack(side=tk.LEFT, padx=5)
        Button(self.buttons_frame, text="Edytuj typ", command=self.edit_location_type).pack(side=tk.LEFT, padx=5)
        Button(self.buttons_frame, text="Usuń typ", command=self.remove_location_type).pack(side=tk.LEFT, padx=5)

    def display_location_types(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for index, typ in enumerate(self.save_data["location_types"]):
            row = tk.Frame(self.scrollable_frame)
            row.pack(fill=tk.X, padx=5, pady=2)

            # Nazwa z lewej
            name_label = tk.Label(row, text=typ["nazwa"], anchor="w", width=20)
            name_label.pack(side=tk.LEFT, padx=(5, 0))

            # Ikona z prawej
            icon_path = os.path.join(self.resources_path, typ["ikona"])
            try:
                img = Image.open(icon_path)
                img.thumbnail((32, 32))
                icon = ImageTk.PhotoImage(img)

                icon_label = tk.Label(row, image=icon)
                icon_label.image = icon
            except Exception:
                icon_label = tk.Label(row, text="[Brak ikony]")

            icon_label.pack(side=tk.RIGHT, padx=(0, 5))

            row.bind("<Button-1>", lambda e, idx=index: self.select_index(idx))
            name_label.bind("<Button-1>", lambda e, idx=index: self.select_index(idx))
            icon_label.bind("<Button-1>", lambda e, idx=index: self.select_index(idx))

            if index == self.selected_index:
                row.config(bg="#d0e0ff")
                name_label.config(bg="#d0e0ff")
                icon_label.config(bg="#d0e0ff")

    def select_index(self, index):
        self.selected_index = index
        self.display_location_types()

    def add_location_type(self):
        name = simpledialog.askstring("Nowy typ", "Podaj nazwę typu:")
        if not name:
            return

        filetypes = [("Pliki graficzne", "*.png *.jpg *.jpeg *.bmp")]
        icon_file = filedialog.askopenfilename(
            title="Wybierz ikonę",
            initialdir=self.resources_path,
            filetypes=filetypes
        )
        if not icon_file:
            return

        icon_name = os.path.basename(icon_file)

        self.save_data["location_types"].append({
            "nazwa": name,
            "ikona": icon_name
        })
        self.save()
        self.display_location_types()

    def edit_location_type(self):
        if self.selected_index is None:
            return

        typ = self.save_data["location_types"][self.selected_index]
        new_name = simpledialog.askstring("Edytuj nazwę", "Nowa nazwa:", initialvalue=typ["nazwa"])
        if new_name:
            typ["nazwa"] = new_name

        if messagebox.askyesno("Ikona", "Czy chcesz zmienić ikonę?"):
            filetypes = [("Pliki graficzne", "*.png *.jpg *.jpeg *.bmp")]
            icon_file = filedialog.askopenfilename(
                title="Wybierz nową ikonę",
                initialdir=self.resources_path,
                filetypes=filetypes
            )
            if icon_file:
                typ["ikona"] = os.path.basename(icon_file)

        self.save()
        self.display_location_types()

    def remove_location_type(self):
        if self.selected_index is None:
            return

        if not messagebox.askyesno("Potwierdzenie", "Czy na pewno usunąć ten typ?"):
            return

        del self.save_data["location_types"][self.selected_index]
        self.selected_index = None
        self.save()
        self.display_location_types()

    def save(self):
        with open(self.save_filename, 'w', encoding='utf-8') as f:
            json.dump(self.save_data, f, ensure_ascii=False, indent=2)
