# --- al inicio del archivo ---
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

def render_edad_vs_prestacion(df: pd.DataFrame, titulo="📊 Análisis Edad vs Prestación"):
    st.header(titulo)

    # detectar columnas
    def pick_col(posibles):
        m = {c.lower(): c for c in df.columns}
        for p in posibles:
            for k,v in m.items():
                if p in k: return v
        return None

    col_fnac  = pick_col(["fechanac", "fecha_nac", "fechanacimiento", "fecha nacimiento"])
    col_prest = pick_col(["prestacion", "prestación", "proced", "servicio"])
    col_genero= pick_col(["sexo","genero","género"])
    col_ciud  = pick_col(["ciudad","municipio","localidad"])

    if not col_fnac or not col_prest:
        st.error(f"Faltan columnas clave. Fecha nac.: {col_fnac} · Prestación: {col_prest}")
        return

    # preparar
    dfx = df.copy()
    dfx[col_fnac] = pd.to_datetime(dfx[col_fnac], errors="coerce")
    dfx["edad"] = dfx[col_fnac].apply(lambda x: date.today().year - x.year if pd.notnull(x) else None)
    dfx = dfx.dropna(subset=["edad", col_prest])
    dfx = dfx[dfx["edad"].between(0,110)]

    # Filtros
    with st.expander("⚙️ Filtros"):
        top_n = st.slider("Top prestaciones a analizar", 10, 100, 30, 5)
        gen_sel = st.multiselect("Género", sorted(dfx[col_genero].dropna().unique())) if col_genero else []
        ciu_sel = st.multiselect("Ciudad", sorted(dfx[col_ciud].dropna().unique())) if col_ciud else []
    if col_genero and gen_sel: dfx = dfx[dfx[col_genero].isin(gen_sel)]
    if col_ciud and ciu_sel:   dfx = dfx[dfx[col_ciud].isin(ciu_sel)]

    # bins & top
    bins = list(range(0,111,5))
    dfx["rango_edad"] = pd.cut(dfx["edad"], bins=bins, right=False)
    top_prest = dfx[col_prest].value_counts().head(top_n).index
    d_top = dfx[dfx[col_prest].isin(top_prest)]

    # Heatmap
    st.subheader("🔶 Heatmap rango de edad × prestación (Top)")
    tabla = pd.crosstab(d_top["rango_edad"], d_top[col_prest]).sort_index()
    st.dataframe(tabla.style.background_gradient(cmap="OrRd").format("{:,}"), use_container_width=True)

    # Distribuciones
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Distribución por prestación (Top)**")
        st.bar_chart(d_top[col_prest].value_counts())
    with colB:
        st.markdown("**Distribución por rangos de edad**")
        st.bar_chart(dfx["rango_edad"].value_counts().sort_index())

    # Perfil por prestación
    st.markdown("**🎯 Perfil de edad por prestación seleccionada**")
    sel = st.selectbox("Prestación", list(top_prest))
    st.bar_chart(dfx[dfx[col_prest]==sel]["rango_edad"].value_counts().sort_index())

    # Conclusiones automáticas
    st.subheader("📝 Conclusiones automáticas")
    insights = []
    for rng, sub in d_top.groupby("rango_edad"):
        if not sub.empty:
            pmax = sub[col_prest].value_counts().idxmax()
            insights.append(f"En {rng} domina **{pmax}**.")
    if len(top_prest) >= 2:
        primeras = d_top[col_prest].value_counts().nlargest(2)
        insights.append(f"Top prestaciones globales: **{primeras.index[0]}** y **{primeras.index[1]}**.")

    if insights: 
        for i in insights: st.markdown(f"- {i}")
    else:
        st.info("No se generaron conclusiones con los filtros actuales.")

# --- mantener abajo tu main opcional para ejecución directa ---
if __name__ == "__main__":
    st.write("Este módulo está pensado para ser importado desde la app principal.")
