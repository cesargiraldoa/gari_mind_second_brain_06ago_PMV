import pymssql
import pandas as pd

# === Mantener EXACTO lo de Abraham (preview TOP 10) ===
def get_sales_data():
    """
    Vista previa (rápida) - TOP 10 registros para no saturar la UI.
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

# === NUEVO: análisis con TODOS los registros ===
def get_all_sales_data():
    """
    Carga completa para análisis (todos los registros).
    """
    try:
        conn = pymssql.connect(
            server="147.182.194.168",
            user="sa",
            password="dEVOPS2022a",
            database="DENTISALUD"
        )
        query = "SELECT * FROM Prestaciones_Temporal;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ Error al cargar datos de ventas (full):", e)
        return pd.DataFrame({'error': [str(e)]})
