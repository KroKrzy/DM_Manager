
import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Button, filedialog
from TypyLokacji import TypyLokacji
from MapManager import MapManager
from NpcManager import NpcManager

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), '..', 'Resources')
SAVES_PATH = os.path.join(os.path.dirname(__file__), '..', 'Saves')

app_context = {
    "data": None,
    "file_path": None,
    "resources_path": RESOURCES_PATH
}

def load_json_files():
    return [os.path.splitext(f)[0] for f in os.listdir(SAVES_PATH) if f.endswith('.json')]


def refresh_file_list():
    file_listbox.delete(0, tk.END)
    for f in load_json_files():
        file_listbox.insert(tk.END, f)

def create_new_file():
    filename = simpledialog.askstring("Nowy plik", "Podaj nazwę pliku (bez rozszerzenia):")
    if not filename:
        return
    if not filename.endswith('.json'):
        filename += '.json'

    filepath = os.path.join(SAVES_PATH, filename)
    if os.path.exists(filepath):
        messagebox.showerror("Błąd", "Plik już istnieje.")
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

    messagebox.showinfo("Sukces", f"Utworzono plik: {filename}")
    refresh_file_list()

def open_selected_file():
    selected = file_listbox.curselection()
    if not selected:
        messagebox.showwarning("Uwaga", "Wybierz plik z listy.")
        return
    filename = file_listbox.get(selected[0])
    open_file(filename)

def open_file(filename):
    filepath = os.path.join(SAVES_PATH, filename + ".json")
    app_context["file_path"] = filepath

    if not os.path.isfile(filepath):
        messagebox.showerror("Błąd", "Plik nie istnieje.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Błąd", "Plik nie jest poprawnym JSON-em.")
            return

    app_context["data"] = data

    if 'world_map' not in data:
        data['world_map'] = None
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    if data['world_map']:
        image_path = os.path.join(RESOURCES_PATH, data['world_map'])
        if not os.path.isfile(image_path):
            messagebox.showerror("Błąd", f"Nie znaleziono pliku graficznego: {data['world_map']}")
            return
        show_map(image_path)
    else:
        filetypes = [("Pliki graficzne", "*.png *.jpg *.jpeg *.bmp")]
        img_file = filedialog.askopenfilename(
            title="Wybierz plik graficzny",
            initialdir=RESOURCES_PATH,
            filetypes=filetypes
        )
        if not img_file:
            return

        selected_filename = os.path.basename(img_file)
        data['world_map'] = selected_filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        show_map(img_file)

def on_root_close():
    root.destroy()
    os._exit(0)  # wymuszone zamknięcie nawet jeśli inne okna istnieją


def show_map(image_path):
    root.geometry("1000x600")
    file_listbox.pack_forget()
    btn_open.pack_forget()
    btn_new.pack_forget()
    map_manager.load_map(image_path)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

# === GUI ===
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_root_close)

root.title("DM Manager")
root.geometry("400x300")

file_listbox = Listbox(root, width=50)
file_listbox.pack(pady=10)

btn_open = Button(root, text="Otwórz", command=open_selected_file)
btn_open.pack(pady=5)

btn_new = Button(root, text="Nowy plik", command=create_new_file)
btn_new.pack(pady=5)

main_frame = tk.Frame(root)
main_frame.pack()

left_panel = tk.Frame(main_frame, width=400)
map_manager = MapManager(main_frame, app_context)

btn_new_location = Button(left_panel, text="Nowa lokacja", command=lambda: map_manager.enable_add_location())
btn_new_location.pack(pady=5)

btn_types = Button(
    left_panel,
    text="Typy lokacji",
    command=lambda: TypyLokacji(root, app_context["data"], app_context["file_path"], RESOURCES_PATH).window.lift()
)
btn_types.pack(pady=5)

btn_npc = Button(
    left_panel,
    text="Zarządzaj NPC",
    command=lambda: NpcManager(root, app_context["data"], app_context["file_path"], None, RESOURCES_PATH, assign_mode=False)

)
btn_npc.pack(pady=5)

refresh_file_list()
root.mainloop()
