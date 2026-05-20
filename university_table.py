import sqlite3

conn = sqlite3.connect("interview.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS universities(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
password TEXT
)
""")

conn.commit()
conn.close()