from decimal import Decimal
from pathlib import Path
import unittest

from app.documents.comparison import compare_invoice_to_purchase_order
from app.documents.extraction import Invoice, PurchaseOrder, extract_document
from app.documents.workspace import UserWorkspace


class DocumentComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        self.workspace = UserWorkspace(repository_root / "data")

    def read_invoice(self, filename: str) -> Invoice:
        text = self.workspace.read_document("user_001", filename)
        result = extract_document(text)
        self.assertIsInstance(result, Invoice)
        return result

    def read_purchase_order(self, filename: str) -> PurchaseOrder:
        text = self.workspace.read_document("user_001", filename)
        result = extract_document(text)
        self.assertIsInstance(result, PurchaseOrder)
        return result

    def test_matching_invoice_and_purchase_order(self) -> None:
        result = compare_invoice_to_purchase_order(
            self.read_invoice("invoice_inv_1001.txt"),
            self.read_purchase_order("po_2001.txt"),
        )

        self.assertEqual(result.status, "match")
        self.assertEqual(result.total_difference, Decimal("0"))
        self.assertEqual(result.issues, ())

    def test_detects_purchase_order_amount_mismatch(self) -> None:
        result = compare_invoice_to_purchase_order(
            self.read_invoice("invoice_inv_1002.txt"),
            self.read_purchase_order("po_2002.txt"),
        )

        self.assertEqual(result.status, "mismatch")
        self.assertEqual(result.total_difference, Decimal("8260.00"))
        self.assertEqual(result.issues[0].issue_type, "purchase_order_amount_mismatch")
        self.assertEqual(len(result.issues), 1)


if __name__ == "__main__":
    unittest.main()
