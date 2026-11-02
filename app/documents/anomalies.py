from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.documents.extraction import Invoice


@dataclass(frozen=True)
class DuplicateInvoice:
    invoice_number: str
    duplicate_filenames: tuple[str, ...]
    vendor: str
    total: Decimal


def find_duplicate_invoices(
    invoices: list[tuple[str, Invoice]],
) -> tuple[DuplicateInvoice, ...]:
    """Find invoices with the same vendor, number, date, and total."""
    groups: dict[tuple[str, str, object, Decimal], list[str]] = {}
    for filename, invoice in invoices:
        key = (
            invoice.vendor,
            invoice.invoice_number,
            invoice.invoice_date,
            invoice.total,
        )
        groups.setdefault(key, []).append(filename)

    duplicates: list[DuplicateInvoice] = []
    for key, filenames in groups.items():
        if len(filenames) > 1:
            duplicates.append(
                DuplicateInvoice(
                    invoice_number=key[1],
                    duplicate_filenames=tuple(filenames),
                    vendor=key[0],
                    total=key[3],
                )
            )
    return tuple(duplicates)
