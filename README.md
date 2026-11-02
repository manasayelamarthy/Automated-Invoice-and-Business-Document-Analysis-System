# AI Document Intelligence Platform

Phase 1 is a document intelligence platform for isolated user workspaces.
It currently supports synthetic invoices, purchase orders, and contracts.

## Current capabilities

- Load documents from a specific user's workspace
- Prevent cross-user workspace access
- Classify invoice, purchase-order, and contract documents
- Extract typed invoice and purchase-order fields
- Compare invoices with purchase orders
- Detect vendor, currency, reference-number, and total mismatches
- Parse financial amounts using `Decimal`
- Validate required fields, dates, and numeric values

## Run tests

```powershell
python -m unittest discover -s .\tests -v
```

## List a user's documents

```powershell
python -m app.documents.cli list user_001
```

Compare an invoice with its purchase order:

```powershell
python -m app.documents.cli compare user_001 invoice_inv_1002.txt po_2002.txt
```

## Run the Phase 1 browser platform

Install the project dependencies:

```powershell
pip install -e .
```

Start the web server:

```powershell
uvicorn app.web:app --reload
```

Open `http://127.0.0.1:8000` in a browser. Select a user workspace, inspect
its documents, and compare an invoice with a purchase order.

Synthetic data is stored under `data/`. The `data/fixtures/` directory is the
shared test reference, while `data/users/user_001`, `data/users/user_002`, and
`data/users/user_003` represent isolated user workspaces.
