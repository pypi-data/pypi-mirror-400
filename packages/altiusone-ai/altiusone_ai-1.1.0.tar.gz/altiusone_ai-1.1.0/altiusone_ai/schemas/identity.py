"""
AltiusOne AI SDK - Identity Document Schema
===========================================
Predefined schema for identity document extraction.
"""

from typing import Any, Dict


# Raw schema dictionary
IDENTITY_SCHEMA: Dict[str, Any] = {
    "document_type": "string",
    "document_number": "string",
    "issuing_country": "string",
    "issuing_authority": "string?",
    "issue_date": "string?",
    "expiry_date": "string?",
    "personal_info": {
        "surname": "string",
        "given_names": "string",
        "date_of_birth": "string",
        "place_of_birth": "string?",
        "gender": "string?",
        "nationality": "string",
        "height": "string?",
        "eye_color": "string?",
    },
    "address": {
        "street": "string?",
        "city": "string?",
        "postal_code": "string?",
        "country": "string?",
    },
    "mrz": "string?",
    "is_valid": "boolean?",
}


class IdentitySchema:
    """
    Identity document extraction schema.

    Supports:
    - Passports
    - National ID cards
    - Driving licenses
    - Residence permits

    Extracts:
    - Document metadata (type, number, validity)
    - Personal information
    - Address (if present)
    - Machine Readable Zone (MRZ)

    Example:
        ```python
        from altiusone_ai import AltiusOneAI
        from altiusone_ai.schemas import IdentitySchema

        client = AltiusOneAI(api_url="https://ai.altiusone.ch", api_key="...")

        # For passport
        data = client.extract(
            text=passport_text,
            schema=IdentitySchema.passport()
        )

        # For driving license
        data = client.extract(
            text=license_text,
            schema=IdentitySchema.driving_license()
        )
        ```
    """

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Get the general identity document schema."""
        return IDENTITY_SCHEMA.copy()

    @staticmethod
    def passport() -> Dict[str, Any]:
        """Get schema for passports."""
        return {
            "document_type": "string",
            "passport_number": "string",
            "issuing_country": "string",
            "issuing_authority": "string?",
            "issue_date": "string",
            "expiry_date": "string",
            "surname": "string",
            "given_names": "string",
            "date_of_birth": "string",
            "place_of_birth": "string",
            "gender": "string",
            "nationality": "string",
            "mrz_line1": "string?",
            "mrz_line2": "string?",
        }

    @staticmethod
    def national_id() -> Dict[str, Any]:
        """Get schema for national ID cards."""
        return {
            "document_type": "string",
            "id_number": "string",
            "issuing_country": "string",
            "issue_date": "string?",
            "expiry_date": "string?",
            "surname": "string",
            "given_names": "string",
            "date_of_birth": "string",
            "place_of_birth": "string?",
            "gender": "string?",
            "nationality": "string",
            "address": "string?",
        }

    @staticmethod
    def driving_license() -> Dict[str, Any]:
        """Get schema for driving licenses."""
        return {
            "document_type": "string",
            "license_number": "string",
            "issuing_country": "string",
            "issuing_authority": "string?",
            "issue_date": "string",
            "expiry_date": "string",
            "surname": "string",
            "given_names": "string",
            "date_of_birth": "string",
            "place_of_birth": "string?",
            "address": "string?",
            "categories": "string[]",
            "restrictions": "string[]?",
        }

    @staticmethod
    def residence_permit() -> Dict[str, Any]:
        """Get schema for residence permits."""
        return {
            "document_type": "string",
            "permit_number": "string",
            "permit_type": "string",
            "issuing_country": "string",
            "issue_date": "string",
            "expiry_date": "string",
            "surname": "string",
            "given_names": "string",
            "date_of_birth": "string",
            "nationality": "string",
            "address": "string?",
            "employer": "string?",
            "remarks": "string?",
        }

    @staticmethod
    def with_custom_fields(**fields: str) -> Dict[str, Any]:
        """Get identity schema with additional custom fields."""
        schema = IDENTITY_SCHEMA.copy()
        schema.update(fields)
        return schema
