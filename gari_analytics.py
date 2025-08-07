# gari_analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_sales_data

def calcular_edad(fecha_nacimiento, fecha_ref):
    return fecha_ref.year - fecha_nacimiento.year - (
        (fecha_ref.month, fecha_ref.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )

def analizar_edad_vs_prestacion(df):
    st.subheader("📊 Análisis Edad vs Prestación (universo completo)")

    # Convertir fechas
    df["FechaNacimiento"] = pd.to_datetime(df["FechaNacimiento"], errors="coerce")
    df["Fecha_Presupuesto"] = pd.to_datetime(df["Fecha_Presupuesto"], errors="coerce")

    # Calcular edad (si ambas fechas existen)
    df["Edad"] = df.apply(
        lambda r: calcular_edad(r["FechaNacimiento"], r["Fecha_Presupuesto"])
        if pd.notnull(r["FechaNacimiento"]) and pd.notnull(r["Fecha_Presupuesto"])
        else None, axis=1
    )

    # Agrupar edades
    bins   = [0,10,20,30,40,50,60,70,120]
    labels = ["0-10","11-20","21-30","31-40","41-50","51-60","61-70","71+"]
    df["GrupoEdad"] = pd.cut(df["Edad"], bins=bins, labels=labels, right=False)

    # Resumen
    resumen = (
        df.dropna(subset=["GrupoEdad","Prestacion"])
          .groupby(["GrupoEdad","Prestacion"]).size()
          .reset_index(name="Conteo")
    )

    # Gráfico
    fig = px.bar(
        resumen, x="GrupoEdad", y="Conteo", color="Prestacion",
        title="Distribución de Prestaciones por Grupo de Edad",
        labels={"GrupoEdad":"Grupo de Edad","Conteo":"Cantidad"}
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Ver tabla resumen"):
        st.dataframe(resumen)

def main():
    st.subheader("🔍 Gari Analytics – Análisis Exploratorio + Edad vs Prestación")

    # ✅ Traer TODOS los registros
    df = get_sales_data(limit=None)

    if df is None or df.empty:
        st.warning("⚠️ No se pudo cargar la data o está vacía.")
        return

    st.success(f"Total de registros cargados: {len(df):,}")

    st.markdown("### 👁️ Vista previa (solo visual, NO limita el análisis)")
    st.dataframe(df.head(50))  # solo preview, el análisis usa df completo

    # Botón para lanzar el análisis
    if st.button("🔎 Analizar Edad vs Prestación (100% registros)"):
        analizar_edad_vs_prestacion(df)
