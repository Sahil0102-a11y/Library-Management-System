# library.py
from typing import List, Optional
from datetime import datetime, timedelta, date
from models import Book, Member
import database
import sqlite3

DATE_FMT = "%Y-%m-%d"

class Library:
    def __init__(self):
        database.init_db()

    # ----------------- Book operations -----------------
    def add_book(self, isbn: str, title: str, author: str, year: Optional[int], copies: int) -> int:
        cur = database.get_connection().cursor()
        cur.execute(
            "INSERT INTO books (isbn, title, author, year, copies_total, copies_available) VALUES (?, ?, ?, ?, ?, ?)",
            (isbn, title, author, year, copies, copies)
        )
        cur.connection.commit()
        book_id = cur.lastrowid
        cur.connection.close()
        return book_id

    def update_book(self, book_id: int, **fields) -> bool:
        allowed = {"isbn", "title", "author", "year", "copies_total", "copies_available"}
        set_clause = []
        params = []
        for k, v in fields.items():
            if k in allowed:
                set_clause.append(f"{k} = ?")
                params.append(v)
        if not set_clause:
            return False
        params.append(book_id)
        query = f"UPDATE books SET {', '.join(set_clause)} WHERE id = ?"
        database.execute(query, tuple(params), commit=True)
        return True

    def remove_book(self, book_id: int) -> bool:
        database.execute("DELETE FROM books WHERE id = ?", (book_id,), commit=True)
        return True

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        rows = database.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        if not rows:
            return None
        r = rows[0]
        return Book(id=r["id"], isbn=r["isbn"], title=r["title"], author=r["author"],
                    year=r["year"], copies_total=r["copies_total"], copies_available=r["copies_available"])

    def search_books(self, keyword: str) -> List[Book]:
        like = f"%{keyword}%"
        rows = database.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?",
                                (like, like, like))
        return [Book(id=r["id"], isbn=r["isbn"], title=r["title"], author=r["author"],
                     year=r["year"], copies_total=r["copies_total"], copies_available=r["copies_available"]) for r in rows]

    def list_books(self) -> List[Book]:
        rows = database.execute("SELECT * FROM books")
        return [Book(id=r["id"], isbn=r["isbn"], title=r["title"], author=r["author"],
                     year=r["year"], copies_total=r["copies_total"], copies_available=r["copies_available"]) for r in rows]

    # ----------------- Member operations -----------------
    def add_member(self, name: str, email: str, phone: Optional[str]) -> int:
        join_date = date.today().strftime(DATE_FMT)
        cur = database.get_connection().cursor()
        cur.execute("INSERT INTO members (name, email, phone, join_date) VALUES (?, ?, ?, ?)",
                    (name, email, phone, join_date))
        cur.connection.commit()
        member_id = cur.lastrowid
        cur.connection.close()
        return member_id

    def update_member(self, member_id: int, **fields) -> bool:
        allowed = {"name", "email", "phone"}
        set_clause = []
        params = []
        for k, v in fields.items():
            if k in allowed:
                set_clause.append(f"{k} = ?")
                params.append(v)
        if not set_clause:
            return False
        params.append(member_id)
        query = f"UPDATE members SET {', '.join(set_clause)} WHERE id = ?"
        database.execute(query, tuple(params), commit=True)
        return True

    def remove_member(self, member_id: int) -> bool:
        database.execute("DELETE FROM members WHERE id = ?", (member_id,), commit=True)
        return True

    def get_member_by_id(self, member_id: int) -> Optional[Member]:
        rows = database.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        if not rows:
            return None
        r = rows[0]
        return Member(id=r["id"], name=r["name"], email=r["email"], phone=r["phone"],
                      join_date=datetime.strptime(r["join_date"], DATE_FMT).date())

    def list_members(self) -> List[Member]:
        rows = database.execute("SELECT * FROM members")
        return [Member(id=r["id"], name=r["name"], email=r["email"], phone=r["phone"],
                       join_date=datetime.strptime(r["join_date"], DATE_FMT).date()) for r in rows]

    # ----------------- Borrow / Return -----------------
    def borrow_book(self, book_id: int, member_id: int, days: int = 14) -> bool:
        # Check availability
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT copies_available FROM books WHERE id = ?", (book_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise ValueError("Book not found.")
        if row["copies_available"] <= 0:
            conn.close()
            return False

        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=days)
        cur.execute("INSERT INTO borrows (book_id, member_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
                    (book_id, member_id, borrow_date.strftime(DATE_FMT), due_date.strftime(DATE_FMT)))
        cur.execute("UPDATE books SET copies_available = copies_available - 1 WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
        return True

    def return_book(self, borrow_id: int) -> bool:
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM borrows WHERE id = ?", (borrow_id,))
        record = cur.fetchone()
        if not record:
            conn.close()
            raise ValueError("Borrow record not found.")
        if record["return_date"] is not None:
            conn.close()
            return False  # already returned

        return_date = date.today().strftime(DATE_FMT)
        cur.execute("UPDATE borrows SET return_date = ? WHERE id = ?", (return_date, borrow_id))
        cur.execute("UPDATE books SET copies_available = copies_available + 1 WHERE id = ?", (record["book_id"],))
        conn.commit()
        conn.close()
        return True

    def list_borrowed(self) -> List[sqlite3.Row]:
        rows = database.execute("SELECT b.id as borrow_id, books.title, members.name as member_name, b.borrow_date, b.due_date, b.return_date "
                                "FROM borrows b JOIN books ON b.book_id = books.id JOIN members ON b.member_id = members.id "
                                "ORDER BY b.borrow_date DESC")
        return rows

    def list_overdue(self) -> List[sqlite3.Row]:
        today = date.today().strftime(DATE_FMT)
        rows = database.execute("SELECT b.id as borrow_id, books.title, members.name as member_name, b.borrow_date, b.due_date "
                                "FROM borrows b JOIN books ON b.book_id = books.id JOIN members ON b.member_id = members.id "
                                "WHERE b.return_date IS NULL AND b.due_date < ?",
                                (today,))
        return rows
