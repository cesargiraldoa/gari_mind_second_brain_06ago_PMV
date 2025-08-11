import streamlit as st
import pandas as pd
from db_connection import get_sales_data, get_preview, get_all_sales_data

st.set_page_config(page_title="Gari – Conexión y Preview", layout="wide")
st.title("🧠 Gari Analytics – Conexión y Preview (pymssql/Abraham)")

# 🔌 Verificación rápida con el código de Abraham
st.subheader("🔌 Verificación rápida")
try:
    df_preview = get_sales_data()  # usa TOP 10 de Prestaciones_Temporal
    st.success("Conexión OK ✅ (pymssql)")
    st.dataframe(df_preview)
except Exception as e:
    st.error(f"Fallo en conexión/consulta: {e}")

st.divider()

# ⚙️ Opciones para análisis completo (sin mostrar toda la tabla)
st.subheader("📊 Cargar datos completos para análisis")
tabla = st.text_input("Tabla base", value="Prestaciones_Temporal")
c1, c2 = st.columns(2)
date_from = c1.date_input("Desde (opcional)", value=None)
date_to   = c2.date_input("Hasta (opcional)", value=None)
date_col  = st.text_input("Columna de fecha (opcional)", value="")

if st.button("Cargar todo (solo para análisis)"):
    try:
        df_all = get_all_sales_data(
            table_name=tabla.strip(),
            date_col=(date_col.strip() or None),
            date_from=(date_from.strftime("%Y-%m-%d") if date_from else None),
            date_to=(date_to.strftime("%Y-%m-%d") if date_to else None),
        )
        st.success(f"Dataset para análisis cargado: {len(df_all):,} filas ✅ (abajo solo preview 10)")
        st.dataframe(df_all.head(10))
    except Exception as e:
        st.error(f"No se pudo cargar el dataset completo: {e}")
