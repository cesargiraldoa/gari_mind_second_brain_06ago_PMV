import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_sales_data

def calcular_edad(fecha_nacimiento, fecha_ref):
    return fecha_ref.year - fecha_nacimiento.year - (
        (fecha_ref.month, fecha_ref.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )

def analizar_edad_vs_prestacion(df):
    st.subheader("📊 Análisis Edad vs Prestación")

    # Convertir fechas
    df["FechaNacimiento"] = pd.to_datetime(df["FechaNacimiento"], errors="coerce")
    df["Fecha_Presupuesto"] = pd.to_datetime(df["Fecha_Presupuesto"], errors="coerce")

    # Calcular Edad
    df["Edad"] = df.apply(
        lambda row: calcular_edad(row["FechaNacimiento"], row["Fecha_Presupuesto"])
        if pd.notnull(row["FechaNacimiento"]) and pd.notnull(row["Fecha_Presupuesto"])
        else None,
        axis=1
    )

    # Crear grupos de edad
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 100]
    labels = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71+"]
    df["GrupoEdad"] = pd.cut(df["Edad"], bins=bins, labels=labels, right=False)

    # Agrupar por grupo de edad y prestación
    resumen = df.groupby(["GrupoEdad", "Prestacion"]).size().reset_index(name="Conteo")

    # Visualización
    fig = px.bar(
        resumen,
        x="GrupoEdad",
        y="Conteo",
        color="Prestacion",
        title="Distribución de Prestaciones por Grupo de Edad",
        labels={"GrupoEdad": "Grupo de Edad", "Conteo": "Cantidad"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar tabla resumen
    with st.expander("📋 Ver tabla resumen"):
        st.dataframe(resumen)


def main():
    st.subheader("🔍 Gari Analytics – Análisis Exploratorio Inicial")
    
    df = get_sales_data()

    if df is None or df.empty:
        st.warning("⚠️ No se pudo cargar la data o está vacía.")
        return

    st.markdown("### 👁️ Vista previa de los datos")
    st.dataframe(df.head(10))

    # Mostrar resumen general
    st.markdown("### 📊 Estadísticas Descriptivas")
    st.dataframe(df.describe(include="all"))

    # Conteo por columnas
    st.markdown("### 📈 Conteo de valores por columna (no nulos)")
    conteo = df.count().reset_index()
    conteo.columns = ["Columna", "No Nulos"]
    st.dataframe(conteo)

    # Lista de columnas
    st.markdown("### 📚 Columnas disponibles")
    st.json(list(df.columns))

    # Distribución de columnas categóricas
    st.markdown("### 📊 Distribución de valores por columna categórica")
    columnas_categoricas = df.select_dtypes(include="object").columns
    for col in columnas_categoricas:
        st.write(f"#### {col}")
        st.bar_chart(df[col].value_counts())

    # 🔘 Botón para activar análisis
    if st.button("🔎 Analizar Edad vs Prestación"):
        analizar_edad_vs_prestacion(df)
