import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression

# =========================
# Utilidades de detección
# =========================
def _guess_column(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    # también buscar por normalización básica (sin acentos / minúsculas)
    norm = {col.lower().replace("ó","o").replace("á","a").replace("é","e").replace("í","i").replace("ú","u"): col for col in df.columns}
    for c in candidates:
        key = c.lower().replace("ó","o").replace("á","a").replace("é","e").replace("í","i").replace("ú","u")
        if key in norm:
            return norm[key]
    return None

def detectar_columnas(df: pd.DataFrame):
    # Prestación
    prest_candidates = [
        "Prestacion","Prestación","TipoPrestacion","Tipo_Prestacion","Tipo de Prestacion",
        "Prestaciones","Servicio","Procedimiento","CUPS","CodigoCUPS","NombrePrestacion"
    ]
    col_prest = _guess_column(df, prest_candidates)

    # Edad directa
    edad_candidates = ["Edad","EDAD","edad"]
    col_edad = _guess_column(df, edad_candidates)

    # Fechas para calcular edad si no hay columna 'Edad'
    fecha_nac_candidates = ["FechaNacimiento","Fecha_Nacimiento","Fec_Nacimiento","Fecha de Nacimiento","FNacimiento"]
    fecha_ref_candidates = ["FechaPrestacion","Fecha_Atencion","FechaAtencion","Fecha","Fecha_Servicio","FAtencion"]

    col_fnac = _guess_column(df, fecha_nac_candidates)
    col_fref = _guess_column(df, fecha_ref_candidates)

    return col_prest, col_edad, col_fnac, col_fref

def calcular_edad(df: pd.DataFrame, col_edad, col_fnac, col_fref):
    if col_edad and pd.api.types.is_numeric_dtype(df[col_edad]):
        return df[col_edad].astype(float)

    # intentar calcular por fechas
    if col_fnac and col_fref:
        fn = pd.to_datetime(df[col_fnac], errors="coerce")
        fr = pd.to_datetime(df[col_fref], errors="coerce")
        edad = (fr - fn).dt.days / 365.25
        return edad

    # fallback: si hay solo fecha de nacimiento, calcular contra hoy (menos ideal)
    if col_fnac:
        fn = pd.to_datetime(df[col_fnac], errors="coerce")
        hoy = pd.Timestamp.now(tz=None)
        edad = (hoy - fn).dt.days / 365.25
        return edad

    return pd.Series([np.nan]*len(df))

def binar_edad(edad_series: pd.Series, esquema="Décadas"):
    edad = edad_series.copy()
    edad = edad.clip(lower=0, upper=110)  # limpiar outliers extremos

    if esquema == "Décadas":
        bins = [0, 19, 29, 39, 49, 59, 69, 79, 200]
        labels = ["<20","20-29","30-39","40-49","50-59","60-69","70-79","80+"]
    elif esquema == "Quintiles":
        try:
            q = edad[edad.notna()].quantile([0,0.2,0.4,0.6,0.8,1.0]).values
            bins = sorted(list(dict.fromkeys(q)))  # asegurar únicos
            if len(bins) < 3:  # data rara → fallback
                return binar_edad(edad, "Décadas")
            labels = [f"Q{i+1}" for i in range(len(bins)-1)]
        except Exception:
            return binar_edad(edad, "Décadas")
    else:
        # Personalizado: décadas por defecto
        return binar_edad(edad, "Décadas")

    return pd.cut(edad, bins=bins, labels=labels, include_lowest=True, right=True)

# =========================
# Vistas / Gráficos
# =========================
def heatmap_edad_prestacion(df: pd.DataFrame, col_prest: str, edad_bin: pd.Series):
    tabla = pd.crosstab(edad_bin, df[col_prest], dropna=False)
    # Normalización por fila (%) para lectura visual más potente
    tabla_pct = tabla.div(tabla.sum(axis=1), axis=0).fillna(0) * 100

    fig = px.imshow(
        tabla_pct.values,
        labels=dict(x="Prestación", y="Rango de edad", color="% dentro del rango"),
        x=tabla_pct.columns.astype(str),
        y=tabla_pct.index.astype(str),
        aspect="auto",
        color_continuous_scale="Turbo",
        text_auto=".1f",
    )
    fig.update_traces(colorbar=dict(title="%"))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_showgrid=False, yaxis_showgrid=False,
        xaxis_tickangle=45
    )
    return fig, tabla, tabla_pct

