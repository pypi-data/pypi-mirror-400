"""VIKK Legal AI Python Client.

A Python client library for integrating with VIKK Legal AI services.
"""

import os
from pathlib import Path
from typing import Optional

import httpx


class VikkAPIError(Exception):
    """Base exception for VIKK API errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class VikkAuthenticationError(VikkAPIError):
    """Raised when API authentication fails."""

    pass


class VikkRateLimitError(VikkAPIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class VikkAPIClient:
    """Python client for VIKK Legal AI API.

    This client provides a simple interface to interact with VIKK Legal AI
    services for document generation, PDF processing, and conversation import.

    Example:
        >>> from vikk_mcp.client import VikkAPIClient
        >>> client = VikkAPIClient(
        ...     api_url="https://lab.vikk.live",
        ...     api_key="vk_live_your_key_here"
        ... )
        >>> result = client.generate_document(
        ...     document_type="demand_letter",
        ...     title="Demand for Payment",
        ...     sender_name="John Smith",
        ...     sender_address="123 Main St, Los Angeles, CA 90001",
        ...     recipient_name="Jane Doe",
        ...     recipient_address="456 Oak Ave, San Francisco, CA 94102",
        ...     body="This letter demands payment of $5,000...",
        ... )
        >>> print(result["download_url"])
    """

    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
        timeout: float = 30.0,
    ):
        """Initialize the VIKK API client.

        Args:
            api_url: Base URL for the VIKK API. Defaults to VIKK_API_URL env var
                    or "https://lab.vikk.live".
            api_key: API key for authentication. Defaults to VIKK_API_KEY env var.
            timeout: Request timeout in seconds. Defaults to 30.0.

        Raises:
            ValueError: If no API key is provided.
        """
        self.api_url = (
            api_url or os.getenv("VIKK_API_URL", "https://lab.vikk.live")
        ).rstrip("/")
        self.api_key = api_key or os.getenv("VIKK_API_KEY")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "API key is required. Provide api_key parameter or set VIKK_API_KEY environment variable."
            )

        self._client = httpx.Client(
            base_url=self.api_url,
            headers={"X-API-Key": self.api_key},
            timeout=self.timeout,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        json: dict = None,
        params: dict = None,
        files: dict = None,
    ) -> dict:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API endpoint path
            json: JSON body for POST requests
            params: Query parameters
            files: Files to upload

        Returns:
            Response JSON as dict

        Raises:
            VikkAuthenticationError: If API key is invalid
            VikkRateLimitError: If rate limit is exceeded
            VikkAPIError: For other API errors
        """
        try:
            response = self._client.request(
                method=method,
                url=path,
                json=json,
                params=params,
                files=files,
            )

            if response.status_code == 401:
                raise VikkAuthenticationError(
                    "Invalid API key",
                    status_code=401,
                    response=response.json() if response.content else None,
                )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise VikkRateLimitError(
                    "Rate limit exceeded",
                    status_code=429,
                    retry_after=retry_after,
                    response=response.json() if response.content else None,
                )

            response.raise_for_status()
            return response.json() if response.content else {}

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)

            raise VikkAPIError(
                error_detail,
                status_code=e.response.status_code,
                response=e.response.json() if e.response.content else None,
            )

    def _request_bytes(self, method: str, path: str, params: dict = None) -> bytes:
        """Make an HTTP request and return raw bytes."""
        response = self._client.request(method=method, url=path, params=params)
        response.raise_for_status()
        return response.content

    # =========================================================================
    # Document Generation
    # =========================================================================

    def generate_document(
        self,
        document_type: str,
        title: str,
        sender_name: str,
        sender_address: str,
        recipient_name: str,
        recipient_address: str,
        body: str,
        date: str = None,
    ) -> dict:
        """Generate a legal document.

        Args:
            document_type: Type of document (demand_letter, cease_desist, notice,
                          agreement, letter)
            title: Document title/subject
            sender_name: Full name of the sender
            sender_address: Complete address of the sender
            recipient_name: Full name of the recipient
            recipient_address: Complete address of the recipient
            body: Main content/body of the document
            date: Date for the document (defaults to today)

        Returns:
            dict with document_id and download_url

        Example:
            >>> result = client.generate_document(
            ...     document_type="demand_letter",
            ...     title="Demand for Payment",
            ...     sender_name="John Smith",
            ...     sender_address="123 Main St, Los Angeles, CA 90001",
            ...     recipient_name="Jane Doe",
            ...     recipient_address="456 Oak Ave, San Francisco, CA 94102",
            ...     body="This letter demands payment of $5,000 for services rendered.",
            ... )
        """
        return self._request(
            "POST",
            "/api/v1/pdf/generate",
            json={
                "document_type": document_type,
                "title": title,
                "content": {
                    "date": date,
                    "sender": {"name": sender_name, "address": sender_address},
                    "recipient": {"name": recipient_name, "address": recipient_address},
                    "body": [body] if isinstance(body, str) else body,
                },
            },
        )

    def list_templates(self) -> list:
        """List available document templates.

        Returns:
            List of template definitions with type, description, and required_fields

        Example:
            >>> templates = client.list_templates()
            >>> for t in templates:
            ...     print(f"{t['type']}: {t['description']}")
        """
        result = self._request("GET", "/api/v1/pdf/usage")
        # The usage endpoint returns templates as part of the response
        # For a dedicated templates endpoint, we construct from known types
        return [
            {
                "type": "demand_letter",
                "description": "Formal demand letter for payment, property return, or action",
                "required_fields": [
                    "sender_name",
                    "sender_address",
                    "recipient_name",
                    "recipient_address",
                    "body",
                ],
            },
            {
                "type": "cease_desist",
                "description": "Cease and desist letter for stopping unwanted behavior",
                "required_fields": [
                    "sender_name",
                    "sender_address",
                    "recipient_name",
                    "recipient_address",
                    "body",
                ],
            },
            {
                "type": "notice",
                "description": "General legal notice",
                "required_fields": [
                    "sender_name",
                    "sender_address",
                    "recipient_name",
                    "recipient_address",
                    "body",
                ],
            },
            {
                "type": "agreement",
                "description": "Simple agreement between parties",
                "required_fields": [
                    "sender_name",
                    "sender_address",
                    "recipient_name",
                    "recipient_address",
                    "body",
                ],
            },
            {
                "type": "letter",
                "description": "Generic formal letter",
                "required_fields": [
                    "sender_name",
                    "sender_address",
                    "recipient_name",
                    "recipient_address",
                    "body",
                ],
            },
        ]

    # =========================================================================
    # PDF Processing
    # =========================================================================

    def extract_pdf_text(self, file_path: str) -> dict:
        """Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            dict with page_count, total_word_count, and pages array

        Example:
            >>> result = client.extract_pdf_text("/path/to/document.pdf")
            >>> print(f"Pages: {result['page_count']}")
            >>> for page in result['pages']:
            ...     print(f"Page {page['page_number']}: {page['text'][:100]}...")
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        # Step 1: Upload the PDF
        with open(file_path, "rb") as f:
            upload_result = self._request(
                "POST",
                "/api/v1/pdf-processing/upload",
                files={"file": (file_path.name, f, "application/pdf")},
            )

        document_id = upload_result["id"]

        # Step 2: Extract text
        extract_result = self._request(
            "POST",
            "/api/v1/pdf-processing/extract-text",
            json={"document_id": document_id},
        )

        return {
            "page_count": extract_result.get("total_pages", 0),
            "total_word_count": extract_result.get("total_word_count", 0),
            "pages": extract_result.get("pages", []),
        }

    # =========================================================================
    # Utility
    # =========================================================================

    def get_usage(self) -> dict:
        """Get API usage statistics.

        Returns:
            dict with total_requests, total_documents, and rate limits

        Example:
            >>> usage = client.get_usage()
            >>> print(f"Total requests: {usage['total_requests']}")
        """
        return self._request("GET", "/api/v1/pdf/usage")

    # =========================================================================
    # Conversation Import
    # =========================================================================

    def import_conversation(
        self, vikk_json: dict, allow_existing: bool = True
    ) -> dict:
        """Import a vikk.ai conversation.

        Args:
            vikk_json: Conversation in vikk.ai JSON format with UniqueID,
                      Conversation array, etc.
            allow_existing: If True, return existing session if UniqueID matches

        Returns:
            dict with conversation_id, message_count, and parsed_messages

        Example:
            >>> vikk_data = {
            ...     "UniqueID": "abc123",
            ...     "Conversation": [
            ...         {"prompt": "I need help", "response": "How can I help?"}
            ...     ]
            ... }
            >>> result = client.import_conversation(vikk_data)
            >>> print(f"Imported: {result['conversation_id']}")
        """
        return self._request(
            "POST",
            "/api/v1/chat/import-conversation",
            json={**vikk_json, "allow_existing": allow_existing},
        )

    def generate_from_conversation(
        self,
        conversation: list,
        document_type: str = None,
        conversation_id: str = None,
        generate_document: bool = True,
    ) -> dict:
        """Generate a document from a conversation.

        Args:
            conversation: List of messages with role and content
            document_type: Optional document type to generate
            conversation_id: Optional conversation ID for duplicate detection
            generate_document: Whether to generate the document (default True)

        Returns:
            dict with response, and optionally generated_document

        Example:
            >>> # After importing a conversation
            >>> result = client.generate_from_conversation(
            ...     conversation=import_result["parsed_messages"],
            ...     document_type="demand_letter",
            ...     conversation_id=import_result["conversation_id"]
            ... )
        """
        body = {
            "conversation": conversation,
            "generate_document": generate_document,
        }
        if document_type:
            body["document_type"] = document_type
        if conversation_id:
            body["conversation_id"] = conversation_id

        return self._request(
            "POST",
            "/api/v1/chat/generate-from-conversation",
            json=body,
        )

    def classify_intent(self, conversation: list) -> dict:
        """Classify if a conversation needs document generation.

        Args:
            conversation: List of messages with role and content

        Returns:
            dict with needs_document, confidence, suggested_document_type,
            missing_information, and summary

        Example:
            >>> result = client.classify_intent(conversation)
            >>> if result["needs_document"]:
            ...     print(f"Suggested: {result['suggested_document_type']}")
        """
        return self._request(
            "POST",
            "/api/v1/chat/classify-intent",
            json={"conversation": conversation},
        )

    # =========================================================================
    # Session Management
    # =========================================================================

    def list_sessions(self, limit: int = 10) -> list:
        """List conversation sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session summaries

        Example:
            >>> sessions = client.list_sessions(limit=5)
            >>> for s in sessions:
            ...     print(f"{s['id']}: {s.get('title', 'Untitled')}")
        """
        result = self._request(
            "GET",
            "/api/v1/chat/sessions",
            params={"limit": limit},
        )
        return result.get("sessions", [])

    def get_session(self, session_id: str) -> dict:
        """Get a specific session with messages.

        Args:
            session_id: The session ID

        Returns:
            Session details with messages

        Example:
            >>> session = client.get_session("uuid-here")
            >>> print(f"Messages: {len(session['messages'])}")
        """
        return self._request("GET", f"/api/v1/chat/sessions/{session_id}")

    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session.

        Args:
            session_id: The session ID to delete

        Returns:
            True if deleted successfully

        Example:
            >>> if client.delete_session("uuid-here"):
            ...     print("Session deleted")
        """
        self._request("DELETE", f"/api/v1/chat/sessions/{session_id}")
        return True

    # =========================================================================
    # Document Download
    # =========================================================================

    def download_document(
        self, document_id: str, output_path: str = None, source: str = "chat"
    ) -> str:
        """Download a generated document.

        Args:
            document_id: The document ID
            output_path: Where to save the file (defaults to document_{id}.pdf)
            source: "chat" for chat-generated docs, "pdf" for direct generation

        Returns:
            Path to the downloaded file

        Example:
            >>> path = client.download_document("uuid-here")
            >>> print(f"Saved to: {path}")
        """
        if source == "chat":
            endpoint = f"/api/v1/chat/documents/{document_id}/download"
        else:
            endpoint = f"/api/v1/pdf/download/{document_id}"

        content = self._request_bytes("GET", endpoint)

        if not output_path:
            output_path = f"document_{document_id[:8]}.pdf"

        Path(output_path).write_bytes(content)
        return output_path
