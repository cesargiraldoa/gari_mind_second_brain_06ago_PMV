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

def get_all_sales_data(fecha_ini=None, fecha_fin=None):
    """
    Carga completa para análisis.
    Si se pasan fechas (datetime.date o str 'YYYY-MM-DD'), filtra por el rango.
    """
    try:
        conn = pymssql.connect(
            server="147.182.194.168",
            user="sa",
            password="dEVOPS2022a",
            database="DENTISALUD"
        )

        if fecha_ini and fecha_fin:
            query = f"""
                SELECT * FROM Prestaciones_Temporal
                WHERE FechaPrestacion BETWEEN '{fecha_ini}' AND '{fecha_fin}';
            """
        else:
            query = "SELECT * FROM Prestaciones_Temporal;"

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    except Exception as e:
        print("❌ Error al cargar datos de ventas (full):", e)
        return pd.DataFrame({'error': [str(e)]})
