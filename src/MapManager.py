
import os
import uuid
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from Lokacja import Lokacja

class MapManager:
    def __init__(self, master_frame, app_context):
        self.app_context = app_context
        self.canvas = tk.Canvas(master_frame, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.RIGHT)
        self.image_tk = None
        self.icons = []
        self.adding_location = False

    def load_map(self, image_path):
        self.canvas.delete("all")
        self.icons.clear()

        try:
            img = Image.open(image_path)
            img = img.resize((800, 600))
            self.image_tk = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można załadować mapy: {e}")
            return

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Rysuj lokacje
        if "locations" in self.app_context["data"]:
            for loc in self.app_context["data"]["locations"]:
                self.draw_location_icon(loc)

    def enable_add_location(self):
        self.adding_location = True
        messagebox.showinfo("Dodawanie lokacji", "Kliknij w mapę, aby dodać nową lokację.")

    def on_canvas_click(self, event):
        if not self.adding_location:
            return
        self.adding_location = False

        data = self.app_context["data"]
        if "locations" not in data:
            data["locations"] = []

        x, y = event.x, event.y
        name = simpledialog.askstring("Nowa lokacja", "Podaj nazwę lokacji (opcjonalnie):")

        type_names = [t["nazwa"] for t in data.get("location_types", [])]
        selected_type = self.ask_type_selection(type_names)

        loc_id = str(uuid.uuid4())
        location = {
            "id": loc_id,
            "x": x,
            "y": y,
            "typ": selected_type or "domyślna"
        }
        if name:
            location["nazwa"] = name

        data["locations"].append(location)
        self.save()
        self.draw_location_icon(location)

    def draw_location_icon(self, location):
        typ = location.get("typ", "domyślna")
        icon_filename = None

        for t in self.app_context["data"].get("location_types", []):
            if t["nazwa"] == typ:
                icon_filename = t["ikona"]
                break

        x, y = location["x"], location["y"]

        if icon_filename:
            try:
                icon_path = os.path.join(self.app_context["resources_path"], icon_filename)
                img = Image.open(icon_path)
                img.thumbnail((32, 32))
                icon = ImageTk.PhotoImage(img)
                item = self.canvas.create_image(x, y, anchor=tk.CENTER, image=icon)
                self.icons.append(icon)
            except:
                item = self.canvas.create_rectangle(x-16, y-16, x+16, y+16, fill="white", outline="black")
        else:
            item = self.canvas.create_rectangle(x-16, y-16, x+16, y+16, fill="white", outline="black")

        self.canvas.tag_bind(item, "<Button-1>", lambda e, loc=location: self.on_location_click(loc))

    def on_location_click(self, location):
        Lokacja(self.canvas, location, self.app_context["data"], self.app_context["file_path"], self.app_context["resources_path"], self.refresh)

    def refresh(self):
        map_file = os.path.join(self.app_context["resources_path"], self.app_context["data"]["world_map"])
        self.load_map(map_file)

    def save(self):
        with open(self.app_context["file_path"], 'w', encoding='utf-8') as f:
            json.dump(self.app_context["data"], f, ensure_ascii=False, indent=2)

    def ask_type_selection(self, type_names):
        type_window = tk.Toplevel(self.canvas)
        type_window.title("Wybierz typ lokacji")
        type_window.geometry("300x200")
        type_window.attributes("-topmost", True)
        type_window.transient(self.canvas)

        selected = tk.StringVar(value="domyślna")
        tk.Label(type_window, text="Wybierz typ lokacji:").pack(pady=10)
        listbox = tk.Listbox(type_window, listvariable=tk.StringVar(value=["domyślna"] + type_names), height=6)
        listbox.pack(pady=5)

        result = {"type": None}
        def confirm():
            sel = listbox.curselection()
            if sel:
                result["type"] = listbox.get(sel[0])
            type_window.destroy()

        tk.Button(type_window, text="OK", command=confirm).pack(pady=10)
        type_window.grab_set()
        self.canvas.wait_window(type_window)

        return result["type"]
