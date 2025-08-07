import streamlit as st
import pandas as pd
from db_connection import get_all_sales_data

st.set_page_config(page_title="GariMind Second Brain – CésarStyle™", layout="wide")
st.title("🧲 Daily Magnet – Conexión a Base de Datos (pymssql)")

@st.cache_data(ttl=600, show_spinner="Cargando todos los datos desde SQL Server...")
def cargar_todos_los_datos():
    return get_all_sales_data()

if st.button("📥 Cargar TODOS los datos", use_container_width=True):
    try:
        df = cargar_todos_los_datos()
        st.session_state["daily_df"] = df
        st.success(f"Datos cargados: {len(df):,} filas y {len(df.columns)} columnas.")
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
