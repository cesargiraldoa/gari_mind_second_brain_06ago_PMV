import pandas as pd
import pymssql

# Credenciales originales
SQL_SERVER = "sql8020.site4now.net"
SQL_DB     = "db_a91131_test"
SQL_USER   = "db_a91131_test_admin"
SQL_PASS   = "dEVOPS2022"

def get_all_sales_data():
    """
    Conecta vía pymssql y devuelve TODOS los datos de la tabla Prestaciones_Temporal.
    """
    conn = pymssql.connect(
        server=SQL_SERVER,
        user=SQL_USER,
        password=SQL_PASS,
        database=SQL_DB,
        timeout=30,          # tiempo de espera en conexión
        login_timeout=10     # tiempo de espera al iniciar conexión
    )
    try:
        query = "SELECT * FROM dbo.Prestaciones_Temporal"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()
