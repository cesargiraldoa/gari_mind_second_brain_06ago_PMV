import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from db_connection import get_prestaciones  # función que trae todos los datos

st.set_page_config(page_title="📊 Análisis Edad vs Prestación", layout="wide")
st.title("📊 Análisis Edad vs Prestación – GariMind CésarStyle™")

# ========================
# 1️⃣ Carga de datos
# ========================
@st.cache_data(ttl=900, show_spinner="Cargando datos de Prestaciones_Temporal…")
def cargar_datos():
    return get_prestaciones(limit=None)

df = cargar_datos()
st.success(f"Datos cargados: {len(df):,} filas y {len(df.columns)} columnas.")

# ========================
# 2️⃣ Identificación de columnas clave
# ========================
def pick_col(posibles):
    cols = {c.lower(): c for c in df.columns}
    for p in posibles:
        for c_low, c_real in cols.items():
            if p in c_low:
                return c_real
    return None

col_fnac = pick_col(["fechanac", "fecha_nac", "fechanacimiento", "fecha nacimiento"])
col_prest = pick_col(["prestacion", "prestación", "proced", "servicio"])
col_genero = pick_col(["sexo", "genero", "género"])
col_ciudad = pick_col(["ciudad", "municipio", "localidad"])

if not col_fnac or not col_prest:
    st.error(f"No encontré columnas para fecha de nacimiento ({col_fnac}) o prestación ({col_prest})")
    st.stop()

# ========================
# 3️⃣ Preparación de datos
# ========================
df[col_fnac] = pd.to_datetime(df[col_fnac], errors="coerce")
df["edad"] = df[col_fnac].apply(lambda x: date.today().year - x.year if pd.notnull(x) else None)
df = df.dropna(subset=["edad", col_prest])
df = df[df["edad"].between(0, 110)]

# ========================
# 4️⃣ Filtros interactivos
# ========================
with st.sidebar:
    st.header("Filtros")
    top_n = st.slider("Top prestaciones", 5, 50, 20, 5)
    if col_genero:
        genero_sel = st.multiselect("Filtrar por género", df[col_genero].dropna().unique().tolist())
    else:
        genero_sel = []
    if col_ciudad:
        ciudad_sel = st.multiselect("Filtrar por ciudad", df[col_ciudad].dropna().unique().tolist())
    else:
        ciudad_sel = []

df_f = df.copy()
if genero_sel:
    df_f = df_f[df_f[col_genero].isin(genero_sel)]
if ciudad_sel:
    df_f = df_f[df_f[col_ciudad].isin(ciudad_sel)]

# ========================
# 5️⃣ Análisis descriptivo
# ========================
bins = list(range(0, 111, 5))
df_f["rango_edad"] = pd.cut(df_f["edad"], bins=bins, right=False)
top_prest = df_f[col_prest].value_counts().head(top_n).index
df_top = df_f[df_f[col_prest].isin(top_prest)]

st.subheader("🔶 Heatmap rango de edad × prestación")
tabla = pd.crosstab(df_top["rango_edad"], df_top[col_prest]).sort_index()
st.dataframe(tabla.style.background_gradient(cmap="OrRd").format("{:,}"), use_container_width=True)

st.subheader("🔷 Distribución por prestación (Top)")
st.bar_chart(df_top[col_prest].value_counts())

st.subheader("🔹 Distribución por rangos de edad")
st.bar_chart(df_f["rango_edad"].value_counts().sort_index())

# ========================
# 6️⃣ Conclusiones automáticas
# ========================
st.header("📝 Conclusiones automáticas")
insights = []

# Prestación más común por grupo de edad
for rango, subdf in df_top.groupby("rango_edad"):
    if not subdf.empty:
        prest_max = subdf[col_prest].value_counts().idxmax()
        insights.append(f"En el rango {rango}, la prestación más frecuente es **{prest_max}**.")

# Crecimientos/disminuciones (requiere comparar periodos)
# Placeholder: si hay fecha de prestación en datos, aquí se haría el análisis temporal.

if insights:
    for i in insights:
        st.markdown(f"- {i}")
else:
    st.info("No se generaron conclusiones automáticas con los filtros actuales.")

# ========================
# 7️⃣ Modelo predictivo (placeholder)
# ========================
st.header("🤖 Modelo predictivo (en desarrollo)")
st.markdown("""
Este módulo permitirá, a partir de variables como edad, género y ciudad, predecir la probabilidad de que un paciente reciba una prestación específica.
Servirá para:
- Campañas preventivas
- Sugerencias de tratamiento
- Planificación de capacidad
""")

# ========================
# 8️⃣ Exportación
# ========================
st.subheader("📤 Exportar datos y resultados")
st.download_button(
    "Descargar datos filtrados (CSV)",
    data=df_f.to_csv(index=False).encode("utf-8"),
    file_name="prestaciones_filtradas.csv",
    mime="text/csv"
)
st.download_button(
    "Descargar tabla heatmap (CSV)",
    data=tabla.to_csv().encode("utf-8"),
    file_name="heatmap_edad_prestacion.csv",
    mime="text/csv"
)
