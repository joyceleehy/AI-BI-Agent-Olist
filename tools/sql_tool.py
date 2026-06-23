import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.db import get_connection

def run_sql_query(query: str) -> pd.DataFrame:
    """
    Runs a SQL SELECT query against the Olist database.
    Returns results as a pandas DataFrame.
    """
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})
    