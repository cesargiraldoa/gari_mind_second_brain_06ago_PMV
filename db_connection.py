import pandas as pd
import pymssql

SQL_SERVER = "sql8020.site4now.net"
SQL_DB     = "db_a91131_test"
SQL_USER   = "db_a91131_test_admin"
SQL_PASS   = "dEVOPS2022"

def _connect():
    return pymssql.connect(
        server=SQL_SERVER, user=SQL_USER, password=SQL_PASS, database=SQL_DB,
        timeout=30, login_timeout=10
    )

def list_tables_like(pattern="Prestaciones"):
    """
    Lista tablas/vistas disponibles, opcionalmente filtrando por patrón.
    Devuelve nombres calificados con esquema: [schema].[name]
    """
    q = """
    SELECT QUOTENAME(TABLE_SCHEMA)+'.'+QUOTENAME(TABLE_NAME) AS full_name
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE IN ('BASE TABLE','VIEW')
      {where}
    ORDER BY full_name;
    """
    where = "AND TABLE_NAME LIKE %s" if pattern else ""
    params = [f"%{pattern}%"] if pattern else []
    with _connect() as conn:
        return pd.read_sql(q.format(where=where), conn, params=params)["full_name"].tolist()

def detect_prestaciones_table():
    lst = list_tables_like("Prestaciones")
    return lst[0] if lst else None

def get_all_data_from(table_fullname):
    """
    Trae TODOS los registros de la tabla/vista indicada (con esquema).
    `table_fullname` debe venir como [schema].[table] (ya entre corchetes).
    """
    q = f"SELECT * FROM {table_fullname}"
    with _connect() as conn:
        return pd.read_sql(q, conn)

