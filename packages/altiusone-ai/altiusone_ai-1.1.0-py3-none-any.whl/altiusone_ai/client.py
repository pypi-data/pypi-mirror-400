"""
AltiusOne AI SDK - Client
=========================
Main client for interacting with AltiusOne AI Service.
"""

import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx

from altiusone_ai.exceptions import (
    AltiusOneError,
    AuthenticationError,
    RateLimitError,
    APIError,
)


class AltiusOneAI:
    """
    AltiusOne AI Service Client.

    Usage:
        client = AltiusOneAI(
            api_url="https://ai.altiusone.ch",
            api_key="your-api-key"
        )

        # Embeddings
        embeddings = client.embed("Mon texte")

        # Chat
        response = client.chat("Bonjour!")
    """

    def __init__(
        self,
        api_url: str,
        api_key: str,
        timeout: int = 300,
    ):
        """
        Initialize AltiusOne AI client.

        Args:
            api_url: Base URL of the AI service
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.api_url,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        return self._client

    def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = endpoint

        try:
            if files:
                # Multipart request for file uploads
                response = self.client.request(
                    method,
                    url,
                    files=files,
                    data=data,
                )
            else:
                response = self.client.request(
                    method,
                    url,
                    json=data,
                )

            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "60")
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds"
                )
            elif response.status_code >= 400:
                error_data = response.json()
                raise APIError(
                    error_data.get("message", "Unknown error"),
                    status_code=response.status_code,
                )

            return response.json()

        except httpx.TimeoutException as e:
            raise AltiusOneError(f"Request timed out: {e}")
        except httpx.RequestError as e:
            raise AltiusOneError(f"Request failed: {e}")

    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """
        Check service health.

        Returns:
            Health status including Ollama connection state
        """
        return self._request("GET", "/health")

    # -------------------------------------------------------------------------
    # Embeddings
    # -------------------------------------------------------------------------

    def embed(
        self,
        text: Optional[str] = None,
        texts: Optional[List[str]] = None,
    ) -> List[List[float]]:
        """
        Generate embeddings for text(s).

        Args:
            text: Single text to embed
            texts: Multiple texts to embed (batch)

        Returns:
            List of 768-dimensional embedding vectors

        Example:
            # Single text
            embedding = client.embed("Mon texte")[0]

            # Multiple texts
            embeddings = client.embed(texts=["Texte 1", "Texte 2"])
        """
        data = {}
        if text:
            data["text"] = text
        if texts:
            data["texts"] = texts

        response = self._request("POST", "/embeddings", data=data)
        return response["embeddings"]

    # -------------------------------------------------------------------------
    # Chat
    # -------------------------------------------------------------------------

    def chat(
        self,
        message: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate chat response.

        Args:
            message: Simple user message
            messages: Full conversation history
            system: System prompt
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum response tokens

        Returns:
            Assistant response text

        Example:
            # Simple chat
            response = client.chat("Bonjour!")

            # With system prompt
            response = client.chat(
                "Comment déclarer la TVA?",
                system="Tu es un expert comptable suisse."
            )

            # Full conversation
            response = client.chat(messages=[
                {"role": "system", "content": "Tu es un assistant."},
                {"role": "user", "content": "Bonjour"},
                {"role": "assistant", "content": "Bonjour! Comment puis-je vous aider?"},
                {"role": "user", "content": "Explique-moi la TVA"}
            ])
        """
        if messages is None:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            if message:
                messages.append({"role": "user", "content": message})

        if not messages:
            raise ValueError("Must provide message or messages")

        data = {
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            data["max_tokens"] = max_tokens

        response = self._request("POST", "/chat", data=data)
        return response["message"]

    # -------------------------------------------------------------------------
    # OCR
    # -------------------------------------------------------------------------

    def ocr(
        self,
        image_path: Optional[Union[str, Path]] = None,
        image_data: Optional[bytes] = None,
        image_url: Optional[str] = None,
        language: str = "auto",
    ) -> str:
        """
        Perform OCR on image or PDF.

        Args:
            image_path: Path to image or PDF file
            image_data: Raw image bytes
            image_url: URL to image
            language: Language hint (auto, fr, de, en, it)

        Returns:
            Extracted text

        Example:
            # From file
            text = client.ocr(image_path="document.pdf")

            # From bytes
            with open("image.png", "rb") as f:
                text = client.ocr(image_data=f.read())

            # From URL
            text = client.ocr(image_url="https://example.com/doc.png")
        """
        data = {"language": language}

        if image_path:
            path = Path(image_path)
            with open(path, "rb") as f:
                file_data = f.read()

            if path.suffix.lower() == ".pdf":
                data["pdf_base64"] = base64.b64encode(file_data).decode("utf-8")
            else:
                data["image_base64"] = base64.b64encode(file_data).decode("utf-8")

        elif image_data:
            data["image_base64"] = base64.b64encode(image_data).decode("utf-8")

        elif image_url:
            data["image_url"] = image_url

        else:
            raise ValueError("Must provide image_path, image_data, or image_url")

        response = self._request("POST", "/ocr", data=data)
        return response["text"]

    def ocr_file(
        self,
        file_path: Union[str, Path],
        language: str = "auto",
    ) -> str:
        """
        Perform OCR using multipart file upload.

        Args:
            file_path: Path to image or PDF file
            language: Language hint

        Returns:
            Extracted text
        """
        path = Path(file_path)

        with open(path, "rb") as f:
            files = {"file": (path.name, f, "application/octet-stream")}
            response = self._request(
                "POST",
                "/ocr/file",
                data={"language": language},
                files=files,
            )

        return response["text"]

    # -------------------------------------------------------------------------
    # Extract
    # -------------------------------------------------------------------------

    def extract(
        self,
        text: str,
        schema: Dict[str, Any],
        instructions: Optional[str] = None,
        source_language: str = "auto",
        output_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured data from text.

        Args:
            text: Text to extract from
            schema: Expected output structure (use predefined or custom)
            instructions: Additional extraction instructions
            source_language: Source document language (auto, en, fr, de, it, pt)
            output_language: Output language for extracted values

        Returns:
            Extracted data matching schema

        Example with custom schema:
            data = client.extract(
                text="Facture N° 2024-001\\nMontant: CHF 1'500.00",
                schema={
                    "invoice_number": "string",
                    "amount": "number",
                    "currency": "string"
                }
            )

        Example with predefined schema:
            from altiusone_ai.schemas import InvoiceSchema

            data = client.extract(
                text=invoice_text,
                schema=InvoiceSchema.schema(),
                source_language="fr",
                output_language="en"
            )

        Example with multilingual support:
            # Extract from German document, output in French
            data = client.extract(
                text=german_contract,
                schema=ContractSchema.schema(),
                source_language="de",
                output_language="fr"
            )
        """
        data: Dict[str, Any] = {
            "text": text,
            "schema": schema,
            "source_language": source_language,
        }
        if instructions:
            data["instructions"] = instructions
        if output_language:
            data["output_language"] = output_language

        response = self._request("POST", "/extract", data=data)
        return response["data"]


# Async client
class AsyncAltiusOneAI:
    """
    Async AltiusOne AI Service Client.

    Usage:
        async with AsyncAltiusOneAI(api_url, api_key) as client:
            embeddings = await client.embed("Mon texte")
    """

    def __init__(
        self,
        api_url: str,
        api_key: str,
        timeout: int = 300,
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make async HTTP request."""
        try:
            response = await self._client.request(method, endpoint, json=data)

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_data = response.json()
                raise APIError(error_data.get("message", "Unknown error"))

            return response.json()

        except httpx.TimeoutException as e:
            raise AltiusOneError(f"Request timed out: {e}")

    async def embed(
        self,
        text: Optional[str] = None,
        texts: Optional[List[str]] = None,
    ) -> List[List[float]]:
        """Generate embeddings (async)."""
        data = {}
        if text:
            data["text"] = text
        if texts:
            data["texts"] = texts

        response = await self._request("POST", "/embeddings", data=data)
        return response["embeddings"]

    async def chat(
        self,
        message: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate chat response (async)."""
        if messages is None:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            if message:
                messages.append({"role": "user", "content": message})

        response = await self._request(
            "POST",
            "/chat",
            data={"messages": messages, "temperature": temperature},
        )
        return response["message"]

    async def extract(
        self,
        text: str,
        schema: Dict[str, Any],
        instructions: Optional[str] = None,
        source_language: str = "auto",
        output_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured data (async).

        Args:
            text: Text to extract from
            schema: Expected output structure
            instructions: Additional extraction instructions
            source_language: Source document language (auto, en, fr, de, it, pt)
            output_language: Output language for extracted values
        """
        data: Dict[str, Any] = {
            "text": text,
            "schema": schema,
            "source_language": source_language,
        }
        if instructions:
            data["instructions"] = instructions
        if output_language:
            data["output_language"] = output_language

        response = await self._request("POST", "/extract", data=data)
        return response["data"]
