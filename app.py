import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, scrolledtext, END
import numpy as np
import os
import json

# Pfad zur Einstellungsdatei config.json im gleichen Ordner wie dieses Script
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_theme_preference():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('theme', 'darkly')
        except:
            pass
    return 'darkly'

def save_theme_preference(theme_name):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'theme': theme_name}, f)
    except:
        pass

# --- Berechnungsfunktionen (unverändert) ---
def get_neighbors(index, rows, cols):
    row = index // cols
    col = index % cols
    neighbors = [index]
    if row - 1 >= 0:
        neighbors.append(index - cols)
    if row + 1 < rows:
        neighbors.append(index + cols)
    if col - 1 >= 0:
        neighbors.append(index - 1)
    if col + 1 < cols:
        neighbors.append(index + 1)
    return neighbors


def build_matrix(rows, cols):
    size = rows * cols
    A = np.zeros((size, size), dtype=int)
    for j in range(size):
        for i in get_neighbors(j, rows, cols):
            A[i, j] = 1
    return A


def gaussian_elimination_mod2(A, b):
    A = A.copy() % 2
    b = b.copy() % 2
    m, n = A.shape
    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, m):
            if A[r, col] == 1:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            A[[row, pivot]] = A[[pivot, row]]
            b[row], b[pivot] = b[pivot], b[row]
        for r in range(m):
            if r != row and A[r, col] == 1:
                A[r] = (A[r] + A[row]) % 2
                b[r] = (b[r] + b[row]) % 2
        row += 1
        if row == m:
            break
    for r in range(m):
        if np.all(A[r] == 0) and b[r] == 1:
            return None
    x = np.zeros(n, dtype=int)
    for r in range(m - 1, -1, -1):
        nz = np.nonzero(A[r])[0]
        if nz.size == 0:
            continue
        pivot_col = nz[0]
        s = sum(A[r, j] * x[j] for j in nz[1:]) % 2
        x[pivot_col] = (b[r] - s) % 2
    return x


def solve_lights_out(initial_state, rows, cols):
    state = np.array(initial_state, dtype=int) % 2
    size = rows * cols
    goal = np.ones(size, dtype=int)
    A = build_matrix(rows, cols)
    b = (goal + state) % 2
    return gaussian_elimination_mod2(A, b)


def matrix_to_string(state, rows, cols):
    matrix = np.array(state, dtype=int).reshape(rows, cols)
    return "\n".join(" ".join(str(x) for x in row) for row in matrix)


def apply_move(state, move, rows, cols):
    new_state = state.copy()
    for idx in get_neighbors(move, rows, cols):
        new_state[idx] = (new_state[idx] + 1) % 2
    return new_state


def simulate_solution(initial_state, moves, rows, cols):
    current = initial_state.copy()
    output = ""
    step = 1
    for move in moves:
        current = apply_move(current, move, rows, cols)
        r, c = divmod(move, cols)
        output += f"\nSchritt {step}: Drücke Zelle (Zeile {r+1}, Spalte {c+1})\n"
        output += matrix_to_string(current, rows, cols) + "\n"
        step += 1
    return output

# --- GUI mit ttkbootstrap ---
def solve_button_clicked():
    try:
        rows = int(entry_rows.get())
        cols = int(entry_cols.get())
    except ValueError:
        messagebox.showerror("Fehler", "Zeilen und Spalten müssen ganze Zahlen sein!")
        return
    state_str = entry_state.get().strip()
    size = rows * cols
    if len(state_str) != size or any(ch not in "01" for ch in state_str):
        messagebox.showerror("Fehler", f"Der Zustand muss genau {size} Zeichen (0 oder 1) enthalten!")
        return
    state = [int(ch) for ch in state_str]
    solution = solve_lights_out(state, rows, cols)
    if solution is None:
        result = "Keine Lösung gefunden!"
    else:
        moves = [i for i, v in enumerate(solution) if v == 1]
        if not moves:
            result = "Startzustand entspricht Ziel (alle Zellen = 1)."
        else:
            result = "Lösungsschritte (Zeile, Spalte):\n"
            for m in moves:
                r, c = divmod(m, cols)
                result += f"Drücke Zelle {m+1} -> (Zeile {r+1}, Spalte {c+1})\n"
            result += "\nSimulation der Lösungsschritte:\n"
            result += matrix_to_string(state, rows, cols) + "\n"
            result += simulate_solution(state, moves, rows, cols)
            result += "\nGesamtlösung: " + str([m+1 for m in moves])
    text_output.config(state="normal")
    text_output.delete("1.0", END)
    text_output.insert(END, result)
    text_output.config(state="disabled")


