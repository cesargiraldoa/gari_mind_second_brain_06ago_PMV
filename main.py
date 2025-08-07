import streamlit as st
import pandas as pd

from db_connection import get_sales_data, get_all_sales_data
import gari_analytics_edad_vs_prestacion as mod

st.set_page_config(page_title="GariMind – Edad vs Prestación", layout="wide")

st.title("🧠 GariMind CésarStyle™ – Edad vs Prestación")

# ================
# Panel lateral
# ================
st.sidebar.header("⚙️ Controles")
preview = st.sidebar.checkbox("Mostrar vista previa (TOP 10)", value=True)
section = st.sidebar.radio(
    "Secciones", 
    ["🔍 Visión general", "🧪 Patrones y relación", "🔮 Predicción"],
    index=0
)

# ================
# Carga de datos
# ================
with st.spinner("Cargando datos..."):
    df_preview = get_sales_data()
    df_full = get_all_sales_data()

if "error" in df_full.columns:
    st.error("No fue posible cargar la tabla completa. Revisa la conexión o logs.")
    st.write(df_full)
else:
    st.success(f"✅ Datos cargados para análisis completo: N = {len(df_full):,} registros")
    if preview and "error" not in df_preview.columns:
        st.caption("Vista previa (TOP 10) – no afecta el análisis")
        st.dataframe(df_preview)

    # ================
    # Ruteo de páginas
    # ================
    if section == "🔍 Visión general":
        mod.pagina_vision_general(df_full)
    elif section == "🧪 Patrones y relación":
        mod.pagina_patrones(df_full)
    elif section == "🔮 Predicción":
        mod.pagina_prediccion(df_full)

# Notas ejecutivas
st.markdown("---")
st.subheader("🧾 Conclusiones ejecutivas (auto)")
st.markdown("""
- El **heatmap** permite detectar **picos de concentración** por rango de edad y prestación; usa **% por fila** para comparar dentro de cada grupo etario.
- El **Cramér’s V** orienta la **fuerza de asociación** entre edad y prestación (débil ~0.1, moderada ~0.3, fuerte ~0.5).
- Los **clusters de edad** ayudan a perfilar oferta, horarios y campañas por tramos.
- El **modelo baseline** da una primera brújula para **priorizar demanda** por edad y simular escenarios.
""")

st.subheader("🎯 Recomendaciones rápidas")
st.markdown("""
- **Agenda/Staffing:** asigna mayor oferta en los rangos con picos del heatmap.
- **Marketing:** segmenta campañas por los clusters de edad con mayor propensión.
- **Producto/Portafolio:** refuerza prestaciones con alta probabilidad por edad (ver simulador).
""")
