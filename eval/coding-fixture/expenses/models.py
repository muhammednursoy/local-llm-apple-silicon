from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Record:
    date: date
    category: str
    amount: Decimal
    note: str = ""
