import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(layout="centered")
st.title("Garage Tile Designer Final")

# 1. Unidad y medidas
unidad = st.selectbox("Selecciona la unidad de medida", ["metros", "centímetros"])
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

# 3. Colores disponibles
colores = {
    "Blanco": "#FFFFFF",
    "Negro": "#000000",
    "Gris": "#B0B0B0",
    "Gris Oscuro": "#4F4F4F",
    "Azul": "#0070C0",
    "Celeste": "#00B0F0",
    "Amarillo": "#FFFF00",
    "Verde": "#00B050",
    "Rojo": "#FF0000"
}
lista_colores = list(colores.keys())

# 4. Calcular dimensiones en palmetas
dp = 0.4  # 40 cm
dim_cols = math.ceil(ancho_m / dp)
dim_rows = math.ceil(largo_m / dp)

# 5. Inicializar DataFrame en session_state
if 'df' not in st.session_state or st.session_state.df.shape != (dim_rows, dim_cols):
    st.session_state.df = pd.DataFrame(
        [["Blanco"] * dim_cols for _ in range(dim_rows)]
    )
df = st.session_state.df

# 6. Selección de color base
color_base = st.selectbox("Color base", lista_colores, index=0)
if st.button("Aplicar color base"):
    st.session_state.df = pd.DataFrame(
        [[color_base] * dim_cols for _ in range(dim_rows)]
    )
    df = st.session_state.df

# 7. Editor interactivo de diseño
st.subheader("Diseño personalizado: edita la tabla para cambiar colores")
edited = st.data_editor(
    df,
    num_rows="fixed",
    use_container_width=True,
    column_config={
        col: st.column_config.SelectboxColumn(options=lista_colores)
        for col in df.columns
    }
)
# Guardar ediciones\ n
df = edited
st.session_state.df = df

# 8. Renderizar vista gráfica final
fig, ax = plt.subplots(figsize=(dim_cols/5, dim_rows/5))
for y in range(dim_rows):
    for x in range(dim_cols):
        color_name = df.iat[y, x]
        face = colores.get(color_name, "#FFFFFF")
        edge = "white" if color_name == "Negro" else "black"
        ax.add_patch(
            plt.Rectangle((x, dim_rows - 1 - y), 1, 1,
                          facecolor=face, edgecolor=edge)
        )
# Bordillos
if incluir_bordillos:
    if "Arriba" in pos_bord:
        ax.add_patch(plt.Rectangle((0, dim_rows), dim_cols, 0.15, facecolor="black"))
    if "Abajo" in pos_bord:
        ax.add_patch(plt.Rectangle((0, -0.15), dim_cols, 0.15, facecolor="black"))
    if "Izquierda" in pos_bord:
        ax.add_patch(plt.Rectangle((-0.15, 0), 0.15, dim_rows, facecolor="black"))
    if "Derecha" in pos_bord:
        ax.add_patch(plt.Rectangle((dim_cols, 0), 0.15, dim_rows, facecolor="black"))
# Esquineros
if incluir_esquineros:
    s = 0.15
    for (x, y) in [(0, 0), (0, dim_rows), (dim_cols, 0), (dim_cols, dim_rows)]:
        ax.add_patch(plt.Rectangle((x - s/2, y - s/2), s, s, facecolor="black"))
ax.set_xlim(-0.5, dim_cols + 0.5)
ax.set_ylim(-0.5, dim_rows + 0.5)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)

# 9. Cantidad de material y dimensiones
total_palmetas = dim_cols * dim_rows
bord_count = sum([dim_cols if side in ["Arriba", "Abajo"] else dim_rows for side in pos_bord]) - 2 * len(pos_bord)
esq_count = 4 if incluir_esquineros else 0
st.markdown(f"**Total palmetas:** {total_palmetas}")
st.markdown(f"**Bordillos:** {bord_count}")
st.markdown(f"**Esquineros:** {esq_count}")
st.markdown(f"**Dimensiones (palmetas):** {dim_cols} x {dim_rows}")
