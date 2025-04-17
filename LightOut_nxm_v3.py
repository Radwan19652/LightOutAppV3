# app.py
import streamlit as st
import numpy as np

# ── Solver‑Funktionen kopiert ──
def get_neighbors(index, rows, cols):
    row = index // cols
    col = index % cols
    neighbors = [index]
    if row - 1 >= 0:        neighbors.append(index - cols)
    if row + 1 < rows:     neighbors.append(index + cols)
    if col - 1 >= 0:        neighbors.append(index - 1)
    if col + 1 < cols:     neighbors.append(index + 1)
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
    mat = np.array(state, dtype=int).reshape(rows, cols)
    return "\n".join(" ".join(str(x) for x in row) for row in mat)

def apply_move(state, move, rows, cols):
    new = state.copy()
    for idx in get_neighbors(move, rows, cols):
        new[idx] = (new[idx] + 1) % 2
    return new

def simulate_solution(initial_state, moves, rows, cols):
    cur = initial_state.copy()
    out = ""
    step = 1
    for move in moves:
        cur = apply_move(cur, move, rows, cols)
        r, c = divmod(move, cols)
        out += f"\nSchritt {step}: Drücke Zelle (Zeile {r+1}, Spalte {c+1})\n"
        out += matrix_to_string(cur, rows, cols) + "\n"
        step += 1
    return out

# ── Streamlit‑UI ──
st.set_page_config(
    page_title="Lights Out Solver",
    page_icon="🕹",
    layout="centered"
)

st.title("Lights Out Solver (Web‑Version)")
st.markdown("Gib die Größe und den Zustand (0/1) deiner Matrix ein:")

# Eingabe
rows = st.number_input("Zeilen (n)", min_value=1, max_value=8, value=3)
cols = st.number_input("Spalten (m)", min_value=1, max_value=8, value=3)
state_str = st.text_input(
    f"Zustand als {rows*cols} Zeichen (0/1)", 
    value="0"*(rows*cols)
)

# Berechnung
if st.button("Lösung berechnen"):
    try:
        initial = [int(c) for c in state_str.strip()]
        solution = solve_lights_out(initial, rows, cols)
    except:
        st.error("Ungültige Eingabe – nur 0 und 1 erlaubt!")
    else:
        if solution is None:
            st.error("Keine Lösung gefunden!")
        else:
            moves = [i+1 for i,v in enumerate(solution) if v]
            st.success(f"Gesamtlösung (1‑indexiert): {moves}")

            st.subheader("Startmatrix")
            st.code(matrix_to_string(initial, rows, cols), language=None)

            st.subheader("Schritt‑für‑Schritt")
            st.code(simulate_solution(initial, [m-1 for m in moves], rows, cols), language=None)
