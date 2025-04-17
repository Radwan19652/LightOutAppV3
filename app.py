import streamlit as st
import numpy as np

from LightOut_nxm_v3 import get_neighbors, solve_lights_out  # falls du sie in einem separaten Modul belässt

# ── Theme‑Switcher mit Danger‑Buttons ──
theme = st.selectbox("Farbschema wählen:", ["Darkly", "Girly"])

if theme == "Darkly":
    # Darkly‑Palette
    background    = "#222222"
    secondary_bg  = "#444444"
    primary_color = "#e74c3c"   # Danger‑Farbe für Darkly
    text_color    = "#ffffff"
else:
    # Girly‑Palette
    background    = "#ffbbff"
    secondary_bg  = "#ff24ff"
    primary_color = "#e91e63"   # Normale Girly‑Primärfarbe
    text_color    = "#ff0080"

st.markdown(f"""
    <style>
      .reportview-container .main {{ background-color: {background}; }}
      .sidebar .sidebar-content {{ background-color: {secondary_bg}; }}
      /* alle Buttons auf primary_color */
      .stButton>button {{
          background-color: {primary_color} !important;
          color: {text_color} !important;
          border: none;
      }}
      /* Texte und Inputs */
      .stTextInput>div>div>input, .markdown-text-container {{
          color: {text_color};
      }}
    </style>
""", unsafe_allow_html=True)

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
