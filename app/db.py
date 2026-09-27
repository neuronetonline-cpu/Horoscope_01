import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "horoscope.db"

def connect():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = connect()
    c.execute("""CREATE TABLE IF NOT EXISTS horoscopes(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        gender TEXT, birth_date TEXT NOT NULL, birth_time TEXT NOT NULL,
        birth_place TEXT, latitude REAL, longitude REAL,
        timezone TEXT DEFAULT 'Asia/Colombo', utc_time TEXT,
        julian_day REAL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.commit(); c.close()

def add_horoscope(d):
    c=connect()
    cur=c.execute("""INSERT INTO horoscopes
    (name,gender,birth_date,birth_time,birth_place,latitude,longitude,timezone,utc_time,julian_day)
    VALUES(?,?,?,?,?,?,?,?,?,?)""", tuple(d[k] for k in
    ("name","gender","birth_date","birth_time","birth_place","latitude","longitude","timezone","utc_time","julian_day")))
    c.commit(); rid=cur.lastrowid; c.close(); return rid

def search_horoscopes(term=""):
    c=connect()
    rows=c.execute("SELECT * FROM horoscopes WHERE name LIKE ? OR birth_place LIKE ? ORDER BY id DESC",
                   (f"%{term}%",f"%{term}%")).fetchall()
    c.close(); return rows
