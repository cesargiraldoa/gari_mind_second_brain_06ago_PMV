import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_sales_data

def calcular_edad(fecha_nacimiento, fecha_actual):
    return (fecha_actual - fecha_nacimiento).days // 365

def main():
    st.header("🔍 Gari Analytics – Análisis Exploratorio de Datos")

    df = get_sales_data()
    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return
    if "error" in df.columns:
        st.error(f"Error: {df['error'][0]}")
        return

    st.subheader("📋 Vista general de los datos")
    st.dataframe(df.head(10))

    st.subheader("📊 Distribución por Especialidad")
    if "Especialidad" in df.columns:
        fig = px.histogram(df, x="Especialidad")
        st.plotly_chart(fig)

    st.subheader("📊 Distribución por Estado")
    if "Estado" in df.columns:
        fig = px.histogram(df, x="Estado")
        st.plotly_chart(fig)

    st.subheader("📊 Profesional Presupuesto")
    if "Profesional_Presupuesto" in df.columns:
        fig = px.histogram(df, x="Profesional_Presupuesto")
        st.plotly_chart(fig)

    st.subheader("📊 Sucursal")
    if "Sucursal_ppto" in df.columns:
        fig = px.histogram(df, x="Sucursal_ppto")
        st.plotly_chart(fig)

    st.subheader("📅 Distribución por Año de Presupuesto")
    if "Fecha_Presupuesto" in df.columns:
        df['Año_Presupuesto'] = pd.to_datetime(df['Fecha_Presupuesto'], errors='coerce').dt.year
        fig = px.histogram(df, x="Año_Presupuesto")
        st.plotly_chart(fig)

    st.subheader("🎂 Distribución de Edad (si existe FechaNacimiento)")
    if "FechaNacimiento" in df.columns:
        df["FechaNacimiento"] = pd.to_datetime(df["FechaNacimiento"], errors='coerce')
        fecha_actual = pd.Timestamp.now()
        df["Edad"] = df["FechaNacimiento"].apply(lambda x: calcular_edad(x, fecha_actual) if pd.notnull(x) else None)
        fig = px.histogram(df, x="Edad")
        st.plotly_chart(fig)
