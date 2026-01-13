"""
AltiusOne AI SDK
================
Python SDK for AltiusOne AI Service.

Usage:
    from altiusone_ai import AltiusOneAI

    client = AltiusOneAI(
        api_url="https://ai.altiusone.ch",
        api_key="your-api-key"
    )

    # Generate embeddings
    embeddings = client.embed("Mon texte à vectoriser")

    # Chat
    response = client.chat("Bonjour!")

    # OCR
    text = client.ocr(image_path="document.pdf")

    # Extract with predefined schema
    from altiusone_ai.schemas import InvoiceSchema
    data = client.extract(
        text=invoice_text,
        schema=InvoiceSchema.schema(),
        source_language="fr",
        output_language="en"
    )

    # Extract with custom schema
    data = client.extract(
        text="Facture N°123, montant: 1500 CHF",
        schema={"invoice_number": "string", "amount": "number"}
    )
"""

from altiusone_ai.client import AltiusOneAI, AsyncAltiusOneAI
from altiusone_ai.exceptions import (
    AltiusOneError,
    AuthenticationError,
    RateLimitError,
    APIError,
)

__version__ = "1.1.0"
__all__ = [
    "AltiusOneAI",
    "AsyncAltiusOneAI",
    "AltiusOneError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
]
