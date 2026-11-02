from pathlib import Path
import unittest
from decimal import Decimal

from app.documents.processing import review_invoice
from app.documents.workspace import UserWorkspace


class InvoiceReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        self.workspace = UserWorkspace(repository_root / "data")

    def test_review_reports_mismatch_and_duplicate(self) -> None:
        review = review_invoice(
            self.workspace,
            "user_001",
            "invoice_inv_1002.txt",
            "po_2002.txt",
        )

        self.assertEqual(review.comparison.status, "mismatch")
        self.assertEqual(review.comparison.total_difference, Decimal("8260.00"))
        self.assertEqual(len(review.duplicate_invoices), 1)
        self.assertEqual(
            review.duplicate_invoices[0].duplicate_filenames,
            ("invoice_inv_1002.txt", "invoice_inv_1003.txt"),
        )


if __name__ == "__main__":
    unittest.main()
