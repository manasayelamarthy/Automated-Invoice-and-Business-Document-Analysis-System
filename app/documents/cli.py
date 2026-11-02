from __future__ import annotations

import argparse
from pathlib import Path

from app.documents.processing import review_invoice
from app.documents.workspace import UserWorkspace


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect one user's documents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List user documents")
    list_parser.add_argument("user_id", help="User ID from data/users.json")

    compare_parser = subparsers.add_parser("compare", help="Compare an invoice with a purchase order")
    compare_parser.add_argument("user_id", help="User ID from data/users.json")
    compare_parser.add_argument("invoice_filename")
    compare_parser.add_argument("purchase_order_filename")
    args = parser.parse_args()

    repository_root = Path(__file__).resolve().parents[2]
    workspace = UserWorkspace(repository_root / "data")
    if args.command == "list":
        for document in workspace.list_documents(args.user_id):
            print(f"{document.document_type}\t{document.filename}\t{document.size_bytes} bytes")
        return

    review = review_invoice(
        workspace,
        args.user_id,
        args.invoice_filename,
        args.purchase_order_filename,
    )
    comparison = review.comparison
    print(f"Invoice: {comparison.invoice_number}")
    print(f"Purchase order: {comparison.purchase_order_number}")
    print(f"Status: {comparison.status}")
    print(f"Total difference: {comparison.total_difference}")
    for issue in comparison.issues:
        print(f"Issue: {issue.message}")
    for duplicate in review.duplicate_invoices:
        print(f"Duplicate invoices: {', '.join(duplicate.duplicate_filenames)}")


if __name__ == "__main__":
    main()
