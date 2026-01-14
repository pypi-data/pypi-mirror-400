"""VIKK Legal AI MCP Server for Claude Desktop and Claude Code integration."""

import logging
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from vikk_mcp.config import config

# Configure logging to stderr (required for stdio transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("vikk-legal")


async def _make_request(
    method: str,
    endpoint: str,
    data: dict | None = None,
    files: dict | None = None,
    params: dict | None = None,
) -> dict[str, Any]:
    """Make authenticated request to VIKK API."""
    headers = {"X-API-Key": config.api_key}
    url = f"{config.api_url}{endpoint}"

    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                if files:
                    response = await client.post(url, headers=headers, files=files)
                else:
                    response = await client.post(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise


# === DOCUMENT GENERATION TOOLS ===

@mcp.tool()
async def generate_document(
    document_type: str,
    title: str,
    sender_name: str,
    sender_address: str,
    recipient_name: str,
    recipient_address: str,
    body: str,
    date: str | None = None,
) -> str:
    """Generate a legal document (demand_letter, cease_desist, notice, agreement, letter).

    Args:
        document_type: Type of document - one of: demand_letter, cease_desist, notice, agreement, letter
        title: Document title/subject
        sender_name: Full name of the sender
        sender_address: Complete address of the sender
        recipient_name: Full name of the recipient
        recipient_address: Complete address of the recipient
        body: Main content/body of the document
        date: Optional date for the document (defaults to today)
    """
    try:
        from datetime import datetime
        doc_date = date or datetime.now().strftime("%B %d, %Y")

        result = await _make_request("POST", "/api/v1/pdf/generate", {
            "document_type": document_type,
            "title": title,
            "content": {
                "date": doc_date,
                "sender": {"name": sender_name, "address": sender_address},
                "recipient": {"name": recipient_name, "address": recipient_address},
                "body": [body] if isinstance(body, str) else body,
            }
        })

        download_url = f"{config.api_url}/api/v1/pdf/public/{result['id']}"
        return f"""Document generated successfully!

Document ID: {result['id']}
Type: {document_type}
Title: {title}

Download URL: {download_url}

You can share this URL with the user to download the document."""
    except Exception as e:
        logger.error(f"Error generating document: {e}")
        return f"Error generating document: {str(e)}"


@mcp.tool()
async def list_document_templates() -> str:
    """List available document templates and their required fields."""
    templates = """
Available Document Templates:

1. demand_letter - Formal demand for action
   Use for: Security deposit demands, debt collection, breach of contract
   Required fields: sender (name, address), recipient (name, address), body (demand details)

2. cease_desist - Cease and desist letter
   Use for: Harassment, copyright infringement, defamation
   Required fields: sender (name, address), recipient (name, address), body (violation details)

3. notice - Legal notice
   Use for: Eviction notices, termination notices, intent to sue
   Required fields: sender (name, address), recipient (name, address), body (notice content)

4. agreement - Simple agreement/contract
   Use for: Service agreements, simple contracts, MOUs
   Required fields: sender (name, address), recipient (name, address), body (agreement terms)

5. letter - Generic formal letter
   Use for: Any formal correspondence
   Required fields: sender (name, address), recipient (name, address), body (letter content)

To generate a document, use the generate_document tool with:
- document_type: One of the types above
- title: Document title
- sender_name: Your full name
- sender_address: Your complete address
- recipient_name: Recipient's full name
- recipient_address: Recipient's complete address
- body: The main content of the document
"""
    return templates


# === PDF PROCESSING TOOLS ===

@mcp.tool()
async def extract_pdf_text(file_path: str) -> str:
    """Extract text from a local PDF file.

    This uploads the PDF to VIKK and extracts the text content.
    Useful for analyzing contracts, legal documents, or any PDF.

    Args:
        file_path: Absolute path to the PDF file on your local machine
    """
    try:
        # Read local file
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Upload the PDF
        files = {"file": ("document.pdf", file_content, "application/pdf")}
        upload_result = await _make_request("POST", "/api/v1/pdf-processing/upload", files=files)

        doc_id = upload_result["id"]

        # Extract text
        extract_result = await _make_request("POST", "/api/v1/pdf-processing/extract-text", {
            "document_id": doc_id
        })

        output = f"""Extracted Text from: {file_path}

Total Pages: {extract_result.get('total_pages', 0)}
Total Words: {extract_result.get('total_word_count', 0)}

"""

        for page in extract_result.get("pages", []):
            output += f"--- Page {page['page_number']} ({page['word_count']} words) ---\n"
            # Limit text output per page
            text = page["text"]
            if len(text) > 3000:
                text = text[:3000] + "\n...(truncated)"
            output += text + "\n\n"

        return output
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"Error extracting text: {str(e)}"


@mcp.tool()
async def get_api_usage() -> str:
    """Get API usage statistics for the current API key.

    Shows request counts, documents generated, and rate limits.
    """
    try:
        result = await _make_request("GET", "/api/v1/pdf/usage")

        output = """API Usage Statistics:

"""
        output += f"Total Requests: {result.get('total_requests', 0)}\n"
        output += f"Documents Generated: {result.get('documents_generated', 0)}\n"
        output += f"Period: {result.get('period', 'N/A')}\n"

        if result.get("rate_limit"):
            rl = result["rate_limit"]
            output += f"\nRate Limits:\n"
            output += f"- Per Minute: {rl.get('per_minute', 'N/A')}\n"
            output += f"- Per Day: {rl.get('per_day', 'N/A')}\n"

        return output
    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        return f"Error retrieving usage statistics: {str(e)}"


# === RESOURCES ===

@mcp.resource("vikk://templates")
async def list_templates_resource() -> str:
    """List all available document templates."""
    return await list_document_templates()


@mcp.resource("vikk://usage")
async def usage_resource() -> str:
    """Get API usage statistics."""
    return await get_api_usage()


def main():
    """Run the MCP server."""
    logger.info("Starting VIKK Legal AI MCP Server")
    logger.info(f"API URL: {config.api_url}")
    logger.info(f"API Key configured: {'Yes' if config.api_key else 'No'}")

    if not config.api_key:
        logger.warning("No API key configured! Set VIKK_API_KEY environment variable.")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
