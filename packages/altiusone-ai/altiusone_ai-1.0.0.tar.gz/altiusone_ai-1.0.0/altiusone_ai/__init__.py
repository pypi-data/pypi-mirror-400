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

    # Extract structured data
    data = client.extract(
        text="Facture N°123, montant: 1500 CHF",
        schema={"numero": "string", "montant": "number"}
    )
"""

from altiusone_ai.client import AltiusOneAI
from altiusone_ai.exceptions import (
    AltiusOneError,
    AuthenticationError,
    RateLimitError,
    APIError,
)

__version__ = "1.0.0"
__all__ = [
    "AltiusOneAI",
    "AltiusOneError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
]