def reset_button_clicked():
    entry_rows.delete(0, END)
    entry_cols.delete(0, END)
    entry_state.delete(0, END)
    text_output.config(state="normal")
    text_output.delete("1.0", END)
    text_output.config(state="disabled")

# Hauptfenster initialisieren
root = ttk.Window(themename="darkly")
style = ttk.Style()

# Lade letzte Theme‑Einstellung (oder 'darkly' als Fallback)
current = load_theme_preference()
style.theme_use(current)
root.config(bg=style.colors.bg)

# Themes aus JSON laden (nur einmal beim Start)

root.title("Lights Out Solver")
root.geometry("750x600")

# ── Theme‑Toggle zwischen Dark und Pink ──
def set_dark_mode():
    style.theme_use('darkly')
    root.config(bg=style.colors.bg)
    save_theme_preference('darkly')

def set_pink_mode():
    style.theme_use('girly')       # wechselt auf Dein eigenes Girly‑Theme
    root.config(bg=style.colors.bg)  # Fenster‑Hintergrund ans neue Theme anpassen
    save_theme_preference('girly')

# Menü (optional)
menubar = ttk.Menu(root)
file_menu = ttk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Beenden", command=root.quit)
menubar.add_cascade(label="Datei", menu=file_menu)
help_menu = ttk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Über", command=lambda: messagebox.showinfo("Über", "Lights Out Solver v1.0"))
menubar.add_cascade(label="Hilfe", menu=help_menu)
root.config(menu=menubar)

# Frames definieren
frame_input = ttk.Frame(root)
frame_input.pack(padx=10, pady=10, anchor="w")

frame_buttons = ttk.Frame(root)
frame_buttons.pack(padx=10, pady=10, anchor="w")

frame_output = ttk.Frame(root)
frame_output.pack(padx=10, pady=10)

# Farbmodus‑Buttons
button_dark = ttk.Button(frame_buttons, text="Dark Mode", bootstyle=SECONDARY, command=set_dark_mode)
button_dark.grid(row=0, column=0, padx=5, pady=5)
button_pink = ttk.Button(frame_buttons, text="Pink Mode", bootstyle=SECONDARY, command=set_pink_mode)
button_pink.grid(row=0, column=1, padx=5, pady=5)

# Solve & Reset-Buttons
button_solve = ttk.Button(frame_buttons, text="Berechne Lösung", bootstyle=PRIMARY, command=solve_button_clicked)
button_solve.grid(row=0, column=2, padx=10, pady=10)
button_reset = ttk.Button(frame_buttons, text="Reset", bootstyle=SECONDARY, command=reset_button_clicked)
button_reset.grid(row=0, column=3, padx=10, pady=10)

# Eingabefelder
label_rows = ttk.Label(frame_input, text="Anzahl der Zeilen (n):", font=("Helvetica", 12))
label_rows.grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_rows = ttk.Entry(frame_input, width=10, font=("Helvetica", 12))
entry_rows.grid(row=0, column=1, padx=5, pady=5)

label_cols = ttk.Label(frame_input, text="Anzahl der Spalten (m):", font=("Helvetica", 12))
label_cols.grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_cols = ttk.Entry(frame_input, width=10, font=("Helvetica", 12))
entry_cols.grid(row=1, column=1, padx=5, pady=5)

label_state = ttk.Label(frame_input, text="Zustand (n*m Zeichen, 0 oder 1):", font=("Helvetica", 12))
label_state.grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_state = ttk.Entry(frame_input, width=50, font=("Helvetica", 12))
entry_state.grid(row=2, column=1, padx=5, pady=5)

# Ausgabefeld
text_output = scrolledtext.ScrolledText(frame_output, width=80, height=20, font=("Courier", 11), state="disabled", bg="#343a40", fg="white", insertbackground="white")
text_output.pack(padx=10, pady=10)

root.mainloop()