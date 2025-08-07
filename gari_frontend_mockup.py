import streamlit as st
import pandas as pd
import pyodbc
from db_connection import get_sales_data

st.set_page_config(page_title="GariMind Second Brain – CésarStyle™", layout="wide")
st.title("🧲 Daily Magnet – Conexión a Base de Datos (main.py)")

# Evita conectar al cargar: usamos botón + cache
@st.cache_data(ttl=300, show_spinner=True)
def cargar_datos(query):
    return get_sales_data(query=query)

# Parámetros básicos
with st.sidebar:
    st.subheader("⚙️ Parámetros")
    query = st.text_area(
        "Consulta SQL",
        value="SELECT TOP 1000 * FROM dbo.Prestaciones_Temporal",
        height=120
    )

col1, col2 = st.columns([1,1], vertical_alignment="center")

with col1:
    if st.button("📥 Cargar datos ahora", use_container_width=True):
        try:
            df = cargar_datos(query)
            st.session_state["daily_df"] = df
            st.success(f"Datos cargados: {len(df):,} filas, {len(df.columns)} columnas.")
        except pyodbc.Error as e:
            st.error("No se pudo conectar a SQL Server.")
            st.exception(e)
        except Exception as e:
            st.error("Error procesando la consulta.")
            st.exception(e)

with col2:
    if st.button("🧹 Limpiar datos en memoria", use_container_width=True):
        st.session_state.pop("daily_df", None)
        cargar_datos.clear()  # limpia cache
        st.info("Cache y memoria limpiadas.")

st.divider()

# Mostrar resultados solo si existen
df = st.session_state.get("daily_df")
if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
    st.subheader("📊 Vista rápida")
    st.dataframe(df.head(100), use_container_width=True)

    # Pequeño resumen útil
    with st.expander("Resumen de columnas"):
        meta = pd.DataFrame({
            "columna": df.columns,
            "nulos": df.isna().sum().values,
            "tipo": df.dtypes.astype(str).values,
            "únicos": [df[c].nunique(dropna=True) for c in df.columns]
        })
        st.dataframe(meta, use_container_width=True)
else:
    st.info("Pulsa **“Cargar datos ahora”** para traer la muestra.")

