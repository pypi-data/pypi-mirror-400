"""
AltiusOne AI SDK - Invoice Schema
=================================
Predefined schema for invoice extraction.
"""

from typing import Any, Dict


# Raw schema dictionary
INVOICE_SCHEMA: Dict[str, Any] = {
    "invoice_number": "string",
    "invoice_date": "string",
    "due_date": "string?",
    "vendor": {
        "name": "string",
        "address": "string?",
        "vat_number": "string?",
        "phone": "string?",
        "email": "string?",
    },
    "customer": {
        "name": "string",
        "address": "string?",
        "vat_number": "string?",
    },
    "line_items": [{
        "description": "string",
        "quantity": "number",
        "unit_price": "number",
        "total": "number",
        "vat_rate": "number?",
    }],
    "subtotal": "number",
    "vat_amount": "number?",
    "total_amount": "number",
    "currency": "string",
    "payment_terms": "string?",
    "payment_reference": "string?",
    "iban": "string?",
    "notes": "string?",
}


class InvoiceSchema:
    """
    Invoice extraction schema.

    Extracts:
    - Invoice metadata (number, dates)
    - Vendor information
    - Customer information
    - Line items with quantities and prices
    - Totals and VAT
    - Payment information

    Example:
        ```python
        from altiusone_ai import AltiusOneAI
        from altiusone_ai.schemas import InvoiceSchema

        client = AltiusOneAI(api_url="https://ai.altiusone.ch", api_key="...")

        # Extract invoice data
        data = client.extract(
            text=invoice_text,
            schema=InvoiceSchema.schema(),
            source_language="auto",
            output_language="fr"
        )
        ```
    """

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Get the invoice schema dictionary."""
        return INVOICE_SCHEMA.copy()

    @staticmethod
    def minimal() -> Dict[str, Any]:
        """Get a minimal invoice schema (essential fields only)."""
        return {
            "invoice_number": "string",
            "invoice_date": "string",
            "vendor_name": "string",
            "customer_name": "string",
            "total_amount": "number",
            "currency": "string",
        }

    @staticmethod
    def with_custom_fields(**fields: str) -> Dict[str, Any]:
        """
        Get invoice schema with additional custom fields.

        Args:
            **fields: Custom field definitions (field_name="type")

        Example:
            schema = InvoiceSchema.with_custom_fields(
                project_code="string",
                department="string?"
            )
        """
        schema = INVOICE_SCHEMA.copy()
        schema.update(fields)
        return schema
