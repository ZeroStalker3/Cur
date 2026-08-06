from dataclasses import dataclass

@dataclass
class Violations:
    id: int | None
    brand: str
    car_number: str
    violation_date: str
    name: str
    violation_type: str
    invoice_number: str
    payment_amount: float
    
    def __post_init__(self):
        if self.brand is not None and not self.brand.strip():
            raise ValueError("Марка автомобиля не может быть пустой")
        if self.car_number is not None and not self.car_number.strip():
            raise ValueError("Гос. номер не может быть пустым")
        if self.name is not None and not self.name.strip():
            raise ValueError("ФИО не может быть пустым")
        if self.payment_amount is not None and self.payment_amount < 0:
            raise ValueError("Сумма штрафа не может быть отрицательной")