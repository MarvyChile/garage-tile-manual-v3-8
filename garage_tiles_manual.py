
import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.set_page_config(layout="centered")
st.title("Garage Tile Designer v3.12 - Clickable Plotly Grid")

# 1. Unidad y medidas
unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"], key="unidad")
factor = 1 if unidad == "metros" else 0.01
min_val = 1.0 if unidad == "metros" else 10.0
ancho_input = st.number_input(f"Ancho del espacio ({unidad})", min_value=min_val, value=4.0 if unidad=="metros" else 400.0, step=1.0)
largo_input = st.number_input(f"Largo del espacio ({unidad})", min_value=min_val, value=6.0 if unidad=="metros" else 600.0, step=1.0)
ancho_m, largo_m = ancho_input * factor, largo_input * factor
area_m2 = round(ancho_m * largo_m, 2)
st.markdown(f"**Área total:** {area_m2} m²")

# 2. Bordillos y esquineros
incluir_bordillos = st.checkbox("Agregar bordillos", True)
incluir_esquineros = st.checkbox("Agregar esquineros", True)
pos_bord = st.multiselect("¿Dónde colocar bordillos?", ["Arriba","Abajo","Izquierda","Derecha"], default=["Arriba","Abajo","Izquierda","Derecha"])

# 3. Colores disponibles y color base
colores = {
    "Blanco":"#FFFFFF","Negro":"#000000","Gris":"#B0B0B0","Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0","Celeste":"#00B0F0","Amarillo":"#FFFF00","Verde":"#00B050","Rojo":"#FF0000"
}
lista_colores = list(colores.keys())
color_base = st.selectbox("Color base", lista_colores, index=lista_colores.index("Blanco"))

# 4. Inicialización del DataFrame en session_state
cols = math.ceil(ancho_m / 0.4)
rows = math.ceil(largo_m / 0.4)
if 'df' not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame([[color_base]*cols for _ in range(rows)])
df = st.session_state.df

# 5. Heatmap Plotly interactivo
st.subheader("Haz clic en la cuadrícula para pintar")
z = [[lista_colores.index(df.iat[r, c]) for c in range(cols)] for r in range(rows)]
fig = go.Figure(go.Heatmap(
    z=z,
    x=list(range(cols)),
    y=list(range(rows)),
    colorscale=[[i/(len(lista_colores)-1), colores[name]] for i, name in enumerate(lista_colores)],
    showscale=False,
    zmin=0, zmax=len(lista_colores)-1
))
# Anclar ejes a unidades enteras
fig.update_xaxes(tickmode="linear", tick0=0, dtick=1, showgrid=False, showticklabels=False)
fig.update_yaxes(tickmode="linear", tick0=0, dtick=1, showgrid=False, showticklabels=False, autorange='reversed')
fig.update_layout(width=400, height=400, margin=dict(l=20, r=20, t=20, b=20))
# Mostrar y capturar eventos de clic
selected = plotly_events(fig, click_event=True, key="plotly")
if selected:
    c = int(selected[0]['x'])
    r = int(selected[0]['y'])
    if 0 <= r < rows and 0 <= c < cols:
        df.iat[r, c] = color_base
        st.session_state.df = df
st.plotly_chart(fig, use_container_width=True)

# 6. Renderización final con Matplotlib
fig2, ax = plt.subplots(figsize=(cols/5, rows/5))
for y in range(rows):
    for x in range(cols):
        color = colores.get(df.iat[y, x], "#FFFFFF")
        ax.add_patch(plt.Rectangle((x, rows-1-y), 1, 1, facecolor=color, edgecolor="black"))
# Bordillos delgados
if incluir_bordillos:
    if "Arriba" in pos_bord: ax.add_patch(plt.Rectangle((0, rows), cols, 0.15, facecolor="black"))
    if "Abajo" in pos_bord: ax.add_patch(plt.Rectangle((0, -0.15), cols, 0.15, facecolor="black"))
    if "Izquierda" in pos_bord: ax.add_patch(plt.Rectangle((-0.15, 0), 0.15, rows, facecolor="black"))
    if "Derecha" in pos_bord: ax.add_patch(plt.Rectangle((cols, 0), 0.15, rows, facecolor="black"))
# Esquineros
if incluir_esquineros:
    s = 0.15
    for (x, y) in [(0,0),(0,rows),(cols,0),(cols,rows)]:
        ax.add_patch(plt.Rectangle((x-s/2, y-s/2), s, s, facecolor="black"))
ax.set_xlim(-0.5, cols+0.5)
ax.set_ylim(-0.5, rows+0.5)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig2)

# 7. Conteo de material y dimensiones en palmetas
total_palmetas = rows * cols
bord_count = sum([cols if side in ["Arriba","Abajo"] else rows for side in pos_bord]) - 2*len(pos_bord)
esq_count = 4 if incluir_esquineros else 0
st.markdown(f"**Total palmetas:** {total_palmetas}")
st.markdown(f"**Bordillos:** {bord_count}")
st.markdown(f"**Esquineros:** {esq_count}")
st.markdown(f"**Dimensiones (palmetas):** {cols} x {rows}")
