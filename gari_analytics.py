# gari_analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_sqlserver_connection

def main():
    st.subheader("🔍 Análisis de Edad vs Prestación – Universo Completo")

    try:
        conn = get_sqlserver_connection()

        # ✅ Traer TODOS los registros de la tabla
        query = "SELECT Edad, Prestacion FROM dbo.Prestaciones_Temporal"
        df = pd.read_sql(query, conn)
        conn.close()

        # Mostrar cantidad total de registros
        st.success(f"Total de registros analizados: {len(df):,}")

        if df.empty:
            st.warning("⚠️ No hay datos para analizar.")
            return

        # Análisis descriptivo
        st.write("### Vista previa de datos")
        st.dataframe(df)

        # Gráfico interactivo con todos los datos
        fig = px.histogram(
            df,
            x="Edad",
            color="Prestacion",
            barmode="group",
            title="Distribución de Edad por Prestación",
            labels={"Edad": "Edad del paciente", "Prestacion": "Tipo de prestación"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Estadísticas
        st.write("### Estadísticas por Prestación")
        st.write(df.groupby("Prestacion")["Edad"].describe())

    except Exception as e:
        st.error(f"Error en el análisis: {e}")
