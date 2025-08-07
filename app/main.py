import streamlit as st
from db_connection import get_sales_data

st.set_page_config(page_title="🧠 GariMind – Daily Magnet", layout="wide")
st.title("🧲 Daily Magnet – Scroll Narrativo")

st.markdown("Bienvenido al resumen diario de decisiones, ventas y aprendizajes. Consulta lo que ha pasado hoy con tus datos.")

df = get_sales_data()
if df is not None and not df.empty:
    if "error" in df.columns:
        st.error(f"Error al consultar datos: {df['error'][0]}")
    else:
        st.dataframe(df.head(10))
else:
    st.warning("⚠️ Consulta sin resultados o error silencioso.")
