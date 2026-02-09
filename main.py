import sys
import sqlite3
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QLineEdit, QComboBox, QGridLayout,
    QGroupBox, QLabel, QSizePolicy, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QSize, QRegularExpression
from PyQt6.QtGui import QFont, QPalette, QColor, QBrush, QPen, QLinearGradient, QRegularExpressionValidator


# Настройка логирования
logging.basicConfig(
    filename='Log_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class ViolationDatabaseApp(QMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("Регистрация нарушителей ПДД")
        self.setGeometry(100, 100, 1000, 600)
        
        # Инициализация базы данных
        self.init_db()
        
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основная макетная структура
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Создание заголовка
        header_label = QLabel("Список нарушений ПДД")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px;")
        main_layout.addWidget(header_label)
        
        # Создание таблицы
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Id",
            "Марка", "Номер", "Дата", "ФИО", "Тип нарушения", "Квитанция", "Сумма"
        ])
        self.table.hideColumn(0)
        # Настройка таблицы
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { 
                background-color: #ecf0f1; 
                color: black;
                gridline-color: #bdc3c7; 
                selection-background-color: #3498db;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
            }
        """)
        
        # Загрузка данных
        self.load_data()
        
        # Добавление кнопок в нижнюю панель
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_add.setStyleSheet("background-color: #27ae60; color: white; border-radius: 5px;")
        self.btn_add.clicked.connect(self.add_record)
        
        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 5px;")
        self.btn_delete.clicked.connect(self.delete_record)
        
        self.btn_search = QPushButton("Поиск")
        self.btn_search.setStyleSheet("background-color: #9b59b6; color: white; border-radius: 5px;")
        self.btn_search.clicked.connect(self.search_records)
        
        self.btn_sort = QPushButton("Сортировать")
        self.btn_sort.setStyleSheet("background-color: #34495e; color: white; border-radius: 5px;")
        self.btn_sort.clicked.connect(self.sort_records)

        self.btn_edit = QPushButton("Изменить")
        self.btn_edit.setStyleSheet("background-color: #27ae60; color: white; border-radius: 5px;")
        self.btn_edit.clicked.connect(self.edit_record)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_search)
        btn_layout.addWidget(self.btn_sort)
        btn_layout.addWidget(self.btn_edit)

        # Создание группы для фильтрации
        filter_group = QGroupBox("Фильтрация")
        filter_group.setStyleSheet("color: black")
        filter_layout = QGridLayout()
        filter_layout.setHorizontalSpacing(15)
        
        # Добавляем элементы фильтрации
        self.brand_input = QLineEdit()
        self.car_input = QLineEdit()
        self.date_input = QLineEdit()
        self.name_input = QLineEdit()
        self.type_input = QLineEdit()
        self.invoice_input = QLineEdit()
        
        filter_layout.addWidget(QLabel("Марка:"), 0, 0)
        filter_layout.addWidget(self.brand_input, 0, 1)
        
        filter_layout.addWidget(QLabel("Номер:"), 1, 0)
        filter_layout.addWidget(self.car_input, 1, 1)
        
        filter_layout.addWidget(QLabel("Дата:"), 2, 0)
        filter_layout.addWidget(self.date_input, 2, 1)
        
        filter_layout.addWidget(QLabel("ФИО:"), 3, 0)
        filter_layout.addWidget(self.name_input, 3, 1)
        
        filter_layout.addWidget(QLabel("Тип нарушения:"), 4, 0)
        filter_layout.addWidget(self.type_input, 4, 1)
        
        filter_layout.addWidget(QLabel("Квитанция:"), 5, 0)
        filter_layout.addWidget(self.invoice_input, 5, 1)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # Добавление таблицы и кнопок
        main_layout.addWidget(self.table)
        main_layout.addLayout(btn_layout)
        
        # Настройка цветовой схемы
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 248, 255))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        self.setPalette(palette)
    
    def init_db(self):
        """Инициализация базы данных"""
        try:
            logging.info("Инициализация БД")
            conn = sqlite3.connect('violations.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                car_number TEXT NOT NULL,
                violation_date TEXT NOT NULL,
                name TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                invoice_number TEXT UNIQUE,
                payment_amount REAL NOT NULL
            )''')
            conn.commit()
            logging.info("База данных инициализирована успешно")
        except sqlite3.Error as e:
            logging.error(f"Ошибка при создании таблицы: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось инициализировать БД: {str(e)}")
        finally:
            conn.close()

    def load_data(self):
        
        """
        Загрузка данных в таблицу
        """

        try:
            logging.info("Загрузка данных из БД")
            conn = sqlite3.connect('violations.db')
            c = conn.cursor()
            c.execute("SELECT * FROM violations")
            rows = c.fetchall()
            logging.info(f"Найдено {len(rows)} записей")
            
            self.table.setRowCount(len(rows))
            
            for i, row in enumerate(rows):
                # Добавляем ID в скрытый первый столбец
                self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
                # Остальные данные в видимые столбцы
                for j, col in enumerate(row[1:]):
                    self.table.setItem(i, j + 1, QTableWidgetItem(str(col)))
            
            conn.close()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке данных: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")
        except Exception as e:
            logging.exception("Необработанная ошибка")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {str(e)}")
    
    def is_valid_date(self, date_str):
        
        """
        Проверка корректности формата даты
        """

        try:
            logging.debug(f"Проверка даты: {date_str}")
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            logging.error(f"Неверный формат даты: {date_str}")
            return False
    
    def add_record(self):
       
        """
        Открывает диалоговое окно для добавления нового нарушения ПДД.

        Позволяет пользователю ввести данные через форму, выполняет базовую
        валидацию обязательных полей и инициирует сохранение записи в базе данных.
        """

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить нарушение")
        layout = QVBoxLayout()
        
        # Форма ввода
        fields = [
            ("Марка:", QLineEdit()),
            ("Номер:", QLineEdit()),
            ("Дата (YYYY-MM-DD):", QLineEdit()),
            ("ФИО:", QLineEdit()),
            ("Тип нарушения:", QLineEdit()),
            ("Квитанция:", QLineEdit()),
            ("Сумма (число):", QLineEdit())
        ]
        
        for label, field in fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(field)
            layout.addLayout(row)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_cancel = QPushButton("Отмена")
        btn_save.clicked.connect(lambda: self.save_to_db(
            fields[0][1].text().strip(),
            fields[1][1].text().strip(),
            fields[2][1].text().strip(),
            fields[3][1].text().strip(),
            fields[4][1].text().strip(),
            fields[5][1].text().strip(),
            float(fields[6][1].text().strip())
        ))
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            brand = fields[0][1].text().strip()
            car_num = fields[1][1].text().strip()
            date = fields[2][1].text().strip()

            data_now = datetime.today().date()
            db_date = datetime.strptime(date, "%Y-%m-%d").date() 

            if not brand or not car_num or not date:
                logging.warning("Не заполнены обязательные поля")
                QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
                return
                
            if not self.is_valid_date(date):
                logging.warning("Неверный формат даты")
                QMessageBox.warning(self, "Ошибка", "Дата должна быть в формате YYYY-MM-DD")
                return

            # Сохранение в БД
            self.save_to_db(brand, car_num, date, fields[3][1].text(), fields[4][1].text(), 
                                fields[5][1].text(), float(fields[6][1].text()))
            self.load_data()  # Обновляем таблицу
    
    def save_to_db(self, brand, car_num, date, name, violation_type, invoice, amount):
        
        """
        Сохраняет данные о нарушении ПДД в базе данных SQLite.

        :param brand: Марка автомобиля
        :param car_num: Государственный номер автомобиля
        :param date: Дата нарушения в формате YYYY-MM-DD
        :param name: ФИО нарушителя
        :param violation_type: Тип нарушения ПДД
        :param invoice: Номер квитанции
        :param amount: Сумма штрафа
        """

        try:
            logging.info(f"Попытка сохранения записи: {brand} {car_num} {date}")
            conn = sqlite3.connect('violations.db', timeout=5)
            c = conn.cursor()
            c.execute('''
                INSERT INTO violations (brand, car_number, violation_date, name, 
                violation_type, invoice_number, payment_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (brand, car_num, date, name, violation_type, invoice, amount))
            conn.commit()
            logging.info("Запись успешно сохранена")
            QMessageBox.information(self, "Успех", "Запись успешно добавлена")

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logging.error("Ошибка: База данных заблокирована")
                QMessageBox.critical(self, "Ошибка", "База данных заблокирована. Повторите позже.")
            else:
                logging.error(f"Ошибка при сохранении записи: {str(e)}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить запись: {str(e)}")

        except sqlite3.IntegrityError as e:
            logging.error(f"Ошибка уникальности: {str(e)}")
            QMessageBox.critical(self, "Ошибка", "Номер квитанции должен быть уникальным")

        except ValueError as e:
            logging.error(f"Ошибка валидации: {str(e)}")
            QMessageBox.critical(self, "Ошибка", "Сумма должна быть числом")
        
        except Exception as e:
            logging.exception("Неожиданная ошибка при сохранении")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            
        finally:
            if conn:
                conn.close()
    
    def delete_record(self):
        
        """
        Удаляет выбранную пользователем запись из базы данных и таблицы интерфейса.

        Получает идентификатор записи из выделенной строки таблицы
        и выполняет удаление из базы данных SQLite.
        """

        if not self.table.selectionModel().hasSelection():
            logging.warning("Попытка удаления без выбора строки")
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления")
            return
            
        row_index = self.table.selectionModel().selectedRows()[0].row()
        selected_id = self.table.item(row_index, 0).text()  # ID из скрытого столбца
        
        try:
            logging.info(f"Удаление записи с ID: {selected_id}")
            conn = sqlite3.connect('violations.db', timeout=5)
            c = conn.cursor()
            c.execute("DELETE FROM violations WHERE id = ?", (selected_id,))
            conn.commit()
            conn.close()
            
            self.table.removeRow(row_index)
            QMessageBox.information(self, "Успех", "Запись удалена")
            logging.info("Запись успешно удалена")

        except sqlite3.Error as e:
            logging.error(f"Ошибка при удалении: {str(e)}")
            QMessageBox.critical(self, "Ошибка", "Не удалось удалить запись")
            
        except Exception as e:
            logging.exception("Ошибка при удалении")
            QMessageBox.critical(self, "Ошибка", "Ошибка удаления")
    
    def search_records(self):
        
        """
        Формирует SQL-запрос с условиями LIKE для каждого заполненного поля
        и отображает найденные записи в таблице.
        """""

        query = "SELECT * FROM violations WHERE 1=1"
        params = []

        fields = {
            "brand": self.brand_input,
            "car_number": self.car_input,
            "violation_date": self.date_input,
            "name": self.name_input,
            "violation_type": self.type_input,
            "invoice_number": self.invoice_input
        }

        for db_field, widget in fields.items():
            value = widget.text().strip()
            if value:
                query += f" AND {db_field} LIKE ?"
                params.append(f"%{value}%")

        logging.info(f"Поиск SQL: {query}")
        logging.info(f"Параметры: {params}")

        try:
            conn = sqlite3.connect("violations.db", timeout=5)
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            self.display_results(results)

        except sqlite3.Error as e:
            logging.error(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска:\n{e}")

    def display_results(self, results):
        
        """
        Отображение результатов поиска в таблицу

        :param results: Список кортежей с записями, полученными из базы данных
        """

        if not results:
            logging.warning("Нет результатов поиска")
            QMessageBox.warning(self, "Результаты", "Не найдено записей")
            return

        logging.info(f"Найдено {len(results)} записей")
        self.table.setRowCount(0)
        for i, row in enumerate(results):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            for j, col in enumerate(row[1:]):
                self.table.setItem(i, j + 1, QTableWidgetItem(str(col)))
    
    def sort_records(self):
        
        """
        Выполняет сортировку записей по дате нарушения
        и обновляет содержимое таблицы.
        """

        column = self.table.horizontalHeader().logicalIndex(2) 
        
        # Существует ли данные
        if column == -1:
            logging.warning("Не найден столбец для сортировки")
            return
        
        # Сортировка
        try:
            conn = sqlite3.connect('violations.db', timeout=5)
            c = conn.cursor()
            c.execute("SELECT * FROM violations ORDER BY violation_date ASC")
            rows = c.fetchall()
            conn.close()
            
            # Обновление таблицы
            self.table.setRowCount(len(rows))
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                # Добавляем ID в скрытый первый столбец
                self.table.setItem(i, 0, QTableWidgetItem(str(row[0])))
                # Остальные данные в видимые столбцы
                for j, col in enumerate(row[1:]):
                    self.table.setItem(i, j + 1, QTableWidgetItem(str(col)))
            logging.info("Таблица отсортирована по дате")
        except sqlite3.Error as e:
            logging.error(f"Ошибка при сортировке: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось отсортировать: {str(e)}")
    
    def edit_record(self):
        
        """
        Открывает диалоговое окно для редактирования выбранной записи.

        Получает данные выбранной строки таблицы, заполняет поля диалога
        и передаёт обновлённые значения в метод update_record.
        """

        if not self.table.selectionModel().hasSelection():
            logging.warning("Попытка редактирования без выбора строки")
            QMessageBox.warning(self, "Ошибка", "Выберите строку для редактирования")
            return
        
        row_index = self.table.selectionModel().selectedRows()[0].row()
        record = self.get_record_from_row(row_index)
        
        # Открываем для редактирования
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать нарушение")
        layout = QVBoxLayout()
        
        fields = [
            ("Марка:", QLineEdit(record['brand'])),
            ("Номер:", QLineEdit(record['car_number'])),
            ("Дата:", QLineEdit(record['violation_date'])),
            ("ФИО:", QLineEdit(record['name'])),
            ("Тип нарушения:", QLineEdit(record['violation_type'])),
            ("Квитанция:", QLineEdit(record['invoice_number'])),
            ("Сумма:", QLineEdit(str(record['payment_amount'])))
        ]
        
        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_cancel = QPushButton("Отмена")
        btn_save.clicked.connect(lambda: self.update_record(record, fields))
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        # Добавляем поля
        for label, field in fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(field)
            layout.addLayout(row)
        
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()  # Обновляем таблицу после сохранения
            logging.info("Запись успешно обновлена")
    
    def update_record(self, record, fields):
        
        """
        Docstring для update_record:
        Обновляет запись о нарушении ПДД в базе данных.

        :param record: Словарь с текущими данными записи, содержащий как минимум ключ 'id'
        :param fields: Список UI-элементов, из которых извлекаются новые значения полей
        """

        try:
            logging.info(f"Обновление записи с ID: {record['id']}")
            conn = sqlite3.connect('violations.db', timeout=5)
            c = conn.cursor()
            # Формируем запрос
            update_query = "UPDATE violations SET "
            for field in ["brand", "car_number", "violation_date", "name", 
                        "violation_type", "invoice_number", "payment_amount"]:
                update_query += f"{field} = ?, "
            update_query = update_query.rstrip(", ") + " WHERE id = ?"
            
            # Получаем обновленные данные
            new_data = [field[1].text() for field in fields]
            new_data.append(str(record['id']))
            
            # Выполняем обновление
            c.execute(update_query, new_data)
            conn.commit()
            conn.close()
            logging.info("Запись обновлена")

        except sqlite3.Error as e:
            logging.error(f"Ошибка при обновлении записи: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись: {str(e)}")
            
        except Exception as e:
            logging.exception("Неожиданная ошибка при обновлении")
            QMessageBox.critical(self, "Ошибка", "Ошибка при обновлении записи")
    
    def get_record_from_row(self, row_index):
        
        """
        Docstring для get_record_from_row
        Возвращает запись о нарушении из базы данных по индексу строки.

        :param row_index: Индекс записи в результирующем списке (нумерация с 0)
        :return: Словарь с данными о нарушении ПДД
        """

        # ID из скрытого столбца
        record_id = self.table.item(row_index, 0).text()
        
        # Получаем полные данные из БД по ID
        conn = sqlite3.connect('violations.db')
        c = conn.cursor()
        c.execute("SELECT * FROM violations WHERE id = ?", (record_id,))
        record = c.fetchone()
        conn.close()

        return {
            'id': record[0],
            'brand': record[1],
            'car_number': record[2],
            'violation_date': record[3],
            'name': record[4],
            'violation_type': record[5],
            'invoice_number': record[6],
            'payment_amount': record[7]
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ViolationDatabaseApp()
    window.show()
    sys.exit(app.exec())