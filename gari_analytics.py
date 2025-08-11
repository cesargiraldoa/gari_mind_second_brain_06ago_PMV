# gari_analytics.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
from db_connection import get_all_sales_data

# --- utilidades de detección de columnas ---
AGE_CANDIDATES = ["Edad", "edad", "Edad_Paciente", "Edad_Anos"]
DOB_CANDIDATES = ["Fecha_Nacimiento", "FechaNac", "Fec_Nac", "FecNacimiento", "FechaNac_Paciente"]
DATE_CANDIDATES = ["Fecha_Accion", "Fecha_Prestacion", "Fecha_Presupuesto", "Fecha", "fecha"]
PREST_CANDIDATES = ["Prestacion", "Prestación", "Prestacion_Principal", "Nombre_Prestacion"]
SEDE_CANDIDATES = ["Sucursal_pto", "Sede", "Clinica", "Sucursal", "Centro"]

def _pick_first(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
        # case-insensitive
        matches = [col for col in df.columns if col.lower() == c.lower()]
        if matches:
            return matches[0]
    return None

def _compute_age(df: pd.DataFrame, dob_col: str, ref_date_col: Optional[str]) -> pd.Series:
    dob = pd.to_datetime(df[dob_col], errors="coerce")
    if ref_date_col and ref_date_col in df.columns:
        ref = pd.to_datetime(df[ref_date_col], errors="coerce")
    else:
        ref = pd.Timestamp.today()
    age_years = (pd.to_datetime(ref) - dob).dt.days / 365.25
    return np.floor(age_years).astype("Int64")

def _build_bins(age: pd.Series) -> pd.Categorical:
    bins = [-1, 12, 17, 24, 34, 44, 54, 64, 120]
    labels = ["0–12", "13–17", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"]
    return pd.cut(age.clip(lower=0, upper=120), bins=bins, labels=labels)

def _top_n(series: pd.Series, n=12) -> List[str]:
    return series.value_counts().head(n).index.tolist()

def run_age_vs_prestacion():
    st.header("📈 Módulo: Edad vs Prestación")

    # --- Parámetros de carga ---
    with st.expander("Opciones de carga de datos", expanded=False):
        tabla = st.text_input("Tabla fuente", "Prestaciones_Temporal")
        c1, c2 = st.columns(2)
        desde = c1.date_input("Desde (opcional)", value=None)
        hasta = c2.date_input("Hasta (opcional)", value=None)
        date_force = st.text_input("Forzar columna de fecha (opcional)", value="")
        if st.button("Cargar datos (para análisis)"):
            st.session_state["_load_trigger"] = True

    if not st.session_state.get("_load_trigger"):
        st.info("Carga los datos para iniciar el análisis.")
        return

    df = get_all_sales_data(
        table_name=tabla.strip(),
        date_col=(date_force.strip() or None),
        date_from=(desde.strftime("%Y-%m-%d") if desde else None),
        date_to=(hasta.strftime("%Y-%m-%d") if hasta else None),
    )
    if df.empty:
        st.warning("No se obtuvieron filas con los filtros dados.")
        return

    st.success(f"Dataset cargado para análisis: {len(df):,} filas")

    # --- Detección de columnas clave ---
    prest_col = _pick_first(df, PREST_CANDIDATES)
    date_col  = date_force.strip() or _pick_first(df, DATE_CANDIDATES)
    sede_col  = _pick_first(df, SEDE_CANDIDATES)
    age_col   = _pick_first(df, AGE_CANDIDATES)
    dob_col   = _pick_first(df, DOB_CANDIDATES)

    if not prest_col:
        st.error("No pude detectar la columna de Prestación. Indícala manualmente.")
        prest_col = st.text_input("Columna de Prestación", value=prest_col or "")
        if not prest_col:
            return

    # --- Calcular edad ---
    if age_col and df[age_col].notna().any():
        edad = pd.to_numeric(df[age_col], errors="coerce")
    elif dob_col:
        edad = _compute_age(df, dob_col, date_col)
    else:
        st.warning("No se encontró columna de edad ni de fecha de nacimiento. Asignaré NaN.")
        edad = pd.Series([pd.NA]*len(df), dtype="Int64")

    df["_Edad"] = edad
    df["_Edad_Bin"] = _build_bins(df["_Edad"])

    # --- Seleccionar top de prestaciones para visualizar ---
    n_top = st.slider("Número de prestaciones a visualizar (Top N)", 5, 30, 12)
    top_prest = _top_n(df[prest_col].astype(str), n=n_top)
    dfx = df[df[prest_col].astype(str).isin(top_prest)].copy()

    # --- KPIs ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Edad promedio", f"{pd.to_numeric(dfx['_Edad'], errors='coerce').mean():.1f} años")
    k2.metric("Prestación más frecuente", dfx[prest_col].mode(dropna=True).iloc[0] if not dfx.empty else "—")
    if sede_col:
        top_sede = dfx[sede_col].mode(dropna=True).iloc[0] if not dfx.empty else "—"
        k3.metric("Sede dominante", top_sede)
    total_bins = dfx["_Edad_Bin"].notna().sum()
    k4.metric("Registros con edad", f"{total_bins:,}")

    # --- Heatmap (Edad bin vs Prestación) ---
    st.subheader("Mapa de calor: grupos de edad vs prestación (Top N)")
    pt = pd.pivot_table(
        dfx, index="_Edad_Bin", columns=prest_col, values=prest_col,
        aggfunc="count", fill_value=0
    ).astype(int)

    fig, ax = plt.subplots(figsize=(min(14, 2+0.6*len(pt.columns)), 6))
    im = ax.imshow(pt.values, aspect="auto")
    ax.set_yticks(range(len(pt.index))); ax.set_yticklabels(pt.index.astype(str))
    ax.set_xticks(range(len(pt.columns))); ax.set_xticklabels(pt.columns, rotation=45, ha="right")
    for i in range(pt.shape[0]):
        for j in range(pt.shape[1]):
            ax.text(j, i, f"{pt.values[i,j]:,}", ha="center", va="center", fontsize=8)
    ax.set_xlabel("Prestación (Top N)"); ax.set_ylabel("Grupo de edad")
    fig.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
    st.pyplot(fig, use_container_width=True)

    # --- Barras: distribución por edad de la prestación top ---
    st.subheader("Distribución por edad – prestación más frecuente")
    if not dfx.empty:
        prest_top = dfx[prest_col].mode(dropna=True).iloc[0]
        df_top = dfx[dfx[prest_col] == prest_top]
        dist = df_top["_Edad_Bin"].value_counts().sort_index()
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.bar(dist.index.astype(str), dist.values)
        ax2.set_xlabel("Grupo de edad"); ax2.set_ylabel("N° casos"); ax2.set_title(prest_top)
        st.pyplot(fig2, use_container_width=True)

    # --- Conclusiones automáticas ---
    st.subheader("🧠 Conclusiones automáticas")
    bullets = []

    # 1) grupo etario con más casos
    grp_counts = dfx["_Edad_Bin"].value_counts()
    if not grp_counts.empty:
        bullets.append(f"- El grupo etario con mayor volumen es **{grp_counts.idxmax()}** ({int(grp_counts.max()):,} registros).")

    # 2) prestación dominante por grupo etario
    top_by_age = (
        dfx.dropna(subset=["_Edad_Bin"])
           .groupby(["_Edad_Bin", prest_col])[prest_col]
           .count()
           .rename("n").reset_index()
           .sort_values(["_Edad_Bin", "n"], ascending=[True, False])
           .groupby("_Edad_Bin").head(1)
    )
    for _, row in top_by_age.iterrows():
        bullets.append(f"- En **{row['_Edad_Bin']}** predomina **{row[prest_col]}** (n={int(row['n']):,}).")

    # 3) edad promedio por prestación top
    mean_age = (
        dfx.dropna(subset=["_Edad"])
           .groupby(prest_col)["_Edad"]
           .mean()
           .sort_values(ascending=False)
           .head(5)
    )
    if not mean_age.empty:
        bullets.append("- **Prestaciones con mayor edad promedio**: " +
                       ", ".join([f"{k} ({v:.1f})" for k, v in mean_age.items()]))

    if bullets:
        st.markdown("\n".join(bullets))
    else:
        st.info("No fue posible generar conclusiones con los datos disponibles.")
