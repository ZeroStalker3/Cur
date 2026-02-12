import sqlite3
#import logging
from config import DB_name
from models import Violations
from PyQt6.QtWidgets import QMessageBox
import logging

class Database:
    def __init__(self):
        self.init_db()

    def connect(self):
        logger = logging.getLogger(__name__)
        #logger.info(f"Иниициализация базы данных {DB_name}")
        
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

    def fetch_by_id(self, record_id: int):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM violations WHERE id = ?",
                (record_id,)
            ).fetchone()

            if not row:
                return None

            return Violations(*row)

    def insert(self, v: Violations):
        try:
            with self.connect() as conn:
                conn.execute("""
                INSERT INTO violations (brand, car_number, violation_date, name, 
                    violation_type, invoice_number, payment_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (v.brand, v.car_number, v.violation_date, v.name, v.violation_type,
                    v.invoice_number, v.payment_amount))
                
                logger = logging.getLogger(__name__)
                logger.info("Сохранение данных в базу")
        
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка: База данных заблокирована {e}")

                QMessageBox.critical(self, "Ошибка", "База данных заблокирована. Повторите позже.")
        
    def search(self, filters: dict):
        query = "SELECT * FROM violations WHERE 1=1"
        params = []

        for field, value in filters.items():
            if value:
                query += f" AND {field} LIKE ?"
                params.append(f"%{value}%")

        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [Violations(*row) for row in rows]

        logger = logging.getLogger(__name__)        
        logger.info("Попытка поиска данных")

    def fetch_sorted(self, ascending: bool = True):
        order = "ASC" if ascending else "DESC"

        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM violations ORDER BY violation_date {order}"
            ).fetchall()

            return [Violations(*row) for row in rows]

    def delete(self, record_id: int):
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM violations WHERE id = ?",
                (record_id,)
            )
            logger = logging.getLogger(__name__)
            logger.info(f"Попытка удаления {record_id}")
                

    def update(self, v: Violations):
        with self.connect() as conn:
            conn.execute("""
                UPDATE violations SET brand = ?, car_number = ?, violation_date = ?, name = ?, 
                        violation_type = ?, invoice_number = ?, payment_amount = ? WHERE id = ?"""
                        , (v.brand, v.car_number, v.violation_date, v.name, v.violation_type,
                           v.invoice_number, v.payment_amount, v.id))
            logger = logging.getLogger(__name__)
            logger.info(f"Обновление записи - {v.id}")