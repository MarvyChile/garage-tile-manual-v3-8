import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="centered")
st.title("Garage Tile Designer Final v3.13 - Clickable Grid con botones")

# 1. Unidad y medidas
unidad = st.selectbox(
    "Selecciona la unidad de medida", ["metros", "centímetros"], key="unidad"
)
factor = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0
ancho_input = st.number_input(
    f"Ancho del espacio ({unidad})", min_value=min_val,
    value=4.0 if unidad == "metros" else 400.0, step=1.0
)
largo_input = st.number_input(
    f"Largo del espacio ({unidad})", min_value=min_val,
    value=6.0 if unidad == "metros" else 600.0, step=1.0
)
ancho_m = ancho_input * factor
largo_m = largo_input * factor
area_m2 = round(ancho_m * largo_m, 2)
st.markdown(f"**Área total:** {area_m2} m²")

# 2. Bordillos y esquineros
incluir_bordillos = st.checkbox("Agregar bordillos", value=True)
incluir_esquineros = st.checkbox("Agregar esquineros", value=True)
pos_bord = st.multiselect(
    "¿Dónde colocar bordillos?",
    ["Arriba", "Abajo", "Izquierda", "Derecha"],
    default=["Arriba", "Abajo", "Izquierda", "Derecha"]
)

# 3. Colores y base
colores = {
    "Blanco": "#FFFFFF", "Negro": "#000000", "Gris": "#B0B0B0", "Gris Oscuro": "#4F4F4F",
    "Azul": "#0070C0", "Celeste": "#00B0F0", "Amarillo": "#FFFF00", "Verde": "#00B050", "Rojo": "#FF0000"
}
lista_colores = list(colores.keys())
color_base = st.selectbox(
    "Color base", lista_colores, index=lista_colores.index("Blanco")
)

# 4. Inicializar o actualizar DataFrame
cols = math.ceil(ancho_m / 0.4)
rows = math.ceil(largo_m / 0.4)

def init_df():
    # Crear un DataFrame con color base en todas las celdas
    return pd.DataFrame([[color_base] * cols for _ in range(rows)])

# Inicializar en session_state si no existe o cambia tamaño\ n
if 'df' not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = init_df()
df = st.session_state.df

# 5. Botón aplicar color base
if st.button("Aplicar color base"):
    st.session_state.df = init_df()
    df = st.session_state.df

# 6. Diseño personalizado con botones
st.subheader("Diseño personalizado: haz clic en cada celda")
for r in range(rows):
    row_cols = st.columns(cols)
    for c, col_ui in enumerate(row_cols):
        cell_color = df.iat[r, c]
        hexcol = colores[cell_color]
        # Botón invisible para clic\ n
        if col_ui.button("", key=f"btn_{r}_{c}"):
            st.session_state.df.iat[r, c] = color_base
            df = st.session_state.df
        # Mostrar celda coloreada
        col_ui.markdown(
            f"""
            <div style='width:30px; height:30px; background:{hexcol}; border:1px solid {'white' if color_base == 'Negro' else 'black'}; margin-top:-30px;'></div>
            """,
            unsafe_allow_html=True
        )

# 7. Renderizado final con Matplotlib
fig, ax = plt.subplots(figsize=(cols / 5, rows / 5))
for y in range(rows):
    for x in range(cols):
        color = colores.get(st.session_state.df.iat[y, x], "#FFFFFF")
        edge = 'white' if color_base == 'Negro' else 'black'
        ax.add_patch(plt.Rectangle((x, rows - 1 - y), 1, 1, facecolor=color, edgecolor=edge))

# Bordillos y esquineros
if incluir_bordillos:
    if "Arriba" in pos_bord:
        ax.add_patch(plt.Rectangle((0, rows), cols, 0.15, facecolor="black"))
    if "Abajo" in pos_bord:
        ax.add_patch(plt.Rectangle((0, -0.15), cols, 0.15, facecolor="black"))
    if "Izquierda" in pos_bord:
        ax.add_patch(plt.Rectangle((-0.15, 0), 0.15, rows, facecolor="black"))
    if "Derecha" in pos_bord:
        ax.add_patch(plt.Rectangle((cols, 0), 0.15, rows, facecolor="black"))

if incluir_esquineros:
    s = 0.15
    for (x, y) in [(0, 0), (0, rows), (cols, 0), (cols, rows)]:
        ax.add_patch(plt.Rectangle((x - s/2, y - s/2), s, s, facecolor="black"))

ax.set_xlim(-0.5, cols + 0.5)
ax.set_ylim(-0.5, rows + 0.5)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)
