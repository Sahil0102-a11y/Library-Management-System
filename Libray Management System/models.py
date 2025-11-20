# models.py
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Book:
    id: Optional[int]
    isbn: str
    title: str
    author: str
    year: Optional[int]
    copies_total: int
    copies_available: int

@dataclass
class Member:
    id: Optional[int]
    name: str
    email: str
    phone: Optional[str]
    join_date: date
