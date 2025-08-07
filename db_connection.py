# db_connection.py
import pyodbc
import pandas as pd

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=sql8020.site4now.net;"
        "DATABASE=db_a91131_test;"
        "UID=db_a91131_test_admin;"
        "PWD=dEVOPS2022;"
    )

def get_sales_data(limit=None):
    """
    Devuelve datos de Prestaciones_Temporal.
    Si limit es None -> TODOS los registros (como acordamos).
    Si limit es un int -> TOP N.
    """
    conn = get_connection()
    try:
        if limit is None:
            query = "SELECT * FROM Prestaciones_Temporal"
        else:
            query = f"SELECT TOP {int(limit)} * FROM Prestaciones_Temporal"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()
