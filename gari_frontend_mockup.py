import streamlit as st
import pandas as pd
from db_connection import get_sales_data, list_tables_like

st.set_page_config(page_title="GariMind Second Brain – CésarStyle™", layout="wide")
st.title("🧲 Daily Magnet – Conexión a Base de Datos (pymssql)")

with st.sidebar:
    st.subheader("⚙️ Parámetros")
    tablas = list_tables_like() or []
    # Por defecto intenta Prestaciones_Temporal si existe, si no, primera
    default_idx = next((i for i, t in enumerate(tablas) if "Prestaciones_Temporal" in t), 0) if tablas else 0
    tabla_sel = st.selectbox("Tabla origen", tablas, index=default_idx if tablas else 0)
    traer_top = st.checkbox("Traer solo muestra TOP 10 (debug rápido)", value=False)

@st.cache_data(ttl=900, show_spinner="Cargando datos desde SQL Server…")
def cargar(tabla, solo_top):
    # tabla viene como [schema].[name], me quedo con el nombre sin corchetes
    nombre = tabla.split("].")[-1].replace("]", "").replace("[", "") if tabla else "Prestaciones_Temporal"
    return get_sales_data(table=nombre, top=10 if solo_top else None)

if st.button("📥 Cargar TODOS los datos", use_container_width=True):
    try:
        df = cargar(tabla_sel, traer_top)
        st.session_state["daily_df"] = df
        st.success(f"Datos cargados: {len(df):,} filas · {len(df.columns)} columnas.")
    except Exception as e:
        st.error("Error conectando o trayendo datos.")
        st.exception(e)

st.divider()

df = st.session_state.get("daily_df")
if isinstance(df, pd.DataFrame) and not df.empty:
    st.subheader("📊 Vista general")
    st.dataframe(df.head(100), use_container_width=True)
    st.caption(f"Columnas: {list(df.columns)}")
else:
    st.info("Pulsa **Cargar TODOS los datos** para traer el dataset completo.")
