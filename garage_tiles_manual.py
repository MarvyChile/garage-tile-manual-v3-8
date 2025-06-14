
import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from st_aggrid.shared import JsCode

st.set_page_config(layout="centered")
st.title("Garage Tile Designer – Grid interactivo con AgGrid")

# 1. Parámetros y DataFrame inicial
dp = 0.4  # 40 cm
unidad = st.selectbox("Unidad", ["metros","centímetros"])
factor = 1 if unidad=="metros" else 0.01
ancho = st.number_input("Ancho", min_value=1.0, value=4.0, step=0.1) * factor
largo = st.number_input("Largo", min_value=1.0, value=6.0, step=0.1) * factor
cols = math.ceil(ancho/dp)
rows = math.ceil(largo/dp)
area = round(ancho*largo, 2)
st.markdown(f"**Área:** {area} m²")

# 2. Inicializa DataFrame en session_state
if "df" not in st.session_state or st.session_state.df.shape != (rows, cols):
    st.session_state.df = pd.DataFrame(
        [["Blanco"]*cols for _ in range(rows)]
    )
df = st.session_state.df

# 3. Definir colores y cellStyle en JS
colores = {
    "Blanco":"#FFFFFF","Negro":"#000000","Gris":"#B0B0B0","Gris Oscuro":"#4F4F4F",
    "Azul":"#0070C0","Celeste":"#00B0F0","Amarillo":"#FFFF00","Verde":"#00B050","Rojo":"#FF0000"
}
lista_colores = list(colores.keys())

cellstyle_jscode = JsCode('''
function(params) {
    var colorMap = {
        'Blanco':'#FFFFFF','Negro':'#000000','Gris':'#B0B0B0','Gris Oscuro':'#4F4F4F',
        'Azul':'#0070C0','Celeste':'#00B0F0','Amarillo':'#FFFF00','Verde':'#00B050','Rojo':'#FF0000'
    };
    return {
        'backgroundColor': colorMap[params.value] || '#FFFFFF',
        'color': params.value=='Negro' ? 'white' : 'black'
    };
}
''')

# 4. Configuración de AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, cellStyle=cellstyle_jscode)
gb.configure_grid_options(stopEditingWhenCellsLoseFocus=True)
grid_opts = gb.build()

# 5. Mostrar AgGrid y capturar cambios
grid_response = AgGrid(
    df,
    gridOptions=grid_opts,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    data_return_mode=DataReturnMode.AS_INPUT,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
)
st.session_state.df = pd.DataFrame(grid_response["data"])
df = st.session_state.df

# 6. Render final con Matplotlib
fig, ax = plt.subplots(figsize=(cols/5, rows/5))
for y in range(rows):
    for x in range(cols):
        c = df.iat[y, x]
        ax.add_patch(plt.Rectangle((x, rows-1-y), 1, 1,
                                   facecolor=colores.get(c, "#FFFFFF"),
                                   edgecolor="black"))
ax.set_xlim(-0.5, cols+0.5)
ax.set_ylim(-0.5, rows+0.5)
ax.set_aspect("equal")
ax.axis("off")
st.pyplot(fig)
