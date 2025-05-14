import os
import json
import uuid
import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Button, filedialog
from PIL import Image, ImageTk
from TypyLokacji import TypyLokacji

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), '..', 'Resources')
SAVES_PATH = os.path.join(os.path.dirname(__file__), '..', 'Saves')

current_data = None
current_file_path = None
image_tk_ref = None
adding_location = False


def load_json_files():
    return [f for f in os.listdir(SAVES_PATH) if f.endswith('.json')]


def refresh_file_list():
    file_listbox.delete(0, tk.END)
    for f in load_json_files():
        file_listbox.insert(tk.END, f)


def open_selected_file():
    selected = file_listbox.curselection()
    if not selected:
        messagebox.showwarning("Uwaga", "Wybierz plik z listy.")
        return
    filename = file_listbox.get(selected[0])
    open_file(filename)


def open_file(filename):
    global current_data, current_file_path
    filepath = os.path.join(SAVES_PATH, filename)
    current_file_path = filepath

    if not os.path.isfile(filepath):
        messagebox.showerror("Błąd", "Plik nie istnieje.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Błąd", "Plik nie jest poprawnym JSON-em.")
            return

    current_data = data

    if 'world_map' not in data:
        data['world_map'] = None
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    if data['world_map']:
        image_path = os.path.join(RESOURCES_PATH, data['world_map'])
        if not os.path.isfile(image_path):
            messagebox.showerror("Błąd", f"Nie znaleziono pliku graficznego: {data['world_map']}")
            return
        show_image(image_path)
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

        show_image(img_file)

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

def show_image(image_path):
    global image_tk_ref
    file_listbox.pack_forget()
    btn_open.pack_forget()
    btn_new.pack_forget()

    img = Image.open(image_path)
    img = img.resize((800, 600))
    image_tk = ImageTk.PhotoImage(img)
    image_tk_ref = image_tk
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)

    canvas.pack(side=tk.RIGHT)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

    canvas.bind("<Button-1>", on_canvas_click)

    if "locations" in current_data:
        for loc in current_data["locations"]:
            draw_location_icon(loc)


def enable_add_location():
    global adding_location
    adding_location = True
    messagebox.showinfo("Dodawanie lokacji", "Kliknij w mapę, aby dodać nową lokację.")


def on_canvas_click(event):
    global adding_location
    if not adding_location:
        return

    adding_location = False

    if "locations" not in current_data:
        current_data["locations"] = []

    x, y = event.x, event.y
    name = simpledialog.askstring("Nowa lokacja", "Podaj nazwę lokacji (opcjonalnie):")

    type_names = [t["nazwa"] for t in current_data.get("location_types", [])]
    selected_type = ask_type_selection(type_names)

    loc_id = str(uuid.uuid4())

    location = {
        "id": loc_id,
        "x": x,
        "y": y,
        "typ": selected_type or "domyślna"
    }
    if name:
        location["nazwa"] = name

    current_data["locations"].append(location)
    with open(current_file_path, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)

    draw_location_icon(location)


def draw_location_icon(location):
    typ = location.get("typ", "domyślna")
    icon_filename = None

    if typ != "domyślna":
        for t in current_data.get("location_types", []):
            if t["nazwa"] == typ:
                icon_filename = t["ikona"]
                break

    x, y = location["x"], location["y"]

    if icon_filename:
        try:
            icon_path = os.path.join(RESOURCES_PATH, icon_filename)
            img = Image.open(icon_path)
            img.thumbnail((32, 32))
            icon = ImageTk.PhotoImage(img)
            item = canvas.create_image(x, y, anchor=tk.CENTER, image=icon)
            if not hasattr(canvas, "icons"):
                canvas.icons = []
            canvas.icons.append(icon)  # keep reference
        except Exception:
            item = canvas.create_rectangle(x-16, y-16, x+16, y+16, fill="white", outline="black")
    else:
        item = canvas.create_rectangle(x-16, y-16, x+16, y+16, fill="white", outline="black")

    canvas.tag_bind(item, "<Button-1>", lambda e, loc=location: on_location_click(loc))


def on_location_click(location):
    messagebox.showinfo(
        "Lokacja",
        f"ID: {location['id']}\n"
        f"Nazwa: {location.get('nazwa', '(brak)')}\n"
        f"Typ: {location['typ']}\n"
        f"Pozycja: ({location['x']}, {location['y']})"
    )


def ask_type_selection(type_names):
    type_window = tk.Toplevel(root)
    type_window.title("Wybierz typ lokacji")
    type_window.geometry("300x200")
    type_window.attributes("-topmost", True)
    type_window.transient(root)

    selected = tk.StringVar(value="domyślna")
    tk.Label(type_window, text="Wybierz typ lokacji:").pack(pady=10)
    listbox = Listbox(type_window, listvariable=tk.StringVar(value=["domyślna"] + type_names), height=6)
    listbox.pack(pady=5)

    result = {"type": None}

    def confirm():
        sel = listbox.curselection()
        if sel:
            result["type"] = listbox.get(sel[0])
        type_window.destroy()

    Button(type_window, text="OK", command=confirm).pack(pady=10)
    type_window.grab_set()
    root.wait_window(type_window)

    return result["type"]


# === GUI ===
root = tk.Tk()
root.title("DM Manager")

file_listbox = Listbox(root, width=50)
file_listbox.pack(pady=10)

btn_open = Button(root, text="Otwórz", command=open_selected_file)
btn_open.pack(pady=5)

btn_new = Button(root, text="Nowy plik", command=create_new_file)
btn_new.pack(pady=5)

main_frame = tk.Frame(root)
main_frame.pack()

left_panel = tk.Frame(main_frame, width=400)
canvas = tk.Canvas(main_frame, width=800, height=600, bg="white")

btn_new_location = Button(left_panel, text="Nowa lokacja", command=enable_add_location)
btn_new_location.pack(pady=5)

btn_types = Button(
    left_panel,
    text="Typy lokacji",
    command=lambda: TypyLokacji(root, current_data, current_file_path, RESOURCES_PATH).window.lift()
)
btn_types.pack(pady=5)

refresh_file_list()
root.mainloop()
