import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "olist.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def get_table_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_schema(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [(row[1], row[2]) for row in cursor.fetchall()]
    conn.close()
    return columns