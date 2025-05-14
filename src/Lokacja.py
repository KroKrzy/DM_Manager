import os
import json
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, StringVar, OptionMenu, Listbox, filedialog, messagebox
from PIL import Image


class Lokacja:
    def __init__(self, master, location, save_data, save_filename, resources_path, on_close):
        self.location = location
        self.save_data = save_data
        self.save_filename = save_filename
        self.resources_path = resources_path
        self.on_close = on_close

        self.window = Toplevel(master)
        self.window.title("Szczegóły lokacji")
        self.window.geometry("400x500")
        self.window.attributes("-topmost", True)
        self.window.transient(master)
        self.window.grab_set()

        # ID (readonly)
        Label(self.window, text=f"ID: {location['id']}").pack(pady=5)

        # Nazwa
        Label(self.window, text="Nazwa:").pack()
        self.name_var = StringVar(value=location.get("nazwa", ""))
        Entry(self.window, textvariable=self.name_var).pack()

        # Typ
        Label(self.window, text="Typ:").pack()
        all_types = ["domyślna"] + [t["nazwa"] for t in save_data.get("location_types", [])]
        self.type_var = StringVar(value=location.get("typ", "domyślna"))
        OptionMenu(self.window, self.type_var, *all_types).pack()

        # Sub-mapa
        Label(self.window, text="Mapa lokacji (opcjonalnie):").pack(pady=(10, 2))
        Button(self.window, text="Dodaj mapę", command=self.add_sub_map).pack()
        if location.get("sub_map"):
            Button(self.window, text="Otwórz mapę", command=self.open_sub_map).pack(pady=5)

        # NPC list (identyfikatory)
        Label(self.window, text="NPC (ID):").pack(pady=(10, 2))
        self.npc_listbox = Listbox(self.window, height=5)
        self.npc_listbox.pack()
        for npc_id in location.get("npcs", []):
            self.npc_listbox.insert(tk.END, npc_id)

        Button(self.window, text="Otwórz listę NPC", command=self.open_npc_manager).pack(pady=5)

        # Akcje
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

    def open_sub_map(self):
        filename = self.location.get("sub_map")
        if not filename:
            messagebox.showwarning("Brak mapy", "Ta lokacja nie ma przypisanej mapy.")
            return
        path = os.path.join(self.resources_path, filename)
        if not os.path.isfile(path):
            messagebox.showerror("Błąd", f"Nie znaleziono pliku: {filename}")
            return
        try:
            img = Image.open(path)
            img.show()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def open_npc_manager(self):
        messagebox.showinfo("NPC", "Tutaj będzie okno zarządzania NPC (w przyszłości).")

    def save(self):
        self.location["nazwa"] = self.name_var.get()
        self.location["typ"] = self.type_var.get()
        self.location["npcs"] = list(self.npc_listbox.get(0, tk.END))

        with open(self.save_filename, 'w', encoding='utf-8') as f:
            json.dump(self.save_data, f, ensure_ascii=False, indent=2)

        self.window.destroy()
        self.on_close()

    def delete(self):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno usunąć tę lokację?"):
            self.save_data["locations"].remove(self.location)
            with open(self.save_filename, 'w', encoding='utf-8') as f:
                json.dump(self.save_data, f, ensure_ascii=False, indent=2)
            self.window.destroy()
            self.on_close()
