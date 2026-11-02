from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.documents.extraction import Invoice, PurchaseOrder


@dataclass(frozen=True)
class ComparisonIssue:
    issue_type: str
    message: str
    invoice_value: str
    purchase_order_value: str


@dataclass(frozen=True)
class ComparisonResult:
    invoice_number: str
    purchase_order_number: str
    status: str
    total_difference: Decimal
    issues: tuple[ComparisonIssue, ...]


def compare_invoice_to_purchase_order(
    invoice: Invoice,
    purchase_order: PurchaseOrder,
) -> ComparisonResult:
    """Compare an invoice with its related purchase order."""
    issues: list[ComparisonIssue] = []

    check_same_value(
        issues,
        issue_type="vendor_mismatch",
        message="Invoice and purchase order have different vendors.",
        invoice_value=invoice.vendor,
        purchase_order_value=purchase_order.vendor,
    )
    check_same_value(
        issues,
        issue_type="currency_mismatch",
        message="Invoice and purchase order use different currencies.",
        invoice_value=invoice.currency,
        purchase_order_value=purchase_order.currency,
    )
    check_same_value(
        issues,
        issue_type="purchase_order_number_mismatch",
        message="Invoice references a different purchase order number.",
        invoice_value=invoice.purchase_order_number,
        purchase_order_value=purchase_order.purchase_order_number,
    )

    total_difference = invoice.total - purchase_order.total
    if total_difference != Decimal("0"):
        issues.append(
            ComparisonIssue(
                issue_type="purchase_order_amount_mismatch",
                message="Invoice total is different from the purchase order total.",
                invoice_value=str(invoice.total),
                purchase_order_value=str(purchase_order.total),
            )
        )

    return ComparisonResult(
        invoice_number=invoice.invoice_number,
        purchase_order_number=invoice.purchase_order_number,
        status="mismatch" if issues else "match",
        total_difference=total_difference,
        issues=tuple(issues),
    )


def check_same_value(
    issues: list[ComparisonIssue],
    issue_type: str,
    message: str,
    invoice_value: str,
    purchase_order_value: str,
) -> None:
    """Add an issue when two values are different."""
    if invoice_value != purchase_order_value:
        issues.append(
            ComparisonIssue(
                issue_type=issue_type,
                message=message,
                invoice_value=invoice_value,
                purchase_order_value=purchase_order_value,
            )
        )
