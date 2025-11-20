# database.py
import sqlite3
from sqlite3 import Connection
from typing import Optional

DB_FILE = "library.db"

def get_connection() -> Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Books table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        copies_total INTEGER NOT NULL,
        copies_available INTEGER NOT NULL
    )
    """)

    # Members table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        join_date TEXT NOT NULL
    )
    """)

    # Borrow records
    cur.execute("""
    CREATE TABLE IF NOT EXISTS borrows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        borrow_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        FOREIGN KEY (book_id) REFERENCES books(id),
        FOREIGN KEY (member_id) REFERENCES members(id)
    )
    """)

    conn.commit()
    conn.close()

def execute(query: str, params: tuple = (), commit: bool = False) -> sqlite3.Cursor:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    if commit:
        conn.commit()
        conn.close()
        return cur
    else:
        rows = cur.fetchall()
        conn.close()
        return rows
