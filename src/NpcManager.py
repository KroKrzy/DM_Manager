
import tkinter as tk
import os
from tkinter import Toplevel, Button, simpledialog, messagebox, Scrollbar
from PIL import Image, ImageTk

class NpcManager:
    def __init__(self, master, save_data, save_filename, on_npc_selected=None, resources_path="", assign_mode=False):
        self.save_data = save_data
        self.save_filename = save_filename
        self.on_npc_selected = on_npc_selected
        self.resources_path = resources_path
        self.assign_mode = assign_mode
        self.selected_npc_id = None

        self.window = Toplevel(master)
        self.window.title("Zarządzanie NPC")
        self.window.geometry("400x500")
        self.window.transient(master)
        self.window.grab_set()

        if "npcs" not in self.save_data:
            self.save_data["npcs"] = []

        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(frame)
        self.scrollbar = Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.icon_refs = {}

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)

        Button(button_frame, text="Dodaj nową postać", command=self.add_npc).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Usuń postać", command=self.delete_npc).pack(side=tk.LEFT, padx=5)

        self.refresh_list()

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.icon_refs.clear()

        for npc in self.save_data.get("npcs", []):
            row = tk.Frame(self.scrollable_frame)
            row.pack(fill=tk.X, pady=2, padx=5)

            icon_label = tk.Label(row)
            icon_label.pack(side=tk.LEFT, padx=(5, 10))

            icon = None
            icon_path = npc.get("obraz")
            if icon_path:
                full_path = os.path.join(self.resources_path, icon_path)
                if os.path.isfile(full_path):
                    try:
                        img = Image.open(full_path)
                        img = img.resize((20, 20), Image.LANCZOS)
                        icon = ImageTk.PhotoImage(img)
                    except Exception:
                        pass
            if not icon:
                img = Image.new("RGB", (20, 20), color="white")
                icon = ImageTk.PhotoImage(img)

            icon_label.configure(image=icon)
            icon_label.image = icon
            self.icon_refs[npc["id"]] = icon

            name_label = tk.Label(row, text=npc.get("nazwa", "[bezimienny]"), anchor="w")
            name_label.pack(side=tk.LEFT, expand=True)
            name_label.bind("<Double-Button-1>", lambda e, n=npc: self.handle_npc_click_object(n))

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
        npc_id = self.selected_npc_id
        if not npc_id:
            messagebox.showinfo("Brak wyboru", "Kliknij najpierw postać.")
            return

        npc = next((n for n in self.save_data["npcs"] if n["id"] == npc_id), None)
        if not npc:
            return

        if not messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć NPC '{npc.get('nazwa', '')}'?"):
            return

        # Usuń NPC z każdej lokacji, do której był przypisany
        for location in self.save_data.get("locations", []):
            if "npcs" in location and npc_id in location["npcs"]:
                location["npcs"].remove(npc_id)
            if "npc_ilosci" in location and npc_id in location["npc_ilosci"]:
                del location["npc_ilosci"][npc_id]

        self.save_data["npcs"] = [n for n in self.save_data["npcs"] if n["id"] != npc_id]
        self.save()
        self.refresh_list()

    def handle_npc_click_object(self, npc):
        self.selected_npc_id = npc["id"]
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
