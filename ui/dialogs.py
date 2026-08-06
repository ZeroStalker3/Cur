from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QDateEdit,
    QMessageBox,
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QDoubleValidator

from models import Violations


class ViolationDialog(QDialog):

    FIELD_LABELS = {
        "brand": "Марка автомобиля",
        "car_number": "Гос. номер",
        "violation_date": "Дата нарушения",
        "name": "ФИО",
        "violation_type": "Тип нарушения",
        "invoice_number": "Номер квитанции",
        "payment_amount": "Сумма штрафа",
    }

    def __init__(self, parent=None, violation: Violations | None = None):
        super().__init__(parent)
        self.setWindowTitle("Нарушение ПДД")
        self.setMinimumWidth(350)

        self.inputs = {}
        layout = QVBoxLayout(self)

        for field, label in self.FIELD_LABELS.items():
            layout.addWidget(QLabel(label))
            if field == "violation_date":
                edit = QDateEdit()
                edit.setDisplayFormat("yyyy-MM-dd")
                edit.setCalendarPopup(True)
                edit.setDate(QDate.currentDate())

                if violation:
                    edit.setDate(
                        QDate.fromString(
                            violation.violation_date,
                            "yyyy-MM-dd"
                        )
                    )
            else:
                edit = QLineEdit()
                if violation:
                    edit.setText(str(getattr(violation, field)))

            self.inputs[field] = edit
            layout.addWidget(edit)

        btn = QPushButton("Сохранить")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def accept(self):
        data = self.get_data()
        
        check_fields = [
            (data.brand, "Марка автомобиля"),
            (data.car_number, "Гос. номер"),
            (data.name, "ФИО"),
            (data.violation_type, "Тип нарушения"),
            (data.invoice_number, "Номер квитанции")
        ]
        
        for value, field_name in check_fields:
            if not value: # Если строка пустая после strip()
                QMessageBox.warning(self, "Ошибка валидации", f"Поле '{field_name}' не может быть пустым!")
                return # Прерываем закрытие диалога

        if data.payment_amount <= 0:
            QMessageBox.warning(self, "Ошибка валидации", "Сумма штрафа должна быть больше нуля!")
            return

        super().accept()

    def get_data(self) -> Violations:
        try:
            payment_value = float(self.inputs["payment_amount"].text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Ошибка валидации", "Сумма штрафа должна быть числом!")
            raise ValueError("Некорректная сумма штрафа")
        
        return Violations(
            id=None,
            brand=self.inputs["brand"].text().strip(),
            car_number=self.inputs["car_number"].text().strip(),
            violation_date=self.inputs["violation_date"]
                .date()
                .toString("yyyy-MM-dd"),
            name=self.inputs["name"].text().strip(),
            violation_type=self.inputs["violation_type"].text().strip(),
            invoice_number=self.inputs["invoice_number"].text().strip(),
            payment_amount=payment_value
        )
