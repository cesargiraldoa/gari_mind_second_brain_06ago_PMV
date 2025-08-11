import pymssql
import pandas as pd

# 🔌 Conexión estable de Abraham
def get_conn():
    return pymssql.connect(
        server="147.182.194.168",
        user="sa",
        password="dEVOPS2022a",
        database="DENTISALUD",
        timeout=30, login_timeout=15
    )

# ✅ Preview TOP 10 (lo que ya usas)
def get_sales_data():
    try:
        conn = get_conn()
        query = "SELECT TOP 10 * FROM Prestaciones_Temporal;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ Error al cargar datos de ventas:", e)
        return pd.DataFrame({'error': [str(e)]})

# ▶️ NUEVO: Carga completa para análisis, con filtro opcional de fechas
def get_all_sales_data(
    table_name: str = "Prestaciones_Temporal",
    date_col: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None
) -> pd.DataFrame:
    base = f"SELECT * FROM {table_name}"
    params = []
    if date_col and date_from and date_to:
        base += f" WHERE CONVERT(date, {date_col}) BETWEEN %s AND %s"
        params = [date_from, date_to]
    with get_conn() as conn:
        return pd.read_sql(base, conn, params=params if params else None)
