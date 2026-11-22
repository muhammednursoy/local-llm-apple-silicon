import os
import unittest
from datetime import date
from decimal import Decimal

from expenses.store import load, parse_amount

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "data", "sample.csv")


class StoreTest(unittest.TestCase):
    def test_parse_amount(self):
        self.assertEqual(parse_amount("1.250,40"), Decimal("1250.40"))
        self.assertEqual(parse_amount("-150,00"), Decimal("-150.00"))

    def test_load(self):
        records = load(SAMPLE)
        self.assertEqual(len(records), 7)
        self.assertEqual(records[2].category, "transport")
        self.assertEqual(records[0].date, date(2026, 9, 28))
