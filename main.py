import streamlit as st
import pandas as pd
from db_connection import get_sales_data
from gari_analytics import run_age_vs_prestacion

st.set_page_config(page_title="Gari – Conexión + Analítica", layout="wide")
st.title("🧠 Gari Analytics – Conexión y Analítica (pymssql/Abraham)")

tabs = st.tabs(["✅ Conexión & Preview", "📈 Edad vs Prestación"])

with tabs[0]:
    st.subheader("🔌 Verificación rápida")
    try:
        df_preview = get_sales_data()
        st.success("Conexión OK ✅ (pymssql)")
        st.dataframe(df_preview)
    except Exception as e:
        st.error(f"Fallo en conexión/consulta: {e}")

with tabs[1]:
    run_age_vs_prestacion()
