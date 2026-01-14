# VIKK Legal AI MCP Server

MCP (Model Context Protocol) server for integrating VIKK Legal AI with Claude Desktop and Claude Code.

## Overview

This MCP server provides tools for:
- Generating legal documents (demand letters, cease & desist, notices, agreements)
- Chatting with VIKK Legal AI assistant
- Extracting text from PDF files
- Managing chat sessions

## Quick Start (Recommended)

The easiest way to use this MCP server is with `uvx` - no installation required!

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "vikk-legal": {
      "command": "uvx",
      "args": ["vikk-legal-mcp"],
      "env": {
        "VIKK_API_URL": "https://lab.vikk.live",
        "VIKK_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Then restart Claude Desktop (Cmd+Q on macOS).

### Get an API Key

Contact VIKK AI technical support.

## Available Tools

### Document Generation

| Tool | Description |
|------|-------------|
| `generate_document` | Create legal documents (demand letters, cease & desist, notices, etc.) |
| `list_document_templates` | List available document types and required fields |

### Chat

| Tool | Description |
|------|-------------|
| `chat_with_vikk` | Have a conversation with VIKK Legal AI |
| `get_session_history` | Retrieve conversation history for a session |
| `list_chat_sessions` | List recent chat sessions |

### PDF Processing

| Tool | Description |
|------|-------------|
| `extract_pdf_text` | Extract text from a local PDF file |

### Utility

| Tool | Description |
|------|-------------|
| `get_api_usage` | Check API usage and rate limits |

## Available Resources

| URI | Description |
|-----|-------------|
| `vikk://templates` | Document templates reference |
| `vikk://usage` | API usage statistics |

## Examples

### Generate a Demand Letter

```
"Generate a demand letter for unpaid rent. The landlord is John Smith at 123 Main St,
Anytown CA 90210. The tenant is Jane Doe at 456 Oak Ave, Anytown CA 90211.
The amount owed is $2,500 for March and April rent."
```

### Chat with VIKK

```
"Chat with VIKK about how to write a cease and desist letter for trademark infringement."
```

### Extract PDF Text

```
"Extract the text from /Users/me/Documents/contract.pdf"
```

## Troubleshooting

### Server not appearing in Claude Desktop

1. Verify the config file path and JSON syntax
2. Use absolute paths (not relative)
3. Fully restart Claude Desktop (Cmd+Q on macOS)
4. Check logs: `tail -f ~/Library/Logs/Claude/mcp*.log`

### API errors

1. Verify VIKK_API_KEY is set correctly
2. Check that the API URL is accessible
3. Ensure your API key has not expired
4. Check rate limits with `get_api_usage`

### Connection refused

1. Verify the VIKK server is running
2. Check the API URL is correct (include protocol: http/https)
3. Check firewall settings

## License

MIT License
