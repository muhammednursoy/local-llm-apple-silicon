import io
import os
import unittest
from contextlib import redirect_stdout
from datetime import date
from decimal import Decimal

from expenses.__main__ import main
from expenses.models import Record
from expenses.report import monthly_summary

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "data", "sample.csv")


def rec(day, category, amount):
    return Record(date.fromisoformat(day), category, Decimal(amount))


class MonthlySummaryTest(unittest.TestCase):
    def test_category_totals_largest_first(self):
        records = [rec("2026-10-01", "groceries", "100.50"), rec("2026-10-02", "transport", "300"), rec("2026-10-03", "groceries", "50")]
        self.assertEqual(monthly_summary(records, 2026, 10), [("transport", Decimal("300")), ("groceries", Decimal("150.50"))])

    def test_refund_reduces_total(self):
        records = [rec("2026-10-01", "groceries", "100"), rec("2026-10-05", "groceries", "-40")]
        self.assertEqual(monthly_summary(records, 2026, 10), [("groceries", Decimal("60"))])

    def test_other_months_not_counted(self):
        records = [rec("2026-09-30", "groceries", "100"), rec("2025-10-15", "groceries", "70")]
        self.assertEqual(monthly_summary(records, 2026, 10), [])

    def test_cli_month_option(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main([SAMPLE, "--month", "2026-10"])
        self.assertEqual(out.getvalue().splitlines(), [
            "rent       18,000.00",
            "groceries  1,100.40",
            "transport  415.50",
        ])

    def test_cli_without_option_lists_unchanged(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main([SAMPLE])
        self.assertEqual(len(out.getvalue().splitlines()), 7)
