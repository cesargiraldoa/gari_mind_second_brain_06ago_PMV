import pymssql
import pandas as pd

SERVER = "147.182.194.168"
USER = "sa"
PASSWORD = "dEVOPS2022a"
DATABASE = "DENTISALUD"

def get_connection():
    return pymssql.connect(
        server=SERVER, user=USER, password=PASSWORD, database=DATABASE,
        timeout=30, login_timeout=10, as_dict=False
    )

def get_sales_data(table="Prestaciones_Temporal", top=None):
    """
    Trae datos desde SQL Server vía pymssql.
    - table: nombre de la tabla/vista (sin esquema si es dbo)
    - top: si None, trae TODO; si es int, aplica TOP n
    """
    top_clause = f"TOP {int(top)} " if top else ""
    query = f"SELECT {top_clause} * FROM dbo.{table};"
    with get_connection() as conn:
        df = pd.read_sql(query, conn)
    return df

def list_tables_like(pattern=None):
    where = "WHERE TABLE_TYPE IN ('BASE TABLE','VIEW')"
    params = []
    if pattern:
        where += " AND TABLE_NAME LIKE %s"
        params.append(f"%{pattern}%")
    q = f"""
    SELECT QUOTENAME(TABLE_SCHEMA)+'.'+QUOTENAME(TABLE_NAME) AS full_name
    FROM INFORMATION_SCHEMA.TABLES
    {where}
    ORDER BY full_name
    """
    with get_connection() as conn:
        return pd.read_sql(q, conn, params=params)["full_name"].tolist()
