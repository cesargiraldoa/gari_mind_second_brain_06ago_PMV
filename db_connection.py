# db_connection.py
import pandas as pd
import pyodbc

def get_conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=sql8020.site4now.net;"
        "DATABASE=db_a91131_test;"
        "UID=db_a91131_test_admin;"
        "PWD=dEVOPS2022;"
        "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
    )

# ▶️ Usado por la vista previa (no queremos traer todo en pantalla)
def get_sales_data(top_n: int = 10) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql(f"SELECT TOP {top_n} * FROM dbo.Prestaciones_Temporal", conn)

# ▶️ Usado por el análisis (sí trae todo, con filtro opcional de fechas)
def get_all_sales_data(date_from: str | None = None, date_to: str | None = None) -> pd.DataFrame:
    query = "SELECT * FROM dbo.Prestaciones_Temporal"
    params = []
    if date_from and date_to:
        query += " WHERE CONVERT(date, Fecha_Prestacion) BETWEEN ? AND ?"
        params = [date_from, date_to]
    with get_conn() as conn:
        return pd.read_sql(query, conn, params=params)
