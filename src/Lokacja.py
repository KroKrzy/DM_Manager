
import os
import json
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, StringVar, OptionMenu, filedialog, messagebox, BooleanVar

class Lokacja:
    def __init__(self, master, location, save_data, save_filename, resources_path, on_close):
        self.location = location
        self.save_data = save_data
        self.save_filename = save_filename
        self.resources_path = resources_path
        self.on_close = on_close

        self.window = Toplevel(master)
        self.window.title("Szczegóły lokacji")
        self.window.geometry("400x400")
        self.window.transient(master)
        self.window.grab_set()

        Label(self.window, text="Nazwa:").pack()
        self.name_var = StringVar(value=location.get("nazwa", ""))
        Entry(self.window, textvariable=self.name_var).pack()

        Label(self.window, text="Typ:").pack()
        all_types = ["domyślna"] + [t["nazwa"] for t in save_data.get("location_types", [])]
        self.type_var = StringVar(value=location.get("typ", "domyślna"))
        OptionMenu(self.window, self.type_var, *all_types).pack()

        self.label_var = BooleanVar(value=location.get("etykieta", False))
        tk.Checkbutton(self.window, text="Pokaż etykietę", variable=self.label_var).pack()

        Label(self.window, text="Mapa lokacji (opcjonalnie):").pack(pady=(10, 2))

        if location.get("sub_map"):
            Button(self.window, text="Zmień mapę", command=self.change_sub_map).pack()
            self.sub_map_button = Button(self.window, text="Otwórz mapę lokacji", command=self.open_sub_map_editor)
            self.sub_map_button.pack(pady=5)
        else:
            Button(self.window, text="Dodaj mapę", command=self.add_sub_map).pack()
        Button(self.window, text="Opis lokacji", command=self.edit_description).pack(pady=5)
        Button(self.window, text="Lista postaci", command=self.open_npc_list).pack(pady=5)

        Button(self.window, text="Zapisz", command=self.save).pack(pady=10)
        Button(self.window, text="Usuń lokację", command=self.delete, fg="red").pack()

    def add_sub_map(self):
        filetypes = [("Obrazy", "*.png *.jpg *.jpeg *.bmp")]
        selected_file = filedialog.askopenfilename(
            title="Wybierz mapę lokacji",
            initialdir=self.resources_path,
            filetypes=filetypes
        )
        if selected_file:
            self.location["sub_map"] = os.path.basename(selected_file)
            if not hasattr(self, "sub_map_button"):
                self.sub_map_button = Button(self.window, text="Otwórz mapę lokacji", command=self.open_sub_map_editor)
                self.sub_map_button.pack(pady=5)
            self.save()

    def change_sub_map(self):
        if not messagebox.askyesno("Potwierdzenie", "Zmiana mapy usunie wszystkie sublokacje. Kontynuować?"):
            return
        filetypes = [("Obrazy", "*.png *.jpg *.jpeg *.bmp")]
        selected_file = filedialog.askopenfilename(
            title="Wybierz nową mapę",
            initialdir=self.resources_path,
            filetypes=filetypes
        )
        if selected_file:
            self.location["sub_map"] = os.path.basename(selected_file)
            self.location["locations"] = []
            self.save()
            messagebox.showinfo("Mapa zmieniona", "Mapa została zmieniona i sublokacje usunięte.")

    def open_sub_map_editor(self):
        from MapManager import MapManager
        from TypyLokacji import TypyLokacji

        sub_window = tk.Toplevel(self.window)
        sub_window.title(f"Mapa lokacji: {self.location.get('nazwa', '')}")
        sub_window.geometry("1000x600")

        frame = tk.Frame(sub_window)
        frame.pack()

        sub_context = {
            "data": self.location,
            "file_path": self.save_filename,
            "resources_path": self.resources_path,
            "parent_data": self.save_data
        }

        left_panel = tk.Frame(frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        map_frame = tk.Frame(frame)
        map_frame.pack(side=tk.RIGHT)

        sub_manager = MapManager(map_frame, sub_context, sub_mode=True)
        sub_map_file = os.path.join(self.resources_path, self.location["sub_map"])
        sub_manager.load_map(sub_map_file)

        Button(left_panel, text="Nowa lokacja", command=sub_manager.enable_add_location).pack(pady=5)
        Button(left_panel, text="Typy lokacji", command=lambda: TypyLokacji(sub_window, self.save_data, self.save_filename, self.resources_path).window.lift()).pack(pady=5)

    def save(self):
        self.location["nazwa"] = self.name_var.get()
        self.location["typ"] = self.type_var.get()
        self.location["etykieta"] = self.label_var.get()

        with open(self.save_filename, 'w', encoding='utf-8') as f:
            json.dump(self.save_data, f, ensure_ascii=False, indent=2)
        self.on_close()

    def delete(self):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno usunąć tę lokację?"):
            self.save_data["locations"] = [
                loc for loc in self.save_data["locations"]
                if loc.get("id") != self.location.get("id")
            ]

            with open(self.save_filename, 'w', encoding='utf-8') as f:
                json.dump(self.save_data, f, ensure_ascii=False, indent=2)
            self.window.destroy()
            self.on_close()

    def edit_description(self):
        desc_window = tk.Toplevel(self.window)
        desc_window.title("Opis lokacji")
        desc_window.geometry("500x400")
        desc_window.transient(self.window)
        desc_window.grab_set()

        text_frame = tk.Frame(desc_window)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=text.yview)
        text.pack(fill=tk.BOTH, expand=True)

        # Wczytaj istniejący opis, jeśli jest
        if "opis" in self.location:
            text.insert(tk.END, self.location["opis"])

        def save_desc():
            self.location["opis"] = text.get("1.0", tk.END).strip()
            with open(self.save_filename, 'w', encoding='utf-8') as f:
                json.dump(self.save_data, f, ensure_ascii=False, indent=2)
            desc_window.destroy()

        Button(desc_window, text="Zapisz", command=save_desc).pack(pady=5)

    def open_npc_list(self):
        from LokacjaNpcList import LokacjaNpcList
        from NpcEditor import NpcEditor

        def on_data_updated():
            self.save()

        LokacjaNpcList(
            self.window,
            self.location,
            self.save_data,
            self.save_filename,
            self.resources_path,
            on_data_updated
        )
