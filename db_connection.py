# db_connection.py
import pyodbc
import pandas as pd

def get_sqlserver_connection():
    """
    Retorna una conexión ODBC (Driver 18) a SQL Server.
    """
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=sql8020.site4now.net;"
        "DATABASE=db_a91131_test;"
        "UID=db_a91131_test_admin;"
        "PWD=dEVOPS2022;"
    )

def get_sales_data(limit=None):
    """
    Lee datos de la tabla Prestaciones_Temporal.
    - limit=None -> TODOS los registros (por defecto).
    - limit=int  -> TOP N registros.
    """
    conn = get_sqlserver_connection()
    try:
        if limit is None:
            query = "SELECT * FROM Prestaciones_Temporal"
        else:
            query = f"SELECT TOP {int(limit)} * FROM Prestaciones_Temporal"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()
