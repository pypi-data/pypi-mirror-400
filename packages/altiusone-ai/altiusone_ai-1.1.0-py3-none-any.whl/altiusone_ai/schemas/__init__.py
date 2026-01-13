"""
AltiusOne AI SDK - Predefined Schemas
=====================================
Ready-to-use extraction schemas for common document types.

Nomenclature Rules:
-------------------
- Field names: snake_case (e.g., invoice_number, total_amount)
- Language: English (technical standard)
- Types:
    - "string"      -> Text value
    - "number"      -> Numeric value (int or float)
    - "boolean"     -> True/False
    - "string[]"    -> List of strings
    - {...}         -> Nested object
    - [{...}]       -> List of objects
- Optional fields: Add "?" suffix (e.g., "string?", "number?")

Example Custom Schema:
----------------------
```python
my_schema = {
    "company_name": "string",
    "revenue": "number",
    "is_active": "boolean",
    "tags": "string[]",
    "notes": "string?",  # Optional
    "address": {
        "street": "string",
        "city": "string",
        "postal_code": "string",
        "country": "string?"
    },
    "contacts": [{
        "name": "string",
        "email": "string",
        "phone": "string?"
    }]
}
```
"""

from altiusone_ai.schemas.invoice import InvoiceSchema, INVOICE_SCHEMA
from altiusone_ai.schemas.contract import ContractSchema, CONTRACT_SCHEMA
from altiusone_ai.schemas.resume import ResumeSchema, RESUME_SCHEMA
from altiusone_ai.schemas.identity import IdentitySchema, IDENTITY_SCHEMA
from altiusone_ai.schemas.quote import QuoteSchema, QUOTE_SCHEMA
from altiusone_ai.schemas.expense import ExpenseSchema, EXPENSE_SCHEMA

__all__ = [
    # Schema classes (with helper methods)
    "InvoiceSchema",
    "ContractSchema",
    "ResumeSchema",
    "IdentitySchema",
    "QuoteSchema",
    "ExpenseSchema",
    # Raw schema dictionaries
    "INVOICE_SCHEMA",
    "CONTRACT_SCHEMA",
    "RESUME_SCHEMA",
    "IDENTITY_SCHEMA",
    "QUOTE_SCHEMA",
    "EXPENSE_SCHEMA",
]
