import pyodbc

def get_conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=sql8020.site4now.net;"
        "DATABASE=db_a91131_test;"
        "UID=db_a91131_test_admin;"
        "PWD=dEVOPS2022;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )

def get_sales_sample(top_n=10):
    with get_conn() as conn:
        return pd.read_sql(f"SELECT TOP {top_n} * FROM dbo.Prestaciones_Temporal", conn)
