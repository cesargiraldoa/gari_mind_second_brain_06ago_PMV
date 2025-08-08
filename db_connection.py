import pymssql
import pandas as pd

def get_sales_data():
    """
    Vista previa rápida (TOP 10) – lo de Abraham tal cual.
    """
    try:
        conn = pymssql.connect(
            server="147.182.194.168",
            user="sa",
            password="dEVOPS2022a",
            database="DENTISALUD"
        )
        query = "SELECT TOP 10 * FROM Prestaciones_Temporal;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ Error al cargar datos de ventas (preview):", e)
        return pd.DataFrame({'error': [str(e)]})

# ====== LISTAS DE CANDIDATOS ======
CANDIDATOS = {
    "prestacion": [
        "Prestacion","Prestación","TipoPrestacion","Tipo_Prestacion","Tipo de Prestacion",
        "Prestaciones","Servicio","Procedimiento","CUPS","CodigoCUPS","NombrePrestacion"
    ],
    "edad": ["Edad","EDAD","edad"],
    "fecha_prestacion": [
        "FechaPrestacion","Fecha_Atencion","FechaAtencion","Fecha",
        "Fecha_Servicio","FAtencion"
    ],
    "fecha_nacimiento": [
        "FechaNacimiento","Fecha_Nacimiento","Fec_Nacimiento",
        "Fecha de Nacimiento","FNacimiento"
    ],
    "sucursal": [
        "Sucursal","Clinica","Clínica","Centro","CentroMedico","Centro_Medico"
    ],
    "valor_venta": [
        "ValorVenta","Valor","Total","Monto","Precio",
        "Valor_Prestacion","Valor_Prestación"
    ]
}

def detectar_columnas_existentes(cols_bd):
    """
    Recibe lista de columnas reales en BD y detecta las que coinciden
    con los candidatos de cada categoría.
    """
    encontrados = {}
    norm_map = {col.lower().replace("ó","o").replace("á","a").replace("é","e").replace("í","i").replace("ú","u"): col
                for col in cols_bd}

    for categoria, candidatos in CANDIDATOS.items():
        for cand in candidatos:
            key = cand.lower().replace("ó","o").replace("á","a").replace("é","e").replace("í","i").replace("ú","u")
            if key in norm_map:
                encontrados[categoria] = norm_map[key]
                break
    return encontrados

def get_all_sales_data(fecha_ini=None, fecha_fin=None):
    """
    Carga optimizada para análisis: solo columnas clave detectadas dinámicamente.
    """
    try:
        conn = pymssql.connect(
            server="147.182.194.168",
            user="sa",
            password="dEVOPS2022a",
            database="DENTISALUD"
        )

        # Paso 1: detectar columnas reales
        df_head = pd.read_sql("SELECT TOP 1 * FROM Prestaciones_Temporal;", conn)
        columnas_bd = list(df_head.columns)
        cols_detectadas = detectar_columnas_existentes(columnas_bd)

        # Paso 2: construir lista final de columnas a traer
        columnas_finales = []

        # Prestación
        if "prestacion" in cols_detectadas:
            columnas_finales.append(cols_detectadas["prestacion"])

        # Edad o fechas para calcularla
        if "edad" in cols_detectadas:
            columnas_finales.append(cols_detectadas["edad"])
        else:
            if "fecha_nacimiento" in cols_detectadas:
                columnas_finales.append(cols_detectadas["fecha_nacimiento"])
            if "fecha_prestacion" in cols_detectadas:
                columnas_finales.append(cols_detectadas["fecha_prestacion"])

        # Fecha prestación (para filtros y series)
        if "fecha_prestacion" in cols_detectadas and cols_detectadas["fecha_prestacion"] not in columnas_finales:
            columnas_finales.append(cols_detectadas["fecha_prestacion"])

        # Sucursal
        if "sucursal" in cols_detectadas:
            columnas_finales.append(cols_detectadas["sucursal"])

        # Valor venta
        if "valor_venta" in cols_detectadas:
            columnas_finales.append(cols_detectadas["valor_venta"])

        if not columnas_finales:
            # Si no detecta nada, trae todo (fallback)
            print("⚠️ No se detectaron columnas clave, se traerá todo.")
            columnas_sql = "*"
        else:
            columnas_sql = ", ".join(f"[{c}]" for c in columnas_finales)

        # Paso 3: construir consulta con filtro opcional
        if fecha_ini and fecha_fin and "fecha_prestacion" in cols_detectadas:
            col_fecha = cols_detectadas["fecha_prestacion"]
            query = f"""
                SELECT {columnas_sql}
                FROM Prestaciones_Temporal
                WHERE [{col_fecha}] BETWEEN '{fecha_ini}' AND '{fecha_fin}';
            """
        else:
            query = f"SELECT {columnas_sql} FROM Prestaciones_Temporal;"

        # Paso 4: ejecutar y devolver
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    except Exception as e:
        print("❌ Error al cargar datos de ventas (full optimizado):", e)
        return pd.DataFrame({'error': [str(e)]})
