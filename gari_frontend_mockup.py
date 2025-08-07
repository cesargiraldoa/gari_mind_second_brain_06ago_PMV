import streamlit as st
import pandas as pd
from db_connection import list_tables_like, detect_prestaciones_table, get_all_data_from

st.set_page_config(page_title="GariMind Second Brain – CésarStyle™", layout="wide")
st.title("🧲 Daily Magnet – Conexión a Base de Datos (pymssql)")

# 1) Detectar automáticamente y permitir elegir
with st.sidebar:
    st.subheader("⚙️ Parámetros")
    st.caption("Elige la tabla real (con esquema) para cargar TODOS los datos.")
    opciones = list_tables_like("")  # lista TODO
    sugerida = detect_prestaciones_table()
    idx = opciones.index(sugerida) if sugerida in opciones else 0
    tabla_sel = st.selectbox("Tabla", opciones, index=idx if opciones else 0)

@st.cache_data(ttl=600, show_spinner="Cargando todos los datos desde SQL Server...")
def cargar_todos(tabla_full):
    return get_all_data_from(tabla_full)

if st.button("📥 Cargar TODOS los datos", use_container_width=True):
    try:
        if not tabla_sel:
            st.error("No hay tablas visibles en la BD con tu usuario.")
        else:
            df = cargar_todos(tabla_sel)
            st.session_state["daily_df"] = df
            st.success(f"Datos cargados de {tabla_sel}: {len(df):,} filas, {len(df.columns)} columnas.")
    except Exception as e:
        st.error("Error conectando o trayendo datos.")
        st.exception(e)

st.divider()

df = st.session_state.get("daily_df")
if isinstance(df, pd.DataFrame) and not df.empty:
    st.subheader("📊 Vista general")
    st.dataframe(df.head(100), use_container_width=True)
    st.write("**Columnas:**", list(df.columns))
    st.write("**Total de filas:**", len(df))
else:
    st.info("Pulsa **Cargar TODOS los datos** para traer el dataset completo.")
