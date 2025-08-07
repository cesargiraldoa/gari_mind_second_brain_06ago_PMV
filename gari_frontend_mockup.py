
import streamlit as st

from db_connection import get_sales_data

st.set_page_config(page_title="GariMind Second Brain – CésarStyle™", layout="wide")
st.sidebar.title("🧠 GariMind Menu")

menu = st.sidebar.radio("Navegación principal", [
    "🧲 Daily Magnet – Scroll Narrativo (Real)",
    "🔍 Gari Analytics",
    "🧪 Explorador SQL",
    "🧲 Daily Magnet – Scroll Narrativo (Mockup)",
    "🧠 Boss Journal",
    "📦 Módulo BIC3",
    "📈 Inteligencia Comercial",
    "📊 Análisis Técnico Validado",
    "📋 Proyectos y Tareas",
    "🧬 Gari & César Lab (IA)",
    "💾 Memoria Empresarial",
    "🎁 Frase de Bondad Diaria"
])

st.title("🧠 GariMind Second Brain – CésarStyle™")

if menu == "🧲 Daily Magnet – Scroll Narrativo (Real)":
    st.subheader("🧲 Daily Magnet – Conexión a Base de Datos (main.py)")
    df = get_sales_data()
    if df is not None and not df.empty:
        if "error" in df.columns:
            st.error(f"Error al consultar datos: {df['error'][0]}")
        else:
            st.dataframe(df.head(10))
    else:
        st.warning("⚠️ Consulta sin resultados o error silencioso.")

elif menu == "🔍 Gari Analytics":
    st.subheader("🔍 Gari Analytics")
    st.write("Módulo de análisis de datos avanzados con visualizaciones dinámicas.")

elif menu == "🧪 Explorador SQL":
    st.subheader("🧪 Explorador SQL")
    st.write("Consulta directa a la base de datos con lenguaje natural o SQL.")

elif menu == "🧲 Daily Magnet – Scroll Narrativo (Mockup)":
    st.subheader("🧲 Daily Magnet – Scroll Narrativo")
    st.write("Resumen diario con narrativa de decisiones, aprendizajes y métricas destacadas.")

elif menu == "🧠 Boss Journal":
    st.subheader("🧠 Boss Journal")
    st.write("Diario ejecutivo por áreas. Registro automatizado y consultivo.")

elif menu == "📦 Módulo BIC3":
    st.subheader("📦 Módulo BIC3")
    st.write("Diagnóstico estratégico por bloques. Integración con documentos y análisis IA.")

elif menu == "📈 Inteligencia Comercial":
    st.subheader("📈 Inteligencia Comercial")
    st.write("Proyecciones, oportunidades y simuladores financieros por zona o canal.")

elif menu == "📊 Análisis Técnico Validado":
    st.subheader("📊 Análisis Técnico Validado")
    st.write("Diagnóstico técnico con evidencia visual y comparativa.")

elif menu == "📋 Proyectos y Tareas":
    st.subheader("📋 Proyectos y Tareas")
    st.write("Gestión de tareas, agenda y proyectos con integración a calendario.")

elif menu == "🧬 Gari & César Lab (IA)":
    st.subheader("🧬 Gari & César Lab (IA)")
    st.write("Módulo de desarrollo de IA personalizado. Modelos, pruebas, algoritmos.")

elif menu == "💾 Memoria Empresarial":
    st.subheader("💾 Memoria Empresarial")
    st.write("Recuerdos y conocimiento organizado por empresa, persona o tema.")

elif menu == "🎁 Frase de Bondad Diaria":
    st.subheader("🎁 Frase de Bondad Diaria – CésarStyle™")
    st.write("Frase inspiradora del día + acción bondadosa sugerida + termómetro de bondad.")
