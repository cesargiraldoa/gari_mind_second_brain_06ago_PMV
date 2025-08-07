# gari_analytics_edad_vs_prestacion.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

def render_edad_vs_prestacion(df: pd.DataFrame, titulo="📊 Análisis Edad vs Prestación"):
    st.header(titulo)

    # ------- helpers -------
    def pick_col(posibles):
        m = {c.lower(): c for c in df.columns}
        for p in posibles:
            for k, v in m.items():
                if p in k:
                    return v
        return None

    # ------- detectar columnas clave -------
    col_fnac   = pick_col(["fechanac", "fecha_nac", "fechanacimiento", "fecha nacimiento"])
    col_prest  = pick_col(["prestacion", "prestación", "proced", "servicio"])
    col_genero = pick_col(["sexo", "genero", "género"])
    col_ciud   = pick_col(["ciudad", "municipio", "localidad", "sede", "sucursal"])

    if not col_fnac or not col_prest:
        st.error(f"Faltan columnas clave. Fecha nac.: {col_fnac} · Prestación: {col_prest}")
        return

    # ------- preparar datos -------
    dfx = df.copy()
    dfx[col_fnac] = pd.to_datetime(dfx[col_fnac], errors="coerce")
    dfx["edad"] = dfx[col_fnac].apply(lambda x: date.today().year - x.year if pd.notnull(x) else None)
    dfx = dfx.dropna(subset=["edad", col_prest])
    dfx = dfx[dfx["edad"].between(0, 110)]
    dfx[col_prest] = dfx[col_prest].astype(str).str.strip()

    # ------- filtros -------
    with st.expander("⚙️ Filtros"):
        top_n = st.slider("Top prestaciones a analizar", 10, 100, 30, 5)
        gen_sel = st.multiselect("Género", sorted(dfx[col_genero].dropna().unique())) if col_genero else []
        ciu_sel = st.multiselect("Ciudad/Sede", sorted(dfx[col_ciud].dropna().unique())) if col_ciud else []
    if col_genero and gen_sel:
        dfx = dfx[dfx[col_genero].isin(gen_sel)]
    if col_ciud and ciu_sel:
        dfx = dfx[dfx[col_ciud].isin(ciu_sel)]

    # ------- bins y top prestaciones -------
    bins = list(range(0, 111, 5))  # rangos de 5 años
    dfx["rango_edad"] = pd.cut(dfx["edad"], bins=bins, right=False)
    top_prest = dfx[col_prest].value_counts().head(top_n).index
    d_top = dfx[dfx[col_prest].isin(top_prest)]

    # ------- heatmap -------
    st.subheader("🔶 Heatmap rango de edad × prestación (Top)")
    tabla = pd.crosstab(d_top["rango_edad"], d_top[col_prest]).sort_index()
    st.dataframe(
        tabla.style.background_gradient(cmap="OrRd").format("{:,}"),
        use_container_width=True
    )

    # ------- distribuciones -------
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Distribución por prestación (Top)**")
        st.bar_chart(d_top[col_prest].value_counts())

    with colB:
        st.markdown("**Distribución por rangos de edad**")
        dist_edad = dfx["rango_edad"].value_counts().sort_index()
        # 🔧 clave: convertir IntervalIndex -> str
        dist_edad.index = dist_edad.index.astype(str)
        st.bar_chart(dist_edad)

    # ------- perfil por prestación -------
    st.markdown("**🎯 Perfil de edad por prestación seleccionada**")
    sel = st.selectbox("Prestación", list(top_prest))
    d_sel = dfx[dfx[col_prest] == sel]["rango_edad"].value_counts().sort_index()
    d_sel.index = d_sel.index.astype(str)  # 🔧 convertir etiquetas a texto
    st.bar_chart(d_sel)

    # ------- KPIs rápidos -------
    k1, k2, k3 = st.columns(3)
    k1.metric("Registros válidos", f"{len(dfx):,}")
    k2.metric("Prestaciones analizadas (Top)", f"{len(top_prest):,}")
    k3.metric("Rangos de edad", f"{tabla.shape[0]:,}")

    # ------- conclusiones automáticas -------
    st.subheader("📝 Conclusiones automáticas")
    insights = []

    # Dominante por rango
    for rng, sub in d_top.groupby("rango_edad"):
        if not sub.empty:
            pmax = sub[col_prest].value_counts().idxmax()
            insights.append(f"En {rng} domina **{pmax}**.")

    # Top global
    vc = d_top[col_prest].value_counts()
    if len(vc) >= 2:
        insights.append(f"Top global: **{vc.index[0]}** ({vc.iloc[0]}) y **{vc.index[1]}** ({vc.iloc[1]}).")
    elif len(vc) == 1:
        insights.append(f"Top global: **{vc.index[0]}** ({vc.iloc[0]}).")

    if col_genero:
        g_split = dfx.groupby(col_genero)[col_prest].apply(lambda s: s.value_counts().head(1))
        try:
            for g, row in g_split.groupby(level=0):
                prest_top = row.index.get_level_values(1)[0]
                count = int(row.values[0])
                insights.append(f"En **{g}** la prestación líder es **{prest_top}** ({count}).")
        except Exception:
            pass

    if insights:
        for i in insights:
            st.markdown(f"- {i}")
    else:
        st.info("No se generaron conclusiones con los filtros actuales.")

# Permite ejecutar el archivo solo para pruebas locales
if __name__ == "__main__":
    st.write("Este módulo está pensado para ser importado desde la app principal.")
