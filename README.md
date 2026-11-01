# AI Document Intelligence Platform

Phase 1 is a document intelligence platform for isolated user workspaces.
It currently supports synthetic invoices, purchase orders, and contracts.

## Current capabilities

- Load documents from a specific user's workspace
- Prevent cross-user workspace access
- Classify invoice, purchase-order, and contract documents
- Extract typed invoice and purchase-order fields
- Parse financial amounts using `Decimal`
- Validate required fields, dates, and numeric values

## Run tests

```powershell
python -m unittest discover -s .\tests -v
```

## List a user's documents

```powershell
python -m app.documents.cli user_001
```

Synthetic data is stored under `data/`. The `data/fixtures/` directory is the
shared test reference, while `data/users/user_001`, `data/users/user_002`, and
`data/users/user_003` represent isolated user workspaces.
