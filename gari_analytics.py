import streamlit as st
import pandas as pd
import numpy as np

from data_loader import fetch_preview, fetch_all

try:
    import plotly.express as px
except Exception:
    px = None  # seguimos sin fallar

# -----------------------------
# Utilidades de detección
# -----------------------------
AGE_CANDIDATES = ["Edad", "EdadPaciente", "Edad_paciente", "EDAD", "edad"]
PREST_CANDIDATES = ["Prestacion", "Prestación", "Especialidad", "Servicio", "Categoria", "Categoría"]
DATE_CANDIDATES = [
    "Fecha_Presupuesto","FechaPrestacion","Fecha_Prestacion","FechaAtencion",
    "Fecha_Atencion","FechaServicio","Fecha_Servicio","Fecha","fecha"
]
SITE_CANDIDATES = ["Sucursal","Sede","Clinica","Clínica","Sucursal_ppto","Sucursal_prest","ROMA","KENNEDY"]
VALUE_CANDIDATES = ["Valor","ValorVenta","Valor_Venta","Total","Num_Presupuesto","NumPresupuesto"]

def pick_col(candidates, cols):
    for c in candidates:
        if c in cols:
            return c
    return None

def clean_age(series):
    s = pd.to_numeric(series, errors="coerce")
    return s.clip(lower=0, upper=120).astype("Int64")

def age_bins():
    edges = [0,10,20,30,40,50,60,70,80,120]
    labels = [f"{edges[i]}–{edges[i+1]-1}" for i in range(len(edges)-1)]
    return edges, labels

