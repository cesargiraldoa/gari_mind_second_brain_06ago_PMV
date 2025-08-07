# gari_analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_sales_data

def _calcular_edad(fecha_nac, fecha_ref):
    return (
        fecha_ref.year - fecha_nac.year
        - ((fecha_ref.month, fecha_ref.day) < (fecha_nac.month, fecha_nac.day))
    )

def analizar_edad_vs_prestacion(df: pd.DataFrame):
    st.subheader("📊 Edad vs Prestación (universo completo)")

    # Convertir fechas (intenta con los nombres esperados)
    df["FechaNacimiento"]   = pd.to_datetime(df.get("FechaNacimiento"),   errors="coerce")
    df["Fecha_Presupuesto"] = pd.to_datetime(df.get("Fecha_Presupuesto"), errors="coerce")

    # Calcular Edad cuando existan ambas fechas
    df["Edad"] = df.apply(
        lambda r: _calcular_edad(r["FechaNacimiento"], r["Fecha_Presupuesto"])
        if pd.notnull(r["FechaNacimiento"]) and pd.notnull(r["Fecha_Presupuesto"])
        else None,
        axis=1,
    )

    # Bins/grupos de edad
    bins   = [0,10,20,30,40,50,60,70,120]
    labels = ["0-10","11-20","21-30","31-40","41-50","51-60","61-70","71+"]
    df["GrupoEdad"] = pd.cut(df["Edad"], bins=bins, labels=labels, right=False)

    # Validar columna Prestacion
    if "Prestacion" not in df.columns:
        st.error("No se encontró la columna 'Prestacion' en la tabla.")
        st.write("Columnas disponibles:", list(df.columns))
        return

    # Resumen por grupo
    resumen = (
        df.dropna(subset=["GrupoEdad", "Prestacion"])
          .groupby(["GrupoEdad", "Prestacion"])
          .size()
          .reset_index(name="Conteo")
          .sort_values(["GrupoEdad", "Conteo"], ascending=[True, False])
    )

    # Gráfico
    fig = px.bar(
        resumen,
        x="GrupoEdad", y="Conteo", color="Prestacion",
        title="Distribución de Prestaciones por Grupo de Edad",
        labels={"GrupoEdad": "Grupo de Edad", "Conteo": "Cantidad"},
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Ver tabla resumen"):
        st.dataframe(resumen, use_container_width=True)

def main():
    st.subheader("🔍 Gari Analytics – Exploratorio + Edad vs Prestación (100% registros)")

    # ✅ Traer TODOS los registros (sin TOP ni .head en el análisis)
    df = get_sales_data(limit=None)

    if df is None or df.empty:
        st.warning("⚠️ No se pudo cargar la data o está vacía.")
        return

    st.success(f"Total de registros cargados: {len(df):,}")

    # Solo para vista previa (NO limita el análisis)
    with st.expander("👁️ Vista previa (primeras filas)"):
        st.dataframe(df.head(50), use_container_width=True)

    # Lanzar análisis
    if st.button("🔎 Analizar Edad vs Prestación (usar todos los registros)"):
        analizar_edad_vs_prestacion(df)
