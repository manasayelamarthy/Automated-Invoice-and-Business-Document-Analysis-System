from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.documents.processing import InvoiceReview, review_invoice
from app.documents.workspace import UserWorkspace, WorkspaceError


class ReviewRequest(BaseModel):
    invoice_filename: str
    purchase_order_filename: str


repository_root = Path(__file__).resolve().parents[1]
workspace = UserWorkspace(repository_root / "data")
app = FastAPI(title="AI Document Intelligence Platform", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return (repository_root / "web" / "index.html").read_text(encoding="utf-8")


@app.get("/api/users")
def list_users() -> list[dict[str, str]]:
    try:
        users = workspace.users_file.read_text(encoding="utf-8")
        return [
            {"user_id": user["user_id"], "display_name": user["display_name"]}
            for user in json.loads(users)
        ]
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=500, detail="Unable to load users") from error


@app.get("/api/users/{user_id}/documents")
def list_documents(user_id: str) -> list[dict[str, object]]:
    try:
        return [
            {
                "filename": document.filename,
                "document_type": document.document_type,
                "size_bytes": document.size_bytes,
            }
            for document in workspace.list_documents(user_id)
        ]
    except WorkspaceError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/users/{user_id}/review")
def review(user_id: str, request: ReviewRequest) -> dict[str, object]:
    try:
        result = review_invoice(
            workspace,
            user_id,
            request.invoice_filename,
            request.purchase_order_filename,
        )
    except (WorkspaceError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return serialize_review(result)


def serialize_review(result: InvoiceReview) -> dict[str, object]:
    comparison = result.comparison
    return {
        "invoice_filename": result.invoice_filename,
        "purchase_order_filename": result.purchase_order_filename,
        "invoice_number": comparison.invoice_number,
        "purchase_order_number": comparison.purchase_order_number,
        "status": comparison.status,
        "total_difference": str(comparison.total_difference),
        "issues": [
            {
                "type": issue.issue_type,
                "message": issue.message,
                "invoice_value": issue.invoice_value,
                "purchase_order_value": issue.purchase_order_value,
            }
            for issue in comparison.issues
        ],
        "duplicate_invoices": [
            {
                "invoice_number": duplicate.invoice_number,
                "filenames": duplicate.duplicate_filenames,
                "vendor": duplicate.vendor,
                "total": str(duplicate.total),
            }
            for duplicate in result.duplicate_invoices
        ],
    }
