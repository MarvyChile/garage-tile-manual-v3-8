
import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Configuración
st.set_page_config(layout="centered")
st.title("Garage Tile Designer v3.10 - Clickable Image")

# 1. Unidad y medidas
unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"])
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
pos_b = st.multiselect("Dónde bordillos?", ["Arriba","Abajo","Izquierda","Derecha"], default=["Arriba","Abajo","Izquierda","Derecha"])

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

# 5. Mostrar Plotly heatmap para clic
st.subheader("Haz clic en la cuadrícula para pintar")
z = [[lista.index(df.iat[r, c])] for r in range(rows) for c in range(cols)]
# but we need matrix shape rows x cols
z = [[lista.index(df.iat[r, c]) for c in range(cols)] for r in range(rows)]

fig = go.Figure(data=go.Heatmap(
    z=z,
    x=list(range(cols)),
    y=list(range(rows)),
    colorscale=[ [i/(len(lista)-1), colores[name]] for i, name in enumerate(lista) ],
    showscale=False,
    hoverinfo='none',
))
fig.update_xaxes(showgrid=False, ticks='')
fig.update_yaxes(showgrid=False, ticks='')
fig.update_layout(
    width=400,
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    yaxis=dict(autorange='reversed')  # para que (0,0) arriba izquierda
)

# Capturar clicks
selected = plotly_events(fig, click_event=True, key='click')
if selected:
    pt = selected[0]
    c = int(pt['x'])
    r = int(pt['y'])
    df.iat[r, c] = base
    st.session_state.df = df

st.pyplot(fig)

# 6. Render final con matplotlib
import matplotlib.pyplot as plt
fig2, ax = plt.subplots(figsize=(cols/5, rows/5))
for y in range(rows):
    for x in range(cols):
        color = colores.get(df.iat[y,x],"#FFFFFF")
        ax.add_patch(plt.Rectangle((x, rows-1-y), 1, 1, facecolor=color, edgecolor="black"))
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
ax.set_xlim(-0.5, cols+0.5)
ax.set_ylim(-0.5, rows+0.5)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig2)

# 7. Conteo material y dimensiones
total = rows*cols
bord_count = sum([cols if side in ["Arriba","Abajo"] else rows for side in pos_b]) - 2*len(pos_b)
esq_count = 4 if esq else 0
st.markdown(f"**Total palmetas:** {total}")
st.markdown(f"**Bordillos:** {bord_count}")
st.markdown(f"**Esquineros:** {esq_count}")
st.markdown(f"**Dimensiones (palmetas):** {cols} x {rows}")
