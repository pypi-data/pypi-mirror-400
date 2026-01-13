"""
AltiusOne AI SDK - Quote Schema
===============================
Predefined schema for quote/estimate extraction.
"""

from typing import Any, Dict


# Raw schema dictionary
QUOTE_SCHEMA: Dict[str, Any] = {
    "quote_number": "string",
    "quote_date": "string",
    "valid_until": "string?",
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
        "contact_person": "string?",
    },
    "project_name": "string?",
    "project_description": "string?",
    "line_items": [{
        "description": "string",
        "quantity": "number",
        "unit": "string?",
        "unit_price": "number",
        "total": "number",
        "notes": "string?",
    }],
    "subtotal": "number",
    "discount": {
        "type": "string?",
        "value": "number?",
    },
    "vat_rate": "number?",
    "vat_amount": "number?",
    "total_amount": "number",
    "currency": "string",
    "payment_terms": "string?",
    "delivery_terms": "string?",
    "warranty": "string?",
    "terms_and_conditions": "string?",
    "notes": "string?",
}


class QuoteSchema:
    """
    Quote/Estimate extraction schema.

    Extracts:
    - Quote metadata (number, dates, validity)
    - Vendor information
    - Customer information
    - Project details
    - Line items with quantities and prices
    - Discounts and totals
    - Terms and conditions

    Example:
        ```python
        from altiusone_ai import AltiusOneAI
        from altiusone_ai.schemas import QuoteSchema

        client = AltiusOneAI(api_url="https://ai.altiusone.ch", api_key="...")

        data = client.extract(
            text=quote_text,
            schema=QuoteSchema.schema()
        )
        ```
    """

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Get the full quote schema dictionary."""
        return QUOTE_SCHEMA.copy()

    @staticmethod
    def minimal() -> Dict[str, Any]:
        """Get a minimal quote schema (essential fields only)."""
        return {
            "quote_number": "string",
            "quote_date": "string",
            "valid_until": "string?",
            "vendor_name": "string",
            "customer_name": "string",
            "total_amount": "number",
            "currency": "string",
        }

    @staticmethod
    def construction() -> Dict[str, Any]:
        """Get schema for construction quotes."""
        return {
            "quote_number": "string",
            "quote_date": "string",
            "valid_until": "string?",
            "contractor": {
                "name": "string",
                "address": "string?",
                "license_number": "string?",
            },
            "client": {
                "name": "string",
                "address": "string?",
            },
            "project": {
                "name": "string",
                "location": "string",
                "description": "string?",
            },
            "work_items": [{
                "category": "string",
                "description": "string",
                "quantity": "number",
                "unit": "string",
                "unit_price": "number",
                "total": "number",
            }],
            "materials_cost": "number?",
            "labor_cost": "number?",
            "subtotal": "number",
            "vat_amount": "number?",
            "total_amount": "number",
            "currency": "string",
            "estimated_duration": "string?",
            "start_date": "string?",
            "payment_schedule": "string?",
            "warranty_period": "string?",
        }

    @staticmethod
    def services() -> Dict[str, Any]:
        """Get schema for service quotes."""
        return {
            "quote_number": "string",
            "quote_date": "string",
            "valid_until": "string?",
            "provider": {
                "name": "string",
                "address": "string?",
            },
            "client": {
                "name": "string",
                "address": "string?",
            },
            "service_description": "string",
            "services": [{
                "name": "string",
                "description": "string?",
                "hours": "number?",
                "hourly_rate": "number?",
                "fixed_price": "number?",
                "total": "number",
            }],
            "subtotal": "number",
            "vat_amount": "number?",
            "total_amount": "number",
            "currency": "string",
            "delivery_date": "string?",
            "payment_terms": "string?",
        }

    @staticmethod
    def with_custom_fields(**fields: str) -> Dict[str, Any]:
        """Get quote schema with additional custom fields."""
        schema = QUOTE_SCHEMA.copy()
        schema.update(fields)
        return schema
