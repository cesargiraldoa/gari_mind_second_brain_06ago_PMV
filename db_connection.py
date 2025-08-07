import pymssql
import pandas as pd

def get_sales_data():
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
        print("❌ Error al cargar datos de ventas:", e)
        return pd.DataFrame({'error': [str(e)]})