def resumen_descriptivo(edad: pd.Series, df: pd.DataFrame, col_prest: str):
    desc = {
        "n_registros": int(edad.notna().sum()),
        "edad_min": float(np.nanmin(edad)),
        "edad_max": float(np.nanmax(edad)),
        "edad_media": float(np.nanmean(edad)),
        "edad_mediana": float(np.nanmedian(edad)),
        "edad_std": float(np.nanstd(edad)),
    }
    top_prest = df[col_prest].value_counts(dropna=False).head(15)
    return desc, top_prest

def pruebas_asociacion(df: pd.DataFrame, col_prest: str, edad_bin: pd.Series):
    tabla = pd.crosstab(edad_bin, df[col_prest])
    chi2, p, dof, expected = chi2_contingency(tabla)
    # Cramér’s V
    n = tabla.sum().sum()
    phi2 = chi2 / n
    r, k = tabla.shape
    cramers_v = np.sqrt(phi2 / (min(k - 1, r - 1) if min(k-1,r-1) > 0 else 1))
    return chi2, p, dof, cramers_v

def clusterizar_por_edad(df: pd.DataFrame, edad: pd.Series, n_clusters=3):
    x = edad.to_frame(name="Edad").copy()
    x = x.replace([np.inf, -np.inf], np.nan).dropna()
    if x.empty or x["Edad"].nunique() < n_clusters:
        return None, None
    km = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
    labels = km.fit_predict(x)
    x["Cluster"] = labels
    cent = km.cluster_centers_.flatten()
    fig = px.box(x, x="Cluster", y="Edad", points="all", title="Clusters por Edad")
    return fig, cent

# =========================
# Modelo predictivo
# =========================
def modelo_baseline(df: pd.DataFrame, edad: pd.Series, col_prest: str, test_size=0.2, random_state=42):
    data = pd.DataFrame({"Edad": edad, "Prestacion": df[col_prest]})
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    if data["Prestacion"].nunique() < 2:
        return None  # no se puede clasificar una sola clase

    X = data[["Edad"]].values
    y = data["Prestacion"].astype(str).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )
    clf = LogisticRegression(max_iter=200, class_weight="balanced", multi_class="ovr")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)

    report = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
    rep_df = pd.DataFrame(report).T

    # Probabilidades por clase para simulador
    return {
        "clf": clf,
        "classes": clf.classes_.tolist(),
        "accuracy": acc,
        "f1_weighted": f1,
        "confusion_matrix": cm,
        "report_df": rep_df,
    }

def simulador_probabilidades(modelo, edad_input: float):
    if modelo is None or edad_input is None:
        return None
    proba = modelo["clf"].predict_proba(np.array([[edad_input]])).flatten()
    classes = modelo["classes"]
    df = pd.DataFrame({"Prestacion": classes, "Probabilidad": proba})
    df = df.sort_values("Probabilidad", ascending=False)
    fig = px.bar(df, x="Prestacion", y="Probabilidad", title=f"Probabilidades estimadas (Edad = {edad_input:.1f})")
    fig.update_layout(xaxis_tickangle=45)
    return fig, df

