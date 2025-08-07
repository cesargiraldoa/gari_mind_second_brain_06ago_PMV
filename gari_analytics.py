import streamlit as st
import pandas as pd
from db_connection import get_sales_data


def main():
    st.subheader("🔍 Gari Analytics – Análisis Exploratorio Inicial")

    df = get_sales_data()

    if df is None or df.empty:
        st.warning("No se encontraron datos en la tabla.")
        return

    st.markdown("### Vista previa de los datos")
    st.dataframe(df.head(10))

    st.markdown("### Estadísticas Descriptivas")
    st.dataframe(df.describe(include='all'))

    st.markdown("### Conteo de valores por columna (no nulos)")
    st.write(df.count())

    st.markdown("### Columnas disponibles")
    st.write(df.columns.tolist())

    st.markdown("### Distribución de valores por columna categórica")
    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        st.markdown(f"**{col}**")
        st.bar_chart(df[col].value_counts().head(10))


if __name__ == "__main__":
    main()
