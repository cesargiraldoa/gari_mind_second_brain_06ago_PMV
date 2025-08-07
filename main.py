import streamlit as st

# Módulos locales
from gari_frontend_mockup import *  # Daily Magnet
from db_connection import get_prestaciones

st.set_page_config(page_title="GariMind Second Brain – CésarStyle™", layout="wide")
st.sidebar.title("GariMind Menu")

menu = st.sidebar.radio("Navegación principal", [
    "🧲 Daily Magnet – Scroll Narrativo (Real)",
    "📊 Análisis Edad vs Prestación",
])

# ---------- Routes ----------
if menu == "🧲 Daily Magnet – Scroll Narrativo (Real)":
    # Re-usa el front del explorador: mostramos el título y dejamos que el archivo lo maneje
    st.experimental_rerun()  # garantiza que el daily magnet se ejecute como página activa

elif menu == "📊 Análisis Edad vs Prestación":
    st.title("📊 Análisis Edad vs Prestación – Módulo dedicado")
    try:
        from gari_analytics_edad_vs_prestacion import render_edad_vs_prestacion
        # Trae TODOS los datos de la tabla fija
        df = get_prestaciones(limit=None)
        render_edad_vs_prestacion(df, titulo="📊 Análisis Edad vs Prestación (Prestaciones_Temporal)")
    except Exception as e:
        st.error("No se pudo cargar el módulo de análisis.")
        st.exception(e)
