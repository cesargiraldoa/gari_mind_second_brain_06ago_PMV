import pyodbc
import pandas as pd

CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=sql8020.site4now.net;"
    "DATABASE=db_a91131_test;"
    "UID=db_a91131_test_admin;"
    "PWD=dEVOPS2022;"
    "Encrypt=yes;TrustServerCertificate=yes;"
)

def get_sqlserver_connection():
    # Timeout corto para no colgar la UI si algo va lento
    return pyodbc.connect(CONN_STR, timeout=10)

def get_sales_data(query="SELECT TOP 1000 * FROM dbo.Prestaciones_Temporal"):
    conn = get_sqlserver_connection()
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()
