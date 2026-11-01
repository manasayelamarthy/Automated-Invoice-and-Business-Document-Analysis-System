from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


class ExtractionError(ValueError):
    """Raised when a supported document cannot be extracted safely."""


@dataclass(frozen=True)
class LineItem:
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal


@dataclass(frozen=True)
class FinancialDocument:
    document_type: str
    vendor: str
    currency: str
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    line_items: tuple[LineItem, ...]


@dataclass(frozen=True)
class Invoice(FinancialDocument):
    invoice_number: str
    invoice_date: date
    purchase_order_number: str
    payment_terms: str


@dataclass(frozen=True)
class PurchaseOrder(FinancialDocument):
    purchase_order_number: str
    order_date: date
    delivery_due: date


_FIELD_PATTERN = re.compile(r"^(?P<name>[^:]+):\s*(?P<value>.+)$")
_LINE_ITEM_PATTERN = re.compile(
    r"^\d+\.\s*(?P<description>.+?)\s*\|\s*"
    r"Quantity:\s*(?P<quantity>[\d.]+)\s*\|\s*"
    r"Unit Price:\s*(?P<unit_price>[\d.]+)\s*\|\s*"
    r"Amount:\s*(?P<amount>[\d.]+)$"
)


def extract_document(text: str) -> Invoice | PurchaseOrder:
    fields, line_items = _parse_common(text)
    document_type = _first_line(text).upper()

    if document_type == "INVOICE":
        return Invoice(
            document_type="invoice",
            vendor=_required(fields, "Vendor"),
            currency=_required(fields, "Currency"),
            subtotal=_decimal(fields, "Subtotal"),
            tax_rate=_decimal(fields, "GST Rate", strip_suffix="%"),
            tax_amount=_decimal(fields, "GST Amount"),
            total=_decimal(fields, "Total"),
            line_items=tuple(line_items),
            invoice_number=_required(fields, "Invoice Number"),
            invoice_date=_date(fields, "Invoice Date"),
            purchase_order_number=_required(fields, "Purchase Order Number"),
            payment_terms=_required(fields, "Payment Terms"),
        )

    if document_type == "PURCHASE ORDER":
        return PurchaseOrder(
            document_type="purchase_order",
            vendor=_required(fields, "Vendor"),
            currency=_required(fields, "Currency"),
            subtotal=_decimal(fields, "Subtotal"),
            tax_rate=_decimal(fields, "GST Rate", strip_suffix="%"),
            tax_amount=_decimal(fields, "GST Amount"),
            total=_decimal(fields, "Total"),
            line_items=tuple(line_items),
            purchase_order_number=_required(fields, "Purchase Order Number"),
            order_date=_date(fields, "Order Date"),
            delivery_due=_date(fields, "Delivery Due"),
        )

    raise ExtractionError(f"Unsupported document type: {document_type or '<empty>'}")


def _parse_common(text: str) -> tuple[dict[str, str], list[LineItem]]:
    fields: dict[str, str] = {}
    line_items: list[LineItem] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        item_match = _LINE_ITEM_PATTERN.match(line)
        if item_match:
            line_items.append(
                LineItem(
                    description=item_match.group("description").strip(),
                    quantity=_to_decimal(item_match.group("quantity"), "Quantity"),
                    unit_price=_to_decimal(item_match.group("unit_price"), "Unit Price"),
                    amount=_to_decimal(item_match.group("amount"), "Amount"),
                )
            )
            continue

        field_match = _FIELD_PATTERN.match(line)
        if field_match:
            fields[field_match.group("name").strip()] = field_match.group("value").strip()
    return fields, line_items


def _first_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def _required(fields: dict[str, str], name: str) -> str:
    value = fields.get(name)
    if not value:
        raise ExtractionError(f"Missing required field: {name}")
    return value


def _decimal(fields: dict[str, str], name: str, strip_suffix: str = "") -> Decimal:
    value = _required(fields, name)
    if strip_suffix and value.endswith(strip_suffix):
        value = value[: -len(strip_suffix)].strip()
    return _to_decimal(value, name)


def _to_decimal(value: str, field_name: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as error:
        raise ExtractionError(f"Invalid numeric value for {field_name}: {value}") from error


def _date(fields: dict[str, str], name: str) -> date:
    value = _required(fields, name)
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ExtractionError(f"Invalid date for {name}: {value}") from error
