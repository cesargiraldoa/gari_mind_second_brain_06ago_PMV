import streamlit as st
from db_connection import run_query

TABLE = "dbo.Prestaciones_Temporal"

@st.cache_data(ttl=300, show_spinner=False)
def fetch_preview(top_n=10):
    q = f"SELECT TOP {int(top_n)} * FROM {TABLE} WITH (NOLOCK)"
    return run_query(q)

@st.cache_data(ttl=900, show_spinner=False)
def fetch_all(date_col=None, date_range=None):
    base = f"SELECT * FROM {TABLE} WITH (NOLOCK)"
    if date_col and date_range:
        start, end = date_range
        base += f" WHERE {date_col} >= ? AND {date_col} < ?"
        return run_query(base, [start, end])
    return run_query(base)
