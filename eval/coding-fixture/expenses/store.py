import csv
from datetime import date
from decimal import Decimal

from .models import Record


def parse_amount(text):
    return Decimal(text.strip().replace(".", "").replace(",", "."))


def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return [
            Record(date.fromisoformat(r["date"]), r["category"].strip().lower(), parse_amount(r["amount"]), r.get("note", ""))
            for r in csv.DictReader(f, delimiter=";")
        ]
