# Phase 1 fixture dataset

These files are synthetic examples for local development and testing. They do
not contain real customer or financial information.

## Files

### Invoices

- `invoice_inv_1001.txt` - normal invoice linked to `po_2001.txt`
- `invoice_inv_1002.txt` - total exceeds linked PO
- `invoice_inv_1003.txt` - duplicate invoice number and amount of `invoice_inv_1002.txt`

### Purchase orders

- `po_2001.txt` - matches `invoice_inv_1001.txt`
- `po_2002.txt` - lower total than `invoice_inv_1002.txt` and `invoice_inv_1003.txt`

### Contracts

- `contract_acme_2026.txt` - includes a late-delivery penalty clause
- `contract_nova_2026.txt` - includes payment and delivery terms for a second vendor

## Expected Phase 1 checks

1. `invoice_inv_1001.txt` should pass the basic invoice-to-PO comparison.
2. `invoice_inv_1002.txt` should produce a purchase-order amount mismatch.
3. `invoice_inv_1003.txt` should produce a duplicate-invoice warning.
4. A semantic search for `late delivery penalty` should retrieve
   `contract_acme_2026.txt`, page 2.
