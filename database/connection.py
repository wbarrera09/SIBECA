import streamlit as st
from sqlalchemy import create_engine
import pandas as pd


def get_engine():
    database_url = st.secrets["DATABASE_URL"]
    engine = create_engine(database_url)
    return engine


def run_query(query, params=None):
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


def execute_query(query, params=None):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(query, params or {})