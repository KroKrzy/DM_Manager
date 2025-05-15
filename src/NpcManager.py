
import tkinter as tk
from tkinter import Toplevel, Listbox, Button, simpledialog, messagebox

class NpcManager:
    def __init__(self, master, save_data, save_filename, on_npc_selected=None, resources_path="", assign_mode=False):
        self.save_data = save_data
        self.save_filename = save_filename
        self.on_npc_selected = on_npc_selected

        self.window = Toplevel(master)
        self.window.title("Zarządzanie NPC")
        self.window.geometry("400x500")
        self.window.transient(master)
        self.window.grab_set()
        self.resources_path = resources_path

        self.assign_mode = assign_mode

        if "npcs" not in self.save_data:
            self.save_data["npcs"] = []

        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = Listbox(frame, yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.listbox.bind("<Double-Button-1>", self.handle_npc_click)

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)

        Button(button_frame, text="Dodaj nową postać", command=self.add_npc).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Usuń postać", command=self.delete_npc).pack(side=tk.LEFT, padx=5)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for npc in self.save_data["npcs"]:
            self.listbox.insert(tk.END, npc.get("nazwa", "[bezimienny]"))

    def add_npc(self):
        from uuid import uuid4
        name = simpledialog.askstring("Nowa postać", "Podaj imię NPC:")
        if not name:
            return

        npc = {
            "id": str(uuid4()),
            "nazwa": name,
            "lokacje": [],
            "opis": "",
            "obraz": "",
            "ekwipunek": ""
        }
        self.save_data["npcs"].append(npc)
        self.save()
        self.refresh_list()

    def delete_npc(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Brak wyboru", "Najpierw wybierz postać do usunięcia.")
            return

        index = selection[0]
        npc = self.save_data["npcs"][index]
        if not messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć NPC '{npc['nazwa']}'?"):
            return

        npc_id = npc["id"]

        # Usuń NPC z każdej lokacji, do której był przypisany
        for location in self.save_data.get("locations", []):
            if "npcs" in location and npc_id in location["npcs"]:
                location["npcs"].remove(npc_id)
            if "npc_ilosci" in location and npc_id in location["npc_ilosci"]:
                del location["npc_ilosci"][npc_id]

        # Usuń NPC z głównej listy
        del self.save_data["npcs"][index]

        self.save()
        self.refresh_list()

    def handle_npc_click(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        npc = self.save_data["npcs"][index]

        if self.assign_mode:
            self.on_npc_selected(npc)
            self.window.destroy()
        else:
            from NpcEditor import NpcEditor
            NpcEditor(self.window, npc, self.save_data, self.save_filename, self.resources_path)

    def save(self):
        import json
        with open(self.save_filename, "w", encoding="utf-8") as f:
            json.dump(self.save_data, f, ensure_ascii=False, indent=2)
