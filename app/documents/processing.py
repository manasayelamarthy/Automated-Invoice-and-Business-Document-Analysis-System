from __future__ import annotations

from dataclasses import dataclass

from app.documents.anomalies import DuplicateInvoice, find_duplicate_invoices
from app.documents.comparison import ComparisonResult, compare_invoice_to_purchase_order
from app.documents.extraction import Invoice, PurchaseOrder, extract_document
from app.documents.workspace import UserWorkspace


@dataclass(frozen=True)
class InvoiceReview:
    invoice_filename: str
    purchase_order_filename: str
    comparison: ComparisonResult
    duplicate_invoices: tuple[DuplicateInvoice, ...]


def review_invoice(
    workspace: UserWorkspace,
    user_id: str,
    invoice_filename: str,
    purchase_order_filename: str,
) -> InvoiceReview:
    invoice = read_invoice(workspace, user_id, invoice_filename)
    purchase_order = read_purchase_order(workspace, user_id, purchase_order_filename)
    comparison = compare_invoice_to_purchase_order(invoice, purchase_order)
    duplicates = find_duplicates_for_user(workspace, user_id)
    return InvoiceReview(invoice_filename, purchase_order_filename, comparison, duplicates)


def read_invoice(workspace: UserWorkspace, user_id: str, filename: str) -> Invoice:
    result = extract_document(workspace.read_document(user_id, filename))
    if not isinstance(result, Invoice):
        raise ValueError(f"{filename} is not an invoice")
    return result


def read_purchase_order(
    workspace: UserWorkspace,
    user_id: str,
    filename: str,
) -> PurchaseOrder:
    result = extract_document(workspace.read_document(user_id, filename))
    if not isinstance(result, PurchaseOrder):
        raise ValueError(f"{filename} is not a purchase order")
    return result


def find_duplicates_for_user(
    workspace: UserWorkspace,
    user_id: str,
) -> tuple[DuplicateInvoice, ...]:
    invoices: list[tuple[str, Invoice]] = []
    for document in workspace.list_documents(user_id):
        if document.document_type == "invoice":
            invoices.append((document.filename, read_invoice(workspace, user_id, document.filename)))
    return find_duplicate_invoices(invoices)
