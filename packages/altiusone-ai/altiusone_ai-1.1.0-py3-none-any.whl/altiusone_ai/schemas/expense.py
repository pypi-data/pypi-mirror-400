"""
AltiusOne AI SDK - Expense Report Schema
========================================
Predefined schema for expense report extraction.
"""

from typing import Any, Dict


# Raw schema dictionary
EXPENSE_SCHEMA: Dict[str, Any] = {
    "report_number": "string?",
    "report_date": "string",
    "period": {
        "start_date": "string",
        "end_date": "string",
    },
    "employee": {
        "name": "string",
        "employee_id": "string?",
        "department": "string?",
        "manager": "string?",
    },
    "expenses": [{
        "date": "string",
        "category": "string",
        "description": "string",
        "vendor": "string?",
        "amount": "number",
        "currency": "string",
        "payment_method": "string?",
        "receipt_attached": "boolean?",
        "billable": "boolean?",
        "project_code": "string?",
    }],
    "totals_by_category": [{
        "category": "string",
        "total": "number",
    }],
    "total_amount": "number",
    "currency": "string",
    "reimbursable_amount": "number?",
    "non_reimbursable_amount": "number?",
    "advance_received": "number?",
    "balance_due": "number?",
    "status": "string?",
    "approval": {
        "approver_name": "string?",
        "approval_date": "string?",
        "comments": "string?",
    },
}


class ExpenseSchema:
    """
    Expense report extraction schema.

    Extracts:
    - Report metadata
    - Employee information
    - Individual expenses with categories
    - Totals and reimbursement info
    - Approval status

    Example:
        ```python
        from altiusone_ai import AltiusOneAI
        from altiusone_ai.schemas import ExpenseSchema

        client = AltiusOneAI(api_url="https://ai.altiusone.ch", api_key="...")

        data = client.extract(
            text=expense_report_text,
            schema=ExpenseSchema.schema()
        )
        ```
    """

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Get the full expense report schema dictionary."""
        return EXPENSE_SCHEMA.copy()

    @staticmethod
    def minimal() -> Dict[str, Any]:
        """Get a minimal expense schema (essential fields only)."""
        return {
            "employee_name": "string",
            "report_date": "string",
            "expenses": [{
                "date": "string",
                "category": "string",
                "description": "string",
                "amount": "number",
            }],
            "total_amount": "number",
            "currency": "string",
        }

    @staticmethod
    def travel() -> Dict[str, Any]:
        """Get schema for travel expense reports."""
        return {
            "report_date": "string",
            "employee": {
                "name": "string",
                "employee_id": "string?",
                "department": "string?",
            },
            "trip": {
                "purpose": "string",
                "destination": "string",
                "start_date": "string",
                "end_date": "string",
            },
            "transportation": [{
                "type": "string",
                "description": "string",
                "amount": "number",
                "currency": "string",
            }],
            "accommodation": [{
                "hotel_name": "string?",
                "check_in": "string",
                "check_out": "string",
                "nights": "number",
                "amount": "number",
                "currency": "string",
            }],
            "meals": [{
                "date": "string",
                "type": "string",
                "amount": "number",
                "currency": "string",
            }],
            "other_expenses": [{
                "category": "string",
                "description": "string",
                "amount": "number",
                "currency": "string",
            }],
            "per_diem_claimed": "number?",
            "total_amount": "number",
            "currency": "string",
        }

    @staticmethod
    def receipt() -> Dict[str, Any]:
        """Get schema for individual receipt extraction."""
        return {
            "vendor_name": "string",
            "vendor_address": "string?",
            "date": "string",
            "time": "string?",
            "items": [{
                "description": "string",
                "quantity": "number?",
                "unit_price": "number?",
                "total": "number",
            }],
            "subtotal": "number?",
            "tax_amount": "number?",
            "tip_amount": "number?",
            "total_amount": "number",
            "currency": "string",
            "payment_method": "string?",
            "card_last_four": "string?",
            "receipt_number": "string?",
        }

    @staticmethod
    def with_custom_fields(**fields: str) -> Dict[str, Any]:
        """Get expense schema with additional custom fields."""
        schema = EXPENSE_SCHEMA.copy()
        schema.update(fields)
        return schema
