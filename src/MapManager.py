
import os
import uuid
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from Lokacja import Lokacja

class MapManager:
    def __init__(self, master_frame, app_context, sub_mode=False):
        self.app_context = app_context
        self.sub_mode = sub_mode
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

        data = self.app_context["data"]
        if "locations" in data:
            for loc in data["locations"]:
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

        type_names = [t["nazwa"] for t in self.get_all_types()]
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

        for t in self.get_all_types():
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
        if location.get("etykieta") and location.get("nazwa"):
            label_text = location["nazwa"]
            text_id = self.canvas.create_text(
                x, y - 28,
                text=label_text,
                fill="white",
                font=("Arial", 9, "bold"),
                anchor="n"
            )

            bbox = self.canvas.bbox(text_id)
            if bbox:
                x0, y0, x1, y1 = bbox
                padding = 4
                rect_id = self.canvas.create_rectangle(
                    x0 - padding, y0 - padding, x1 + padding, y1 + padding,
                    fill="black", outline=""
                )
                self.canvas.tag_raise(text_id, rect_id)

        self.canvas.tag_bind(item, "<Button-1>", lambda e, loc=location: self.on_location_click(loc))

    def on_location_click(self, location):
        Lokacja(
            self.canvas,
            location,
            self.app_context.get("parent_data") or self.app_context["data"],
            self.app_context["file_path"],
            self.app_context["resources_path"],
            self.refresh
        )

    def refresh(self):
        map_key = "sub_map" if self.sub_mode else "world_map"
        map_file = os.path.join(self.app_context["resources_path"], self.app_context["data"][map_key])
        self.load_map(map_file)

    def save(self):
        if self.sub_mode:
            parent_data = self.app_context["parent_data"]
            loc = self.app_context["data"]
            for l in parent_data["locations"]:
                if l["id"] == loc["id"]:
                    l["locations"] = loc.get("locations", [])
                    break
            with open(self.app_context["file_path"], 'w', encoding='utf-8') as f:
                json.dump(parent_data, f, ensure_ascii=False, indent=2)
        else:
            with open(self.app_context["file_path"], 'w', encoding='utf-8') as f:
                json.dump(self.app_context["data"], f, ensure_ascii=False, indent=2)

    def get_all_types(self):
        if self.sub_mode:
            return self.app_context["parent_data"].get("location_types", [])
        else:
            return self.app_context["data"].get("location_types", [])

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
