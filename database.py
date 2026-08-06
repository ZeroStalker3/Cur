import sqlite3
from config import DB_name
from models import Violations
from PyQt6.QtWidgets import QMessageBox
import logging

logger = logging.getLogger(__name__)

class Database:
    ALLOWED_SORT_FIELDS = {"violation_date", "brand", "name", "payment_amount"}
    
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
                
                logger.info("Сохранение данных в базу")
        
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logger.error(f"Ошибка: База данных заблокирована {e}")
                QMessageBox.critical(None, "Ошибка", "База данных заблокирована. Повторите позже.")
            raise
        
        except sqlite3.IntegrityError as e:
            logger.error(f"Ошибка целостности данных: {e}")
            raise
    
    def search(self, filters: dict):
        query = "SELECT * FROM violations WHERE 1=1"
        params = []

        allowed_fields = {"brand", "car_number", "violation_date", "name", "violation_type", "invoice_number"}
        
        for field, value in filters.items():
            if field not in allowed_fields:
                logger.warning(f"Попытка SQL-инъекции через поле: {field}")
                continue
            if value:
                query += f" AND {field} LIKE ?"
                params.append(f"%{value}%")

        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
            logger.info("Выполнен поиск данных")
            return [Violations(*row) for row in rows]

    def fetch_sorted(self, field: str = "violation_date", ascending: bool = True):
        order = "ASC" if ascending else "DESC"
        
        if field not in self.ALLOWED_SORT_FIELDS:
            logger.warning(f"Попытка сортировки по недопустимому полю: {field}")
            field = "violation_date"

        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM violations ORDER BY {field} {order}"
            ).fetchall()

            return [Violations(*row) for row in rows]

    def delete(self, record_id: int):
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM violations WHERE id = ?",
                (record_id,)
            )
            logger.info(f"Удалена запись {record_id}")
                

    def update(self, v: Violations):
        with self.connect() as conn:
            conn.execute("""
                UPDATE violations SET brand = ?, car_number = ?, violation_date = ?, name = ?, 
                        violation_type = ?, invoice_number = ?, payment_amount = ? WHERE id = ?"""
                        , (v.brand, v.car_number, v.violation_date, v.name, v.violation_type,
                           v.invoice_number, v.payment_amount, v.id))
            logger.info(f"Обновлена запись {v.id}")