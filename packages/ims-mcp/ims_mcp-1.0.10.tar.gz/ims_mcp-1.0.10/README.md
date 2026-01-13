# ims-mcp

**Model Context Protocol (MCP) server for Rosetta (Enterprise Engineering Governance and Instructions Management System)**

*Powered by R2R technology for advanced RAG capabilities*

This package provides a FastMCP server that connects to IMS servers for advanced retrieval-augmented generation (RAG) capabilities. It enables AI assistants like Claude Desktop, Cursor, and other MCP clients to search, retrieve, and manage documents in Rosetta knowledge bases.

## Features

- 🔍 **Semantic Search** - Vector-based and full-text search across documents
- 🤖 **RAG Queries** - Retrieval-augmented generation with configurable LLM settings
- 📝 **Document Management** - Upload, update, list, and delete documents with upsert semantics
- 🏷️ **Metadata Filtering** - Advanced filtering by tags, domain, and custom metadata
- 🌐 **Environment-Based Config** - Zero configuration, reads from environment variables

## Installation

### Using uvx (recommended)

The easiest way to use ims-mcp is with `uvx`, which automatically handles installation:

```bash
uvx ims-mcp
```

### Using pip

Install globally or in a virtual environment:

```bash
pip install ims-mcp
```

Then run:

```bash
ims-mcp
```

### As a Python Module

You can also run it as a module:

```bash
python -m ims_mcp
```

## Configuration

The server automatically reads configuration from environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `R2R_API_BASE` or `R2R_BASE_URL` | IMS server URL | `http://localhost:7272` |
| `R2R_COLLECTION` | Collection name for queries | Server default |
| `R2R_API_KEY` | API key for authentication | None |
| `R2R_EMAIL` | Email for authentication (requires R2R_PASSWORD) | None |
| `R2R_PASSWORD` | Password for authentication (requires R2R_EMAIL) | None |
| `IMS_DEBUG` | Enable debug logging to stderr (1/true/yes/on) | None (disabled) |

**Authentication Priority:**
1. If `R2R_API_KEY` is set, it will be used
2. If `R2R_EMAIL` and `R2R_PASSWORD` are set, they will be used to login and obtain an access token
3. If neither is set, the client will attempt unauthenticated access (works for local servers)

**Note:** Environment variables use `R2R_` prefix for compatibility with the underlying R2R SDK.

## Usage with MCP Clients

### Cursor IDE

**Local server (no authentication):**

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "KnowledgeBase": {
      "command": "uvx",
      "args": ["ims-mcp"],
      "env": {
        "R2R_API_BASE": "http://localhost:7272",
        "R2R_COLLECTION": "aia-r1"
      }
    }
  }
}
```

**Remote server (with email/password authentication):**

```json
{
  "mcpServers": {
    "KnowledgeBase": {
      "command": "uvx",
      "args": ["ims-mcp"],
      "env": {
        "R2R_API_BASE": "https://your-server.example.com/",
        "R2R_COLLECTION": "your-collection",
        "R2R_EMAIL": "your-email@example.com",
        "R2R_PASSWORD": "your-password"
      }
    }
  }
}
```

### Claude Desktop

Add to Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ims": {
      "command": "uvx",
      "args": ["ims-mcp"],
      "env": {
        "R2R_API_BASE": "http://localhost:7272",
        "R2R_COLLECTION": "my-collection"
      }
    }
  }
}
```

### Other MCP Clients

Any MCP client can use ims-mcp by specifying the command and environment variables:

```json
{
  "command": "uvx",
  "args": ["ims-mcp"],
  "env": {
    "R2R_API_BASE": "http://localhost:7272"
  }
}
```

## Available MCP Tools

### 1. search

Perform semantic and full-text search across documents.

**Parameters:**
- `query` (str): Search query
- `filters` (dict, optional): Metadata filters (e.g., `{"tags": {"$in": ["agents"]}}`)
- `limit` (int, optional): Maximum results
- `use_semantic_search` (bool, optional): Enable vector search
- `use_fulltext_search` (bool, optional): Enable full-text search

**Example:**
```python
search("machine learning", filters={"tags": {"$in": ["research"]}}, limit=5)
```

### 2. rag

Retrieval-augmented generation with LLM.

**Parameters:**
- `query` (str): Question to answer
- `filters` (dict, optional): Metadata filters
- `limit` (int, optional): Max search results to use
- `model` (str, optional): LLM model name
- `temperature` (float, optional): Response randomness (0-1)
- `max_tokens` (int, optional): Max response length

**Example:**
```python
rag("What is machine learning?", model="gpt-4", temperature=0.7)
```

### 3. put_document

Upload or update a document with upsert semantics.

**Parameters:**
- `content` (str): Document text content
- `title` (str): Document title
- `metadata` (dict, optional): Custom metadata (e.g., `{"tags": ["research"], "author": "John"}`)
- `document_id` (str, optional): Explicit document ID

**Example:**
```python
put_document(
    content="Machine learning is...",
    title="ML Guide",
    metadata={"tags": ["research", "ml"]}
)
```

### 4. list_documents

List documents with pagination and optional tag filtering.

**Parameters:**
- `offset` (int, optional): Documents to skip (default: 0)
- `limit` (int, optional): Max documents (default: 100)
- `document_ids` (list[str], optional): Specific IDs to retrieve
- `compact_view` (bool, optional): Show only ID and title (default: True)
- `tags` (list[str], optional): Filter by tags (e.g., `["agents", "r1"]`)
- `match_all_tags` (bool, optional): If True, document must have ALL tags; if False (default), document must have ANY tag

**Examples:**
```python
# List all documents (compact view - ID and title only)
list_documents(offset=0, limit=10)

# List with full details
list_documents(offset=0, limit=10, compact_view=False)

# Filter by tags (ANY mode - documents with "research" OR "ml")
list_documents(tags=["research", "ml"])

# Filter by tags (ALL mode - documents with both "research" AND "ml")
list_documents(tags=["research", "ml"], match_all_tags=True)
```

**Note:** Tag filtering is performed client-side after fetching results. For large collections with complex filtering needs, consider using the `search()` tool with metadata filters instead.

### 5. get_document

Retrieve a specific document by ID or title.

**Parameters:**
- `document_id` (str, optional): Document ID
- `title` (str, optional): Document title

**Example:**
```python
get_document(title="ML Guide")
```

### 6. delete_document

Delete a document by ID.

**Parameters:**
- `document_id` (str, required): The unique identifier of the document to delete

**Example:**
```python
delete_document(document_id="550e8400-e29b-41d4-a716-446655440000")
```

**Returns:**
- Success message with document ID on successful deletion
- Error message if document not found or permission denied

## Metadata Filtering

All filter operators supported:

- `$eq`: Equal
- `$neq`: Not equal
- `$gt`, `$gte`: Greater than (or equal)
- `$lt`, `$lte`: Less than (or equal)
- `$in`: In array
- `$nin`: Not in array
- `$like`, `$ilike`: Pattern matching (case-sensitive/insensitive)

**Examples:**

```python
# Filter by tags
filters={"tags": {"$in": ["research", "ml"]}}

# Filter by domain
filters={"domain": {"$eq": "instructions"}}

# Combined filters
filters={"tags": {"$in": ["research"]}, "created_at": {"$gte": "2024-01-01"}}
```

## Development

### Local Installation

Install directly from PyPI:

```bash
pip install ims-mcp
```

Or for the latest development version, install from source if you have the code locally:

```bash
pip install -e .
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Building for Distribution

```bash
python -m build
```

## Requirements

- Python >= 3.10
- IMS server running and accessible (powered by R2R Light)
- r2r Python SDK >= 3.6.0
- mcp >= 1.0.0

## License

MIT License - see LICENSE file for details

This package is built on R2R (RAG to Riches) technology by SciPhi AI, which is licensed under the MIT License. We gratefully acknowledge the R2R project and its contributors.

## Links

- **R2R Technology**: https://github.com/SciPhi-AI/R2R
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp

## Support

For issues and questions, visit the package page: https://pypi.org/project/ims-mcp/
