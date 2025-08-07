import pyodbc
import pandas as pd

def get_sales_data():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=sql8020.site4now.net;"
            "DATABASE=db_a91131_test;"
            "UID=db_a91131_test_admin;"
            "PWD=dEVOPS2022;"
            "Encrypt=no;"
        )
        query = "SELECT TOP 100 * FROM dbo.Prestaciones_Temporal"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("Error de conexión:", e)
        return None
