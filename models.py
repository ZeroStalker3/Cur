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