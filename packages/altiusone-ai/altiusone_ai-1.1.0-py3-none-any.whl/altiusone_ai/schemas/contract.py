"""
AltiusOne AI SDK - Contract Schema
==================================
Predefined schema for contract extraction.
"""

from typing import Any, Dict


# Raw schema dictionary
CONTRACT_SCHEMA: Dict[str, Any] = {
    "contract_type": "string",
    "contract_number": "string?",
    "title": "string",
    "effective_date": "string",
    "expiration_date": "string?",
    "parties": [{
        "role": "string",
        "name": "string",
        "address": "string?",
        "representative": "string?",
    }],
    "purpose": "string",
    "key_terms": "string[]",
    "obligations": [{
        "party": "string",
        "description": "string",
    }],
    "payment_terms": {
        "amount": "number?",
        "currency": "string?",
        "schedule": "string?",
        "conditions": "string?",
    },
    "termination_conditions": "string[]?",
    "governing_law": "string?",
    "jurisdiction": "string?",
    "signatures": [{
        "party": "string",
        "signatory_name": "string?",
        "date": "string?",
    }],
    "attachments": "string[]?",
}


class ContractSchema:
    """
    Contract extraction schema.

    Extracts:
    - Contract metadata (type, number, dates)
    - Parties involved
    - Purpose and key terms
    - Obligations per party
    - Payment terms
    - Legal clauses

    Example:
        ```python
        from altiusone_ai import AltiusOneAI
        from altiusone_ai.schemas import ContractSchema

        client = AltiusOneAI(api_url="https://ai.altiusone.ch", api_key="...")

        data = client.extract(
            text=contract_text,
            schema=ContractSchema.schema()
        )
        ```
    """

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Get the contract schema dictionary."""
        return CONTRACT_SCHEMA.copy()

    @staticmethod
    def employment() -> Dict[str, Any]:
        """Get schema for employment contracts."""
        return {
            "contract_type": "string",
            "employer": {
                "name": "string",
                "address": "string?",
            },
            "employee": {
                "name": "string",
                "address": "string?",
                "birth_date": "string?",
                "nationality": "string?",
            },
            "job_title": "string",
            "department": "string?",
            "start_date": "string",
            "end_date": "string?",
            "contract_duration": "string?",
            "probation_period": "string?",
            "work_location": "string?",
            "work_hours": "string?",
            "salary": {
                "gross_amount": "number",
                "currency": "string",
                "payment_frequency": "string",
            },
            "benefits": "string[]?",
            "vacation_days": "number?",
            "notice_period": "string?",
            "non_compete_clause": "boolean?",
            "confidentiality_clause": "boolean?",
        }

    @staticmethod
    def rental() -> Dict[str, Any]:
        """Get schema for rental/lease contracts."""
        return {
            "contract_type": "string",
            "landlord": {
                "name": "string",
                "address": "string?",
            },
            "tenant": {
                "name": "string",
                "address": "string?",
            },
            "property": {
                "address": "string",
                "type": "string?",
                "size_sqm": "number?",
                "rooms": "number?",
            },
            "start_date": "string",
            "end_date": "string?",
            "rent": {
                "amount": "number",
                "currency": "string",
                "payment_day": "number?",
                "charges_included": "boolean?",
            },
            "deposit": {
                "amount": "number?",
                "currency": "string?",
            },
            "notice_period": "string?",
            "allowed_use": "string?",
            "restrictions": "string[]?",
        }

    @staticmethod
    def with_custom_fields(**fields: str) -> Dict[str, Any]:
        """Get contract schema with additional custom fields."""
        schema = CONTRACT_SCHEMA.copy()
        schema.update(fields)
        return schema
