from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton
)
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

        self.inputs = {}
        layout = QVBoxLayout(self)

        for field, label in self.FIELD_LABELS.items():
            layout.addWidget(QLabel(label))

            edit = QLineEdit()
            if violation:
                edit.setText(str(getattr(violation, field)))
            self.inputs[field] = edit
            layout.addWidget(edit)

        btn = QPushButton("Сохранить")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_data(self) -> Violations:
        return Violations(
            id=None,
            brand=self.inputs["brand"].text(),
            car_number=self.inputs["car_number"].text(),
            violation_date=self.inputs["violation_date"].text(),
            name=self.inputs["name"].text(),
            violation_type=self.inputs["violation_type"].text(),
            invoice_number=self.inputs["invoice_number"].text(),
            payment_amount=float(self.inputs["payment_amount"].text())
        )