# =========================
# PÁGINAS
# =========================
def pagina_vision_general(df: pd.DataFrame):
    col_prest, col_edad, col_fnac, col_fref = detectar_columnas(df)
    if col_prest is None:
        st.error("No se detectó la columna de Prestación. Renombra o indica el nombre correcto.")
        st.write("Columnas disponibles:", list(df.columns))
        return

    edad = calcular_edad(df, col_edad, col_fnac, col_fref)
    if edad.isna().all():
        st.error("No fue posible calcular/detectar la Edad con las columnas disponibles.")
        st.write("Columnas disponibles:", list(df.columns))
        return

    scheme = st.selectbox("Esquema de rangos de edad", ["Décadas", "Quintiles"], index=0)
    edad_bin = binar_edad(edad, esquema=scheme)

    desc, top_prest = resumen_descriptivo(edad, df, col_prest)

    st.subheader("Resumen de Edades")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("N registros", f"{desc['n_registros']:,}")
    m2.metric("Mín", f"{desc['edad_min']:.1f}")
    m3.metric("Máx", f"{desc['edad_max']:.1f}")
    m4.metric("Media", f"{desc['edad_media']:.1f}")
    m5.metric("Mediana", f"{desc['edad_mediana']:.1f}")
    m6.metric("Std", f"{desc['edad_std']:.1f}")

    st.subheader("Top prestaciones")
    st.dataframe(top_prest.to_frame("Conteo"))

    st.subheader("Heatmap Edad vs Prestación")
    fig, tabla, tabla_pct = heatmap_edad_prestacion(df, col_prest, edad_bin)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver tabla cruzada (conteos)"):
        st.dataframe(tabla)

    with st.expander("Ver tabla cruzada (%)"):
        st.dataframe(tabla_pct.round(2))

def pagina_patrones(df: pd.DataFrame):
    col_prest, col_edad, col_fnac, col_fref = detectar_columnas(df)
    if col_prest is None:
        st.error("No se detectó la columna de Prestación.")
        return

    edad = calcular_edad(df, col_edad, col_fnac, col_fref)
    if edad.isna().all():
        st.error("No fue posible calcular/detectar la Edad.")
        return

    edad_bin = binar_edad(edad, esquema="Décadas")

    st.subheader("Asociación Edad–Prestación")
    try:
        chi2, p, dof, cv = pruebas_asociacion(df, col_prest, edad_bin)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Chi²", f"{chi2:,.2f}")
        c2.metric("p-valor", f"{p:.4f}")
        c3.metric("GL", f"{dof}")
        c4.metric("Cramér’s V", f"{cv:.3f}")
        st.caption("Regla práctica: ~0.1 (débil), ~0.3 (moderada), ~0.5 (fuerte).")
    except Exception as e:
        st.warning(f"No se pudo calcular Chi²/Cramér’s V: {e}")

    st.subheader("Clusters por edad")
    fig, centers = clusterizar_por_edad(df, edad, n_clusters=3)
    if fig is None:
        st.info("No fue posible clusterizar (datos insuficientes/atípicos).")
    else:
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Centroides de edad aprox.: {', '.join([f'{c:.1f}' for c in centers])}")

def pagina_prediccion(df: pd.DataFrame):
    col_prest, col_edad, col_fnac, col_fref = detectar_columnas(df)
    if col_prest is None:
        st.error("No se detectó la columna de Prestación.")
        return
    edad = calcular_edad(df, col_edad, col_fnac, col_fref)
    if edad.isna().all():
        st.error("No fue posible calcular/detectar la Edad.")
        return

    st.subheader("Modelo predictivo (baseline)")
    modelo = modelo_baseline(df, edad, col_prest)
    if modelo is None:
        st.info("No se pudo entrenar el modelo (clases insuficientes).")
        return

    m1, m2 = st.columns(2)
    m1.metric("Accuracy", f"{modelo['accuracy']:.3f}")
    m2.metric("F1 ponderado", f"{modelo['f1_weighted']:.3f}")

    with st.expander("Reporte de clasificación"):
        st.dataframe(modelo["report_df"].round(3))

    cm = modelo["confusion_matrix"]
    fig_cm = px.imshow(cm, text_auto=True, labels=dict(x="Predicho", y="Real", color="Conteo"),
                       x=modelo["classes"], y=modelo["classes"], aspect="auto", color_continuous_scale="Blues")
    fig_cm.update_layout(margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_cm, use_container_width=True)

    st.subheader("Simulador de probabilidades por edad")
    edad_in = st.slider("Selecciona una edad", min_value=5, max_value=100, value=35, step=1)
    fig_prob, df_prob = simulador_probabilidades(modelo, float(edad_in))
    if fig_prob:
        st.plotly_chart(fig_prob, use_container_width=True)
        with st.expander("Ver tabla de probabilidades"):
            st.dataframe(df_prob.assign(Probabilidad=(df_prob["Probabilidad"]*100).round(2)))
