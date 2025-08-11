# main.py
import streamlit as st
import pandas as pd
from db_connection import get_sales_data, get_all_sales_data

st.set_page_config(page_title="Gari – Health & Preview", layout="wide")
st.title("🧠 Gari Analytics – Conexión y Preview")

st.subheader("🔌 Verificación rápida")
try:
    sample = get_sales_data(5)
    st.success("Conexión SQL OK y funciones importadas correctamente ✅")
    st.dataframe(sample)
except Exception as e:
    st.error(f"Fallo en conexión/consulta: {e}")

st.subheader("📅 Filtro opcional para análisis (usa toda la tabla)")
c1, c2 = st.columns(2)
date_from = c1.date_input("Desde", value=None)
date_to   = c2.date_input("Hasta", value=None)

if st.button("Cargar datos completos para análisis"):
    try:
        df_all = get_all_sales_data(
            date_from.strftime("%Y-%m-%d") if date_from else None,
            date_to.strftime("%Y-%m-%d") if date_to else None
        )
        st.success(f"Datos cargados para análisis: {len(df_all):,} filas ✅")
        st.write("Mostrando solo 10 filas a modo de preview:")
        st.dataframe(df_all.head(10))
    except Exception as e:
        st.error(f"No se pudo cargar el dataset completo: {e}")
