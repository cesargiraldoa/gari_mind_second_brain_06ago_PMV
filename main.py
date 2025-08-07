import streamlit as st
import pandas as pd
from datetime import date

from db_connection import get_sales_data, get_all_sales_data
import gari_analytics_edad_vs_prestacion as mod

st.set_page_config(page_title="GariMind – Edad vs Prestación", layout="wide")

st.title("🧠 GariMind CésarStyle™ – Edad vs Prestación")

# ==============================
# Sidebar / Navegación
# ==============================
st.sidebar.header("⚙️ Navegación")
section = st.sidebar.radio(
    "Secciones",
    ["🏁 Inicio (preview)", "🔍 Visión general", "🧪 Patrones y relación", "🔮 Predicción"],
    index=0
)

# ==============================
# Filtro de rango de fechas
# ==============================
st.sidebar.subheader("📅 Filtro por fecha")
use_filter = st.sidebar.checkbox("Filtrar por rango de fechas", value=False)
fecha_ini = fecha_fin = None
if use_filter:
    fecha_ini = st.sidebar.date_input("Fecha inicial", value=date(2024, 1, 1))
    fecha_fin = st.sidebar.date_input("Fecha final", value=date.today())

# ==============================
# Cache para cargas pesadas
# ==============================
@st.cache_data(show_spinner=False, ttl=600)
def load_full_data_cached(fecha_ini=None, fecha_fin=None):
    """Carga completa (todos los registros o filtrados) con cache."""
    df = get_all_sales_data(fecha_ini, fecha_fin)
    return df

# =======================================
# 1) Inicio: SOLO vista previa (TOP 10)
# =======================================
if section == "🏁 Inicio (preview)":
    st.subheader("Vista previa rápida (TOP 10) – no afecta el análisis")
    with st.spinner("Cargando vista previa…"):
        df_preview = get_sales_data()
    if isinstance(df_preview, pd.DataFrame) and not df_preview.empty and "error" not in df_preview.columns:
        st.dataframe(df_preview, use_container_width=True)
    else:
        st.error("No fue posible cargar la vista previa.")
        st.write(df_preview)
    st.info("➡️ Selecciona una pestaña de **análisis** en la izquierda para procesar **todos** los registros.")

# ======================================================
# 2) Secciones de análisis: usan TODOS o rango de fechas
# ======================================================
else:
    with st.spinner("Procesando datos para análisis…"):
        df_full = load_full_data_cached(fecha_ini, fecha_fin)

    if not isinstance(df_full, pd.DataFrame) or df_full.empty or ("error" in df_full.columns):
        st.error("No fue posible cargar la tabla. Revisa la conexión o logs.")
        st.write(df_full if isinstance(df_full, pd.DataFrame) else "Respuesta inesperada.")
    else:
        rango_txt = f" del {fecha_ini} al {fecha_fin}" if (fecha_ini and fecha_fin) else " (todos los registros)"
        st.success(f"✅ Datos cargados: N = {len(df_full):,} registros{rango_txt}")

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
- El **heatmap** usa **% por rango de edad** para ver concentración por prestación.
- **Cramér’s V** indica la fuerza de asociación Edad–Prestación (≈0.1 débil, ≈0.3 moderada, ≈0.5 fuerte).
- **Clusters de edad** perfilan oferta, horarios y campañas.
- El **modelo baseline** sirve para priorizar demanda por edad y simular escenarios.
""")
        st.subheader("🎯 Recomendaciones rápidas")
        st.markdown("""
- **Agenda/Staffing:** aumenta oferta donde el heatmap muestre picos por edad.
- **Marketing:** segmenta campañas por clusters de edad con mayor propensión.
- **Portafolio:** resalta prestaciones con alta probabilidad por edad (ver simulador).
""")
