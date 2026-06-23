import sqlite3
conn = sqlite3.connect("database/olist.db")
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
for (table,) in tables:
    print(f"\n{table}")
    cols = cursor.execute(f"PRAGMA table_info({table});").fetchall()
    for col in cols:
        print(f"  {col[1]} ({col[2]})")
