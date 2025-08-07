import streamlit as st
from app.db_connection import get_sales_data

st.set_page_config(page_title="🧠 GariMind – Daily Magnet", layout="wide")

st.title("🧲 Daily Magnet – Scroll Narrativo")

st.markdown("Bienvenido al resumen diario de decisiones, ventas y aprendizajes. Consulta lo que ha pasado hoy con tus datos.")

# Mostrar datos de ventas
df = get_sales_data()
if df is not None:
    st.dataframe(df.head(10))
else:
    st.error("No se pudieron cargar los datos de ventas.")
