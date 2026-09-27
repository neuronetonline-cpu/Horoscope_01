import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "horoscope.db"

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect()
    con.execute("""
        CREATE TABLE IF NOT EXISTS horoscopes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            birth_date TEXT NOT NULL,
            birth_time TEXT NOT NULL,
            birth_place TEXT,
            latitude REAL,
            longitude REAL,
            timezone TEXT DEFAULT 'Asia/Colombo',
            utc_time TEXT,
            julian_day REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    columns = {row["name"] for row in con.execute("PRAGMA table_info(horoscopes)")}
    if "utc_time" not in columns:
        con.execute("ALTER TABLE horoscopes ADD COLUMN utc_time TEXT")
    if "julian_day" not in columns:
        con.execute("ALTER TABLE horoscopes ADD COLUMN julian_day REAL")
    con.commit()
    con.close()

def add_horoscope(data):
    con = connect()
    cur = con.execute("""
        INSERT INTO horoscopes
        (name, gender, birth_date, birth_time, birth_place,
         latitude, longitude, timezone, utc_time, julian_day)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["gender"], data["birth_date"], data["birth_time"],
        data["birth_place"], data["latitude"], data["longitude"],
        data["timezone"], data["utc_time"], data["julian_day"]
    ))
    con.commit()
    row_id = cur.lastrowid
    con.close()
    return row_id

def search_horoscopes(term=""):
    con = connect()
    rows = con.execute("""
        SELECT * FROM horoscopes
        WHERE name LIKE ? OR birth_place LIKE ?
        ORDER BY id DESC
    """, (f"%{term}%", f"%{term}%")).fetchall()
    con.close()
    return rows
