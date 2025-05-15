
import tkinter as tk
from tkinter import Toplevel, Button, messagebox, Scrollbar, Spinbox, Checkbutton, IntVar
from NpcManager import NpcManager

class LokacjaNpcList:
    def __init__(self, master, location, save_data, save_filename, resources_path, on_data_updated):
        self.location = location
        self.save_data = save_data
        self.save_filename = save_filename
        self.resources_path = resources_path
        self.on_data_updated = on_data_updated

        self.window = Toplevel(master)
        self.window.title("Postacie w tej lokacji")
        self.window.geometry("400x500")
        self.window.transient(master)
        self.window.grab_set()

        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True)

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

        self.npc_vars = {}  # npc_id -> IntVar

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        Button(button_frame, text="Dodaj NPC", command=self.add_npc).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Usuń zaznaczonych", command=self.remove_selected_npcs).pack(side=tk.LEFT, padx=5)

        self.refresh()

    def refresh(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.npc_vars.clear()

        npc_ids = self.location.get("npcs", [])
        ilości = self.location.setdefault("npc_ilosci", {})

        for npc_id in npc_ids:
            npc = next((n for n in self.save_data.get("npcs", []) if n["id"] == npc_id), None)
            if not npc:
                continue

            row = tk.Frame(self.scrollable_frame)
            row.pack(fill=tk.X, pady=2, padx=5)

            var = IntVar(value=0)
            self.npc_vars[npc_id] = var
            cb = Checkbutton(row, variable=var)
            cb.pack(side=tk.LEFT)

            name_label = tk.Label(row, text=npc.get("nazwa", "[bezimienny]"), anchor="w")
            name_label.pack(side=tk.LEFT)
            name_label.bind("<Double-Button-1>", lambda e, n=npc: self.open_npc_editor(n))

            qty_var = tk.StringVar()
            qty_var.set(ilości.get(npc_id, "1"))

            def update_qty(var=qty_var, npc_id=npc_id):
                ilości[npc_id] = var.get()
                self.save()
                self.on_data_updated()

            spin = Spinbox(row, from_=1, to=99, width=3, textvariable=qty_var, command=update_qty)
            spin.pack(side=tk.RIGHT, padx=5)
            qty_var.trace_add("write", lambda *args, var=qty_var, npc_id=npc_id: update_qty(var, npc_id))

    def add_npc(self):
        def on_npc_selected(npc):
            if npc["id"] not in self.location.setdefault("npcs", []):
                self.location["npcs"].append(npc["id"])
            if "lokacje" not in npc:
                npc["lokacje"] = []
            if self.location["id"] not in npc["lokacje"]:
                npc["lokacje"].append(self.location["id"])
            self.location.setdefault("npc_ilosci", {})[npc["id"]] = "1"
            self.save()
            self.refresh()
            self.on_data_updated()

        NpcManager(self.window, self.save_data, self.save_filename, on_npc_selected, self.resources_path, assign_mode=True)

    def remove_selected_npcs(self):
        to_remove = [npc_id for npc_id, var in self.npc_vars.items() if var.get() == 1]

        for npc_id in to_remove:
            if npc_id in self.location.get("npcs", []):
                self.location["npcs"].remove(npc_id)

            if "npc_ilosci" in self.location and npc_id in self.location["npc_ilosci"]:
                del self.location["npc_ilosci"][npc_id]

            npc = next((n for n in self.save_data.get("npcs", []) if n["id"] == npc_id), None)
            if npc and "lokacje" in npc and self.location["id"] in npc["lokacje"]:
                npc["lokacje"].remove(self.location["id"])

        self.save()
        self.refresh()
        self.on_data_updated()

    def open_npc_editor(self, npc):
        from NpcEditor import NpcEditor
        NpcEditor(self.window, npc, self.save_data, self.save_filename, self.resources_path)

    def save(self):
        import json
        with open(self.save_filename, "w", encoding="utf-8") as f:
            json.dump(self.save_data, f, ensure_ascii=False, indent=2)
