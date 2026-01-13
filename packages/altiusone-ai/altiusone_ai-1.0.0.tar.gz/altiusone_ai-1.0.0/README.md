# AltiusOne AI SDK

Python SDK for AltiusOne AI Service - OCR, Embeddings, Chat, and Extraction.

## Installation

```bash
pip install altiusone-ai
```

Or install from source:

```bash
pip install git+https://github.com/akouni/altiusoneai.git#subdirectory=sdk/python
```

## Quick Start

```python
from altiusone_ai import AltiusOneAI

# Initialize client
client = AltiusOneAI(
    api_url="https://ai.altiusone.ch",
    api_key="your-api-key"
)

# Generate embeddings (768 dimensions, compatible with pgvector)
embeddings = client.embed("Mon texte à vectoriser")

# Chat with AI
response = client.chat("Bonjour, comment allez-vous?")

# OCR on image or PDF
text = client.ocr(image_path="document.pdf")

# Extract structured data
data = client.extract(
    text="Facture N° 2024-001\nMontant: CHF 1'500.00",
    schema={
        "numero_facture": "string",
        "montant": "number",
        "devise": "string"
    }
)
```

## Features

### Embeddings

Generate 768-dimensional vectors compatible with pgvector:

```python
# Single text
embedding = client.embed("Mon texte")[0]

# Batch
embeddings = client.embed(texts=["Texte 1", "Texte 2", "Texte 3"])

# Store in PostgreSQL with pgvector
cursor.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    (text, embedding)
)
```

### Chat

Conversational AI with system prompts:

```python
# Simple message
response = client.chat("Bonjour!")

# With system prompt
response = client.chat(
    "Comment déclarer la TVA?",
    system="Tu es un expert comptable suisse."
)

# Full conversation
response = client.chat(messages=[
    {"role": "system", "content": "Tu es un assistant pour une fiduciaire."},
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Bonjour! Comment puis-je vous aider?"},
    {"role": "user", "content": "Explique-moi la TVA suisse"}
])
```

### OCR

Extract text from images and PDFs:

```python
# From file
text = client.ocr(image_path="document.pdf")

# From bytes
with open("image.png", "rb") as f:
    text = client.ocr(image_data=f.read())

# From URL
text = client.ocr(image_url="https://example.com/doc.png")

# With language hint
text = client.ocr(image_path="document.pdf", language="fr")
```

### Extraction

Extract structured data from text:

```python
# Invoice extraction
invoice_data = client.extract(
    text="""
    Facture N° 2024-001
    Date: 15.01.2024
    Client: Entreprise XYZ SA
    Montant HT: CHF 1'200.00
    TVA (7.7%): CHF 92.40
    Montant TTC: CHF 1'292.40
    """,
    schema={
        "numero_facture": "string",
        "date": "string",
        "client": "string",
        "montant_ht": "number",
        "tva": "number",
        "montant_ttc": "number"
    }
)
```

## Async Support

```python
from altiusone_ai import AsyncAltiusOneAI

async def main():
    async with AsyncAltiusOneAI(api_url, api_key) as client:
        embeddings = await client.embed("Mon texte")
        response = await client.chat("Bonjour!")
```

## Error Handling

```python
from altiusone_ai import (
    AltiusOneAI,
    AuthenticationError,
    RateLimitError,
    APIError,
)

try:
    response = client.chat("Hello")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Too many requests, please wait")
except APIError as e:
    print(f"API error: {e}")
```

## Django Integration

```python
# settings.py
ALTIUSONE_AI_URL = "https://ai.altiusone.ch"
ALTIUSONE_AI_KEY = os.environ["ALTIUSONE_API_KEY"]

# services.py
from django.conf import settings
from altiusone_ai import AltiusOneAI

def get_ai_client():
    return AltiusOneAI(
        api_url=settings.ALTIUSONE_AI_URL,
        api_key=settings.ALTIUSONE_AI_KEY,
    )

# views.py
def search_documents(request):
    query = request.GET.get("q")
    client = get_ai_client()

    # Generate query embedding
    query_embedding = client.embed(query)[0]

    # Search with pgvector
    documents = Document.objects.raw("""
        SELECT *, embedding <=> %s AS distance
        FROM documents
        ORDER BY distance
        LIMIT 10
    """, [query_embedding])

    return JsonResponse({"results": list(documents)})
```

## License

Proprietary - AltiusOne SA
