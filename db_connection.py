import pyodbc
import streamlit as st

@st.cache_resource
def get_sql_conn():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=sql8020.site4now.net;"
        "DATABASE=db_a91131_test;"
        "UID=db_a91131_test_admin;"
        "PWD=dEVOPS2022;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=15;"
    )
    cnxn = pyodbc.connect(conn_str, autocommit=False)
    cnxn.timeout = 30  # ⏱️ timeout de consulta
    return cnxn

def run_query(query, params=None):
    conn = get_sql_conn()
    with conn.cursor() as cur:
        cur.execute(query, params or [])
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
    import pandas as pd
    return pd.DataFrame.from_records(rows, columns=cols)
