import sqlite3
import logging
from config import DB_name
from models import Violations

class Database:
    def __init__(self):
        self.init_db()

    def connect(self):
        return sqlite3.connect(DB_name, timeout=5)
    
    def init_db(self):
        with self.connect() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                car_number TEXT NOT NULL,
                violation_date TEXT NOT NULL,
                name TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                invoice_number TEXT UNIQUE,
                payment_amount REAL NOT NULL
            )''')
    
    def fetch_all(self) -> list[Violations]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM violations").fetchall()
            return [Violations(*row) for row in rows]
    
    def insert(self, v: Violations):
        with self.connect() as conn:
            conn.execute("""
            INSERT INTO violations (brand, car_number, violation_date, name, 
                violation_type, invoice_number, payment_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (v.brand, v.car_number, v.violation_date, v.name, v.violation_type,
                  v.invoice_number, v.payment_amount))
        
    def delete(self, record_id: int):
        with  self.connect() as conn:
            conn.execute("""
            DELETE FROM violations where id = ?
            """, (record_id))