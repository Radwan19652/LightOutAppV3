import streamlit as st
import numpy as np


from LightOut_nxm_v3 import get_neighbors, solve_lights_out  # falls du sie in einem separaten Modul belässt

st.title("Lights Out Solver (Web‐Version)")

rows = st.number_input("Anzahl der Zeilen (n)", min_value=1, max_value=10, value=3)
cols = st.number_input("Anzahl der Spalten (m)", min_value=1, max_value=10, value=3)
state_str = st.text_input(f"Zustand als {rows*cols} Zeichen (0/1)", "0" * (rows*cols))

if st.button("Lösung berechnen"):
    initial = [int(c) for c in state_str.strip()]
    solution = solve_lights_out(initial, rows, cols)
    if solution is None:
        st.error("Keine Lösung gefunden!")
    else:
        moves = [i+1 for i,v in enumerate(solution) if v]
        st.success(f"Gesamtlösung (1‑indexiert): {moves}")
