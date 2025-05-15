
import tkinter as tk
from tkinter import Toplevel, Label, Button, Text, filedialog, messagebox
from PIL import Image, ImageTk
import os
import json
import subprocess
import sys

class NpcEditor:
    def __init__(self, master, npc, save_data, save_filename, resources_path):
        self.npc = npc
        self.save_data = save_data
        self.save_filename = save_filename
        self.resources_path = resources_path

        self.window = Toplevel(master)
        self.window.title(f"NPC: {npc.get('nazwa', '[bezimienny]')}")
        self.window.geometry("800x500")
        self.window.transient(master)
        self.window.grab_set()

        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        Label(left_frame, text="Imię:").pack(anchor="w")
        Label(left_frame, text=npc.get("nazwa", ""), font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,10))

        self.icon_label = Label(left_frame)
        self.icon_label.pack(pady=5)

        self.load_image()

        Button(left_frame, text="Zmień obraz", command=self.change_image).pack(pady=5)
        Button(left_frame, text="Zmień kartę postaci", command=self.set_character_sheet).pack(pady=5)
        Button(left_frame, text="Pokaż kartę postaci", command=self.show_character_sheet).pack(pady=10)

        desc_label = Label(right_frame, text="Opis:")
        desc_label.pack(anchor="w")

        desc_frame = tk.Frame(right_frame)
        desc_frame.pack(fill=tk.BOTH, expand=True)

        desc_scrollbar = tk.Scrollbar(desc_frame)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.desc_text = Text(desc_frame, height=5, wrap=tk.WORD, yscrollcommand=desc_scrollbar.set)
        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.desc_text.insert(tk.END, npc.get("opis", ""))

        desc_scrollbar.config(command=self.desc_text.yview)

        Label(right_frame, text="Ekwipunek:").pack(anchor="w")

        eq_frame = tk.Frame(right_frame)
        eq_frame.pack(fill=tk.BOTH, expand=True)

        eq_scrollbar = tk.Scrollbar(eq_frame)
        eq_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.eq_text = Text(eq_frame, height=5, wrap=tk.WORD, yscrollcommand=eq_scrollbar.set)
        self.eq_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.eq_text.insert(tk.END, npc.get("ekwipunek", ""))

        eq_scrollbar.config(command=self.eq_text.yview)

        Label(self.window, text="Lokalizacje NPC:", font=("Arial", 10, "bold")).pack(pady=(10, 0))

        locations_frame = tk.Frame(self.window)
        locations_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        canvas = tk.Canvas(locations_frame, height=100)
        scrollbar = tk.Scrollbar(locations_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Dodaj etykiety lokalizacji
        Label(self.window, text="Lokalizacje NPC:", font=("Arial", 10, "bold")).pack(pady=(10, 0))

        locations_frame = tk.Frame(self.window)
        locations_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 10))

        canvas = tk.Canvas(locations_frame, height=100)
        scrollbar = tk.Scrollbar(locations_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas)

        # 👇 poprawne przypięcie frame do canvas
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 🔁 Ścieżki z pełnej struktury lokacji
        for path in self.resolve_location_paths():
            tk.Label(scrollable, text=path, wraplength=700, justify="left", fg="gray").pack(anchor="w", padx=5)

        Button(self.window, text="Zapisz", command=self.save).pack(pady=10)

    def load_image(self):
        img_path = os.path.join(self.resources_path, self.npc.get("obraz", ""))
        try:
            img = Image.open(img_path)
        except:
            img = Image.new("RGB", (64, 64), "white")

        img.thumbnail((64, 64))
        self.tk_img = ImageTk.PhotoImage(img)
        self.icon_label.configure(image=self.tk_img)

    def change_image(self):
        filetypes = [("Pliki graficzne", "*.png *.jpg *.jpeg *.bmp")]
        selected = filedialog.askopenfilename(
            title="Wybierz obraz",
            initialdir=self.resources_path,
            filetypes=filetypes
        )
        if selected:
            self.npc["obraz"] = os.path.basename(selected)
            self.load_image()

    def set_character_sheet(self):
        filetypes = [("Pliki graficzne i PDF", "*.png *.jpg *.jpeg *.bmp *.pdf")]
        selected = filedialog.askopenfilename(
            title="Wybierz kartę postaci",
            initialdir=self.resources_path,
            filetypes=filetypes
        )
        if selected:
            self.npc["karta"] = os.path.basename(selected)
            messagebox.showinfo("Zapisano", f"Karta postaci ustawiona: {self.npc['karta']}")

    def show_character_sheet(self):
        filename = self.npc.get("karta")
        if not filename:
            messagebox.showinfo("Brak", "Brak przypisanej karty postaci.")
            return

        filepath = os.path.join(self.resources_path, filename)
        if not os.path.exists(filepath):
            messagebox.showerror("Błąd", f"Nie znaleziono pliku: {filename}")
            return

        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            win = Toplevel(self.window)
            win.title("Karta postaci")
            img = Image.open(filepath)
            img.thumbnail((700, 800))
            self.card_img = ImageTk.PhotoImage(img)
            lbl = Label(win, image=self.card_img)
            lbl.pack()
        elif filename.lower().endswith(".pdf"):
            try:
                if sys.platform == "win32":
                    os.startfile(filepath)
                elif sys.platform == "darwin":
                    subprocess.call(["open", filepath])
                else:
                    subprocess.call(["xdg-open", filepath])
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się otworzyć pliku PDF:\n{e}")

    def resolve_location_paths(self):
        npc_id = self.npc.get("id")
        result = []

        def recurse(locations, path):
            for loc in locations:
                name = loc.get("nazwa", "[brak nazwy]")
                new_path = path + [name]

                if npc_id in loc.get("npcs", []):
                    result.append("/".join(new_path))

                recurse(loc.get("locations", []), new_path)

        all_top_locations = self.save_data.get("locations", [])
        recurse(all_top_locations, [])

        return result

    def save(self):
        self.npc["opis"] = self.desc_text.get("1.0", tk.END).strip()
        self.npc["ekwipunek"] = self.eq_text.get("1.0", tk.END).strip()

        with open(self.save_filename, "w", encoding="utf-8") as f:
            json.dump(self.save_data, f, ensure_ascii=False, indent=2)

        self.window.destroy()