# -----------------------------
# Página principal del módulo
# -----------------------------
def main():
    st.title("🧠 GariMind CésarStyle™ – Edad vs Prestación")

    # --------- Sidebar (filtro por fecha, sin mostrar todos los registros) ---------
    st.sidebar.markdown("## Navegación")
    section = st.sidebar.radio("Secciones", ["🏁 Inicio (preview)", "📊 Visión general", "🧩 Patrones y relación", "🤖 Predicción (beta)"])

    st.sidebar.markdown("## Filtro por fecha")
    use_date = st.sidebar.checkbox("Filtrar por rango de fechas")
    forced_date_col = st.sidebar.text_input("Forzar columna de fecha (opcional)", value="")
    date_range = None
    if use_date:
        c1, c2 = st.sidebar.columns(2)
        start = c1.date_input("Desde")
        end = c2.date_input("Hasta")
        if start and end:
            date_range = (pd.to_datetime(start), pd.to_datetime(end) + pd.Timedelta(days=1))

    # --------- Preview rápido (siempre muestra muestra, nunca todo) ---------
    if section == "🏁 Inicio (preview)":
        with st.spinner("Cargando muestra…"):
            dfp = fetch_preview(10)
        st.dataframe(dfp, use_container_width=True, height=350)
        st.info("Esta tabla es SOLO una muestra. Los análisis de las otras pestañas usan **todos** los registros, sin mostrarlos en tabla.")
        return

    # --------- Carga completa solo para análisis ---------
    with st.status("Cargando y procesando todos los registros…", expanded=True) as status:
        st.write("1/4 ↪️ Descargando datos completos (sin renderizar tabla)…")
        df = fetch_all(date_col=(forced_date_col.strip() or None), date_range=date_range)

        st.write("2/4 🧹 Detección de columnas clave…")
        cols = df.columns.tolist()
        age_col   = pick_col(AGE_CANDIDATES, cols)
        prest_col = pick_col(PREST_CANDIDATES, cols)
        date_col  = (forced_date_col.strip() or pick_col(DATE_CANDIDATES, cols))
        site_col  = pick_col(SITE_CANDIDATES, cols)
        val_col   = pick_col(VALUE_CANDIDATES, cols)

        missing = []
        if age_col is None:   missing.append("Edad")
        if prest_col is None: missing.append("Prestación/Especialidad")
        if missing:
            st.error(f"No se detectaron columnas obligatorias: {', '.join(missing)}. Revisa nombres o ajusta listas de candidatos.")
            status.update(state="error")
            return

        st.write(f"- Edad: **{age_col}** | Prestación: **{prest_col}** | Fecha: **{date_col or '—'}** | Sucursal: **{site_col or '—'}** | Valor: **{val_col or '—'}**")

        st.write("3/4 🔎 Preprocesando…")
        df = df.copy()
        df[age_col] = clean_age(df[age_col])
        edges, labels = age_bins()
        df["_age_bin"] = pd.cut(df[age_col], bins=edges, labels=labels, right=False)

        # Tableros derivados (no se renderizan tablas completas)
        st.write("4/4 📈 Calculando agregados…")
        by_prest = df.groupby(prest_col, dropna=True).size().sort_values(ascending=False).rename("conteo")
        by_age_prest = (df.groupby(["_age_bin", prest_col]).size()
                        .reset_index(name="n")
                        .pivot(index="_age_bin", columns=prest_col, values="n").fillna(0))

        # Valores por prestación (si existe valor)
        by_value = None
        if val_col and val_col in df.columns:
            by_value = df.groupby(prest_col)[val_col].sum().sort_values(ascending=False)

        status.update(label="Datos listos ✅", state="complete")

    # --------- Secciones de análisis (siempre usando df completo) ---------
    if section == "📊 Visión general":
        st.subheader("Top prestaciones por volumen")
        top_n = st.slider("Mostrar top N", min_value=5, max_value=20, value=10, step=1)
        top_series = by_prest.head(top_n)

        if px:
            fig = px.bar(
                top_series.reset_index().rename(columns={prest_col: "Prestación", "conteo": "Casos"}),
                x="Prestación", y="Casos", title="Volumen por Prestación (todos los registros)"
            )
            fig.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(top_series)

        if by_value is not None:
            st.subheader("Top prestaciones por valor")
            topv = by_value.head(top_n)
            if px:
                figv = px.bar(
                    topv.reset_index().rename(columns={prest_col: "Prestación", val_col: "Valor"}),
                    x="Prestación", y="Valor", title="Valor agregado por Prestación (todos los registros)"
                )
                figv.update_layout(xaxis_title="", yaxis_title="")
                st.plotly_chart(figv, use_container_width=True)
            else:
                st.bar_chart(topv)

        # Conclusiones ejecutivas rápidas
        st.markdown("### 📝 Conclusiones automáticas")
        bullets = []
        p1, v1 = (top_series.index[0], int(top_series.iloc[0])) if not top_series.empty else ("—", 0)
        bullets.append(f"- **Líder en volumen:** {p1} con **{v1}** casos.")
        if by_value is not None and not by_value.empty:
            p2, v2 = by_value.index[0], float(by_value.iloc[0])
            bullets.append(f"- **Líder en valor:** {p2} (≈ {v2:,.0f}).")
        # Edad dominante por prestación líder
        if not df[df[prest_col] == p1].empty:
            major = (df[df[prest_col] == p1]
                     .groupby("_age_bin").size().sort_values(ascending=False))
            if not major.empty:
                bullets.append(f"- En **{p1}** domina el rango de edad **{major.index[0]}**.")
        st.markdown("\n".join(bullets))

    elif section == "🧩 Patrones y relación":
        st.subheader("Heatmap Edad × Prestación (conteos)")
        # Heatmap corporativo
        if px:
            fig = px.imshow(
                by_age_prest.values,
                labels=dict(x="Prestación", y="Rango de edad", color="Casos"),
                x=by_age_prest.columns, y=by_age_prest.index,
                aspect="auto", title="Distribución de casos por edad y prestación (todos los registros)"
            )
            fig.update_layout(margin=dict(t=60, b=30, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(by_age_prest, use_container_width=True)

        # Insight: para cada rango, la prestación dominante
        st.markdown("### 🧠 Insight por rango de edad")
        dom = by_age_prest.idxmax(axis=1).rename("Prestación dominante")
        st.dataframe(dom.to_frame(), use_container_width=True, height=300)

        # Conclusiones
        st.markdown("### 📝 Conclusiones")
        insights = []
        for age_rng, prest_dom in dom.items():
            if pd.isna(prest_dom): 
                continue
            value = int(by_age_prest.loc[age_rng, prest_dom])
            insights.append(f"- En **{age_rng}** predomina **{prest_dom}** (≈ {value} casos).")
        if insights:
            st.markdown("\n".join(insights))
        else:
            st.info("No se hallaron patrones dominantes claros con los datos actuales.")

    elif section == "🤖 Predicción (beta)":
        st.caption("Entrena un modelo simple (opcional). No muestra registros; usa todo el dataset internamente.")
        run = st.button("Entrenar modelo base (clasificar prestación por edad)")
        if run:
            try:
                from sklearn.model_selection import train_test_split
                from sklearn.preprocessing import LabelEncoder
                from sklearn.metrics import accuracy_score
                from sklearn.linear_model import LogisticRegression

                y = df[prest_col].astype(str)
                X = pd.DataFrame({"edad": df[age_col].astype("float").fillna(-1.0)})

                # encoder de etiqueta
                le = LabelEncoder()
                y_enc = le.fit_transform(y)

                X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)
                clf = LogisticRegression(max_iter=1000, n_jobs=None)
                clf.fit(X_train, y_train)
                pred = clf.predict(X_test)
                acc = accuracy_score(y_test, pred)

                st.success(f"Exactitud base: **{acc*100:.2f}%** (solo con edad).")
                st.caption("⚠️ Es un baseline. Mejora al agregar variables: sucursal, valor, convenios, fechas, etc.")
            except ModuleNotFoundError:
                st.error("Falta `scikit-learn` en el entorno. Si deseas, lo agregamos a `requirements.txt` y volvemos a entrenar.")
            except Exception as e:
                st.error(f"Error durante el entrenamiento: {e}")
