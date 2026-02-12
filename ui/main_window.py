from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox, QLabel, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer
from database import Database
from ui.dialogs import ViolationDialog
from models import Violations
import logging


class ViolationDatabaseApp(QMainWindow):
    """Главное окно приложения регистрации нарушений ПДД"""

    def __init__(self):
        super().__init__()

        logger = logging.getLogger(__name__)
        logger.info("Запуск приложения")

        self.db = Database()

        self.setWindowTitle("Регистрация нарушителей ПДД")
        self.setGeometry(100, 100, 800, 600)
        
        # Расположение по центру
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self._init_ui()
        self.load_data()

    # ================= UI =================

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title = QLabel("Список нарушений ПДД")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        self.search_inputs = {}

        for field, label in {
            "brand": "Марка",
            "car_number": "Номер",
            "violation_date": "Дата",
            "name": "ФИО",
            "violation_type": "Тип",
            "invoice_number": "Квитанция"
        }.items():
            edit = QLineEdit()
            self.search_inputs[field] = edit
            main_layout.addWidget(QLabel(label))
            main_layout.addWidget(edit)


        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Марка", "Номер", "Дата",
            "ФИО", "Тип нарушения", "Квитанция", "Сумма"
        ])
        self.table.hideColumn(0)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_sorted = QPushButton("Сортировка")
        self.btn_search = QPushButton("Поиск")
        self.btn_delete = QPushButton("Удалить")

        self.btn_add.clicked.connect(self.add_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_sorted.clicked.connect(self.sorted_record)
        self.btn_search.clicked.connect(self.search_records)
        self.btn_delete.clicked.connect(self.delete_record)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_sorted)
        btn_layout.addWidget(self.btn_search)
        btn_layout.addWidget(self.btn_delete)

        main_layout.addLayout(btn_layout)

    # ================= DATA =================

    def load_data(self):
        records = self.db.fetch_all()
        self.table.setRowCount(len(records))

        for row, v in enumerate(records):
            self._insert_row(row, v)

    def _insert_row(self, row: int, v: Violations):
        self.table.setItem(row, 0, QTableWidgetItem(str(v.id)))
        self.table.setItem(row, 1, QTableWidgetItem(v.brand))
        self.table.setItem(row, 2, QTableWidgetItem(v.car_number))
        self.table.setItem(row, 3, QTableWidgetItem(v.violation_date))
        self.table.setItem(row, 4, QTableWidgetItem(v.name))
        self.table.setItem(row, 5, QTableWidgetItem(v.violation_type))
        self.table.setItem(row, 6, QTableWidgetItem(v.invoice_number))
        self.table.setItem(row, 7, QTableWidgetItem(str(v.payment_amount)))

    # ================= ACTIONS =================

    def add_record(self):
        dialog = ViolationDialog(self)
        if dialog.exec():
            try:
                self.db.insert(dialog.get_data())
                self.load_data()
                logger = logging.getLogger(__name__)
                logger.info("Добавление записи")
            except Exception as e:
                logger.warning(f"Ошибка: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_record(self):
        logger = logging.getLogger(__name__)
        row = self.table.currentRow()
        if row == -1:
            logger.warning("Попытка изменения без выбранной записи")
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return

        record_id = int(self.table.item(row, 0).text())
        violation = self.db.fetch_by_id(record_id)

        dialog = ViolationDialog(self, violation)
        if dialog.exec():
            updated = dialog.get_data()
            updated.id = record_id
            try:
                self.db.update(updated)
                self.load_data()
                logger.info(f"Пользователь изменяет запись {record_id}")
            except Exception as e:
                logger.warning(f"Ошибка {e}")
                QMessageBox.critical(self, "Ошибка", str(e))

    def search_records(self):
        logger = logging.getLogger(__name__)
        filters = {
            field: edit.text().strip()
            for field, edit in self.search_inputs.items()
        }

        results = self.db.search(filters)

        self.table.setRowCount(len(results))
        for row, v in enumerate(results):
            self._insert_row(row, v)
            logger.info(f"Пользователь ищет {results}")

    def sorted_record(self):
        logger = logging.getLogger(__name__)
        results = self.db.fetch_sorted()

        self.table.setRowCount(len(results))
        for row, v in enumerate(results):
            self._insert_row(row, v)
            logger.info("Пользователь выполняет сортировку")
        

    def delete_record(self):
        logger = logging.getLogger(__name__)
        row = self.table.currentRow()
        if row == -1:
            logger.warning(f"Ошибка, не выбрана запись")
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return

        record_id = int(self.table.item(row, 0).text())
        if QMessageBox.question(
            self, "Подтверждение",
            "Удалить выбранную запись?"
        ) == QMessageBox.StandardButton.Yes:
            self.db.delete(record_id)
            self.load_data()
            logger.info(f"Запись {record_id} удалена")
