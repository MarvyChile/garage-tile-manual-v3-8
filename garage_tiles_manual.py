
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="centered")
st.title("Garage Tile Designer v3.9 - Clickable Grid")

# 1. Unidad y medidas
unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"], key="unidad")
factor = 1 if unidad=="metros" else 0.01
min_val = 1.0 if unidad=="metros" else 10.0
ancho_input = st.number_input(f"Ancho ({unidad})", min_value=min_val, value=4.0 if unidad=="metros" else 400.0, step=1.0)
largo_input = st.number_input(f"Largo ({unidad})", min_value=min_val, value=6.0 if unidad=="metros" else 600.0, step=1.0)
ancho_m, largo_m = ancho_input*factor, largo_input*factor
area_m2 = round(ancho_m*largo_m,2)
st.markdown(f"**Área total:** {area_m2} m²")

# 2. Bordillos y esquineros
bord = st.checkbox("Agregar bordillos", True)
esq = st.checkbox("Agregar esquineros", True)
pos_b = st.multiselect("Dónde bordillos?", ["Arriba","Abajo","Izquierda","Derecha"],
                       default=["Arriba","Abajo","Izquierda","Derecha"])

# 3. Colores y base
colores = {"Blanco":"#FFFFFF","Negro":"#000000","Gris":"#B0B0B0","Gris Oscuro":"#4F4F4F",
           "Azul":"#0070C0","Celeste":"#00B0F0","Amarillo":"#FFFF00","Verde":"#00B050","Rojo":"#FF0000"}
lista = list(colores.keys())
base = st.selectbox("Color base", lista, index=lista.index("Blanco"))

# 4. DataFrame inicial
cols = math.ceil(ancho_m/0.4); rows = math.ceil(largo_m/0.4)
if 'df' not in st.session_state or st.session_state.df.shape!=(rows,cols):
    st.session_state.df = pd.DataFrame([[base]*cols for _ in range(rows)])
df = st.session_state.df

# 5. Canvas de dibujo por celda
st.subheader("Diseño: haz clic en una celda")
canvas_size = 400
cell_w = canvas_size/cols; cell_h = canvas_size/rows
canvas_res = st_canvas(
    fill_color=colores[base],
    stroke_width=cell_w,
    stroke_color=colores[base],
    background_color="#EEE",
    height=canvas_size,
    width=canvas_size,
    drawing_mode="rect",
    update_streamlit=True,
    key="canvas"
)

# Procesa dibujo
if canvas_res.json_data and 'objects' in canvas_res.json_data:
    for obj in canvas_res.json_data["objects"]:
        left, top = obj["left"], obj["top"]
        c = int(left//cell_w); r = int(top//cell_h)
        if r<rows and c<cols:
            df.iat[rows-1-r,c] = base
    # limpiar objetos procesados
    canvas_res.json_data["objects"].clear()
    st.session_state.df = df

# 6. Mostrar gráfico final
fig, ax = plt.subplots(figsize=(cols/5, rows/5))
for y in range(rows):
    for x in range(cols):
        color = colores.get(df.iat[y,x],"#FFF")
        ax.add_patch(plt.Rectangle((x,rows-1-y),1,1,facecolor=color,edgecolor="black"))
# bordillos y esquineros
if bord:
    if "Arriba" in pos_b: ax.add_patch(plt.Rectangle((0,rows),cols,0.15,facecolor="black"))
    if "Abajo" in pos_b: ax.add_patch(plt.Rectangle((0,-0.15),cols,0.15,facecolor="black"))
    if "Izquierda" in pos_b: ax.add_patch(plt.Rectangle((-0.15,0),0.15,rows,facecolor="black"))
    if "Derecha" in pos_b: ax.add_patch(plt.Rectangle((cols,0),0.15,rows,facecolor="black"))
if esq:
    s=0.15
    for (x,y) in [(0,0),(0,rows),(cols,0),(cols,rows)]:
        ax.add_patch(plt.Rectangle((x-s/2,y-s/2),s,s,facecolor="black"))
ax.set_xlim(-0.5,cols+0.5); ax.set_ylim(-0.5,rows+0.5)
ax.set_aspect('equal'); ax.axis('off')
st.pyplot(fig)

# 7. Conteo material
total = rows*cols
bord_count = sum([cols if side in ["Arriba","Abajo"] else rows for side in pos_b]) - 2*len(pos_b)
esq_count = 4 if esq else 0
st.markdown(f"**Total palmetas:** {total}")
st.markdown(f"**Bordillos:** {bord_count}")
st.markdown(f"**Esquineros:** {esq_count}")
st.markdown(f"**Dimensiones:** {cols} x {rows} palmetas")
