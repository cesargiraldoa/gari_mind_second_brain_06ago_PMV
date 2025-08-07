# main.py
import streamlit as st
import pandas as pd

# Conexión y utilidades
from db_connection import (
    list_tables_like,
    get_sales_data,     # carga una tabla por nombre (opcional TOP n)
    get_prestaciones,   # carga Prestaciones_Temporal completa (o limit)
)

# Módulo de analítica (función reutilizable)
from gari_analytics_edad_vs_prestacion import render_edad_vs_prestacion

# ----------------------------
# Configuración general
# ----------------------------
st.set_page_config(page_title="GariMind Second Brain – CésarStyle™", layout="wide")
st.sidebar.title("GariMind Menu")

menu = st.sidebar.radio(
    "Navegación principal",
    [
        "🧲 Daily Magnet – Conexión a Base de Datos",
        "📊 Análisis Edad vs Prestación",
    ],
)

# =========================================================
# Opción 1: Daily Magnet (Explorador + Auto-análisis)
# =========================================================
if menu == "🧲 Daily Magnet – Conexión a Base de Datos":
    st.title("🧲 Daily Magnet – Conexión a Base de Datos (pymssql)")

    # ---------- Sidebar ----------
    with st.sidebar:
        st.subheader("⚙️ Parámetros")
        tablas = list_tables_like() or []
        default_idx = next((i for i, t in enumerate(tablas) if "Prestaciones_Temporal" in t), 0) if tablas else 0
        tabla_sel = st.selectbox("Tabla origen", tablas, index=default_idx if tablas else 0)
        traer_top = st.checkbox("Traer solo muestra TOP 10 (debug rápido)", value=False)

    @st.cache_data(ttl=900, show_spinner="Cargando datos desde SQL Server…")
    def cargar(tabla, solo_top):
        # tabla viene como [schema].[name]; nos quedamos con el nombre
        nombre = tabla.split("].")[-1].replace("]", "").replace("[", "") if tabla else "Prestaciones_Temporal"
        return get_sales_data(table=nombre, top=10 if solo_top else None)

    # ---------- Botones ----------
    col1, col2 = st.columns([1, 1])
    with col1:
        cargar_btn = st.button("📥 Cargar datos", use_container_width=True)
    with col2:
        limpiar_btn = st.button("🧹 Limpiar datos", use_container_width=True)

    if cargar_btn:
        try:
            df = cargar(tabla_sel, traer_top)
            st.session_state["daily_df"] = df
            st.success(f"Datos cargados: {len(df):,} filas · {len(df.columns)} columnas.")
        except Exception as e:
            st.error("Error conectando o trayendo datos.")
            st.exception(e)

    if limpiar_btn:
        st.session_state.pop("daily_df", None)
        cargar.clear()
        st.info("Cache y memoria limpiadas.")

    st.divider()

    # ---------- Vista general ----------
    df = st.session_state.get("daily_df")
    if isinstance(df, pd.DataFrame) and not df.empty:
        st.subheader("📊 Vista general")
        st.dataframe(df.head(100), use_container_width=True)
        st.caption(f"Columnas: {list(df.columns)}")

        # ====== AUTO-ANÁLISIS cuando la tabla es Prestaciones_Temporal ======
        nombre_tabla = tabla_sel if isinstance(tabla_sel, str) else str(tabla_sel)
        if "Prestaciones_Temporal" in nombre_tabla:
            st.markdown("---")
            st.markdown("### 🔎 Análisis automático detectado para `Prestaciones_Temporal`")
            try:
                render_edad_vs_prestacion(df, titulo="📊 Análisis Edad vs Prestación (auto)")
            except Exception as e:
                st.error("No se pudo renderizar el análisis automático.")
                st.exception(e)
    else:
        st.info("Selecciona una tabla y pulsa **Cargar datos**.")

# =========================================================
# Opción 2: Módulo dedicado (usa todos los datos siempre)
# =========================================================
elif menu == "📊 Análisis Edad vs Prestación":
    st.title("📊 Análisis Edad vs Prestación – Módulo dedicado")
    try:
        # Trae TODOS los datos de dbo.Prestaciones_Temporal
        df = get_prestaciones(limit=None)
        render_edad_vs_prestacion(df, titulo="📊 Análisis Edad vs Prestación (Prestaciones_Temporal)")
    except Exception as e:
        st.error("No se pudo cargar el módulo de análisis.")
        st.exception(e)
