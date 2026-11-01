from pathlib import Path
import unittest
from decimal import Decimal

from app.documents.extraction import ExtractionError, Invoice, PurchaseOrder, extract_document
from app.documents.workspace import UserWorkspace


class DocumentExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        self.workspace = UserWorkspace(repository_root / "data")

    def test_extracts_invoice_fields_and_line_items(self) -> None:
        text = self.workspace.read_document("user_001", "invoice_inv_1002.txt")

        result = extract_document(text)

        self.assertIsInstance(result, Invoice)
        self.assertEqual(result.invoice_number, "INV-1002")
        self.assertEqual(result.purchase_order_number, "PO-2002")
        self.assertEqual(result.total, Decimal("96760.00"))
        self.assertEqual(result.tax_rate, Decimal("18"))
        self.assertEqual(len(result.line_items), 2)

    def test_extracts_purchase_order_fields_and_line_items(self) -> None:
        text = self.workspace.read_document("user_001", "po_2002.txt")

        result = extract_document(text)

        self.assertIsInstance(result, PurchaseOrder)
        self.assertEqual(result.purchase_order_number, "PO-2002")
        self.assertEqual(result.total, Decimal("88500.00"))
        self.assertEqual(result.delivery_due.isoformat(), "2026-10-20")
        self.assertEqual(result.line_items[0].description, "Height-adjustable desks")

    def test_rejects_missing_required_field(self) -> None:
        incomplete_invoice = """\
INVOICE
Vendor: Example
Currency: INR
Subtotal: 100.00
GST Rate: 18%
GST Amount: 18.00
"""
        with self.assertRaisesRegex(ExtractionError, "Missing required field: Total"):
            extract_document(incomplete_invoice)


if __name__ == "__main__":
    unittest.main()
