"""R2R MCP Server - FastMCP server for R2R retrieval system.

This module provides a Model Context Protocol (MCP) server that connects to R2R
for advanced retrieval-augmented generation capabilities.

Environment Variables:
    R2R_API_BASE or R2R_BASE_URL: R2R server URL (default: http://localhost:7272)
    R2R_COLLECTION: Collection name for queries (optional, uses server default)
    R2R_API_KEY: API key for authentication (optional)
    R2R_EMAIL: Email for authentication (optional, requires R2R_PASSWORD)
    R2R_PASSWORD: Password for authentication (optional, requires R2R_EMAIL)

The R2RClient automatically reads these environment variables, so no manual
configuration is needed when running via uvx or other launchers.
"""

import functools
import logging
import os
import signal
import sys
import uuid
from r2r import R2RClient, R2RException

# Debug mode controlled by environment variable
DEBUG_MODE = os.getenv('IMS_DEBUG', '').lower() in ('1', 'true', 'yes', 'on')

# Configure logging based on debug mode
if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG)
else:
    # Suppress all logging output from R2R and other libraries
    logging.basicConfig(level=logging.CRITICAL)
    # Specifically suppress httpx and httpcore which R2R uses
    logging.getLogger('httpx').setLevel(logging.CRITICAL)
    logging.getLogger('httpcore').setLevel(logging.CRITICAL)
    logging.getLogger('r2r').setLevel(logging.CRITICAL)

# Global client instance with authentication
_authenticated_client = None


def debug_print(msg: str):
    """Print debug message to stderr if debug mode enabled."""
    if DEBUG_MODE:
        print(msg, file=sys.stderr)
        sys.stderr.flush()


def cleanup_and_exit(signum=None, frame=None):
    """Gracefully shutdown the server on termination signals."""
    global _authenticated_client
    
    debug_print(f"[ims-mcp] Shutting down gracefully...")
    
    # Cleanup authenticated client if exists
    if _authenticated_client is not None:
        try:
            # R2R client cleanup if needed
            _authenticated_client = None
        except Exception:
            pass  # Ignore errors during shutdown
    
    debug_print(f"[ims-mcp] Shutdown complete")
    sys.exit(0)


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, cleanup_and_exit)
signal.signal(signal.SIGINT, cleanup_and_exit)

def get_authenticated_client() -> R2RClient:
    """Get or create an authenticated R2R client.
    
    This function handles authentication using either:
    1. API key (R2R_API_KEY) - preferred method
    2. Email/password (R2R_EMAIL + R2R_PASSWORD) - fallback method
    
    Returns:
        Authenticated R2RClient instance
    """
    global _authenticated_client
    
    # If client already exists and is authenticated, reuse it
    if _authenticated_client is not None:
        return _authenticated_client
    
    # Log configuration on first client creation
    from ims_mcp import __version__
    base_url = os.getenv('R2R_API_BASE') or os.getenv('R2R_BASE_URL') or 'http://localhost:7272'
    collection = os.getenv('R2R_COLLECTION', 'default')
    api_key = os.getenv('R2R_API_KEY', '')
    email = os.getenv("R2R_EMAIL")
    password = os.getenv("R2R_PASSWORD")
    
    debug_print(f"[ims-mcp v{__version__}]")
    debug_print(f"  server={base_url}")
    debug_print(f"  collection={collection}")
    debug_print(f"  api_key={api_key[:3] + '...' if api_key else 'none'}")
    debug_print(f"  email={email if email else 'none'}")
    debug_print(f"  password={password[:3] + '...' if password else 'none'}")
    
    # Create new client
    client = R2RClient()
    
    # Check for email/password authentication
    email = os.getenv("R2R_EMAIL")
    password = os.getenv("R2R_PASSWORD")
    
    if email and password:
        try:
            # Login - R2RClient automatically handles token internally
            client.users.login(email=email, password=password)
            debug_print(f"[ims-mcp] Login successful")
        except Exception as e:
            debug_print(f"[ims-mcp] Login failed: {e}")
            # If login fails, continue without authentication (might work for local servers)
            pass
    
    # Cache the client for reuse
    _authenticated_client = client
    return client


def retry_on_auth_error(func):
    """Decorator to handle token expiry and automatically re-authenticate.
    
    When R2R server restarts, all authentication tokens are invalidated.
    This decorator catches 401/403 errors, invalidates the cached client,
    re-authenticates, and retries the request once.
    """
    def invalidate_client():
        """Invalidate cached client to force re-authentication."""
        global _authenticated_client
        _authenticated_client = None
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except R2RException as e:
            # Check if this is an authentication error (token expired)
            if hasattr(e, 'status_code') and e.status_code in [401, 403]:
                debug_print(f"[ims-mcp] Token expired, re-authenticating...")
                invalidate_client()
                # Retry once with fresh authentication
                return await func(*args, **kwargs)
            # Re-raise non-auth errors
            raise
    return wrapper


def id_to_shorthand(id: str) -> str:
    """Convert a full ID to shortened version for display."""
    return str(id)[:7]


def format_search_results_for_llm(results) -> str:
    """
    Format R2R search results for LLM consumption.
    
    Formats vector search, graph search, web search, and document search results
    into a readable text format with source IDs and relevant metadata.
    """
    lines = []

    # 1) Chunk search
    if results.chunk_search_results:
        lines.append("Vector Search Results:")
        for c in results.chunk_search_results:
            lines.append(f"Source ID [{id_to_shorthand(c.id)}]:")
            lines.append(c.text or "")  # or c.text[:200] to truncate

    # 2) Graph search
    if results.graph_search_results:
        lines.append("Graph Search Results:")
        for g in results.graph_search_results:
            lines.append(f"Source ID [{id_to_shorthand(g.id)}]:")
            if hasattr(g.content, "summary"):
                lines.append(f"Community Name: {g.content.name}")
                lines.append(f"ID: {g.content.id}")
                lines.append(f"Summary: {g.content.summary}")
            elif hasattr(g.content, "name") and hasattr(
                g.content, "description"
            ):
                lines.append(f"Entity Name: {g.content.name}")
                lines.append(f"Description: {g.content.description}")
            elif (
                hasattr(g.content, "subject")
                and hasattr(g.content, "predicate")
                and hasattr(g.content, "object")
            ):
                lines.append(
                    f"Relationship: {g.content.subject}-{g.content.predicate}-{g.content.object}"
                )

    # 3) Web search
    if results.web_search_results:
        lines.append("Web Search Results:")
        for w in results.web_search_results:
            lines.append(f"Source ID [{id_to_shorthand(w.id)}]:")
            lines.append(f"Title: {w.title}")
            lines.append(f"Link: {w.link}")
            lines.append(f"Snippet: {w.snippet}")

    # 4) Local context docs
    if results.document_search_results:
        lines.append("Local Context Documents:")
        for doc_result in results.document_search_results:
            doc_title = doc_result.title or "Untitled Document"
            doc_id = doc_result.id
            summary = doc_result.summary

            lines.append(f"Full Document ID: {doc_id}")
            lines.append(f"Shortened Document ID: {id_to_shorthand(doc_id)}")
            lines.append(f"Document Title: {doc_title}")
            if summary:
                lines.append(f"Summary: {summary}")

            if doc_result.chunks:
                # Then each chunk inside:
                for chunk in doc_result.chunks:
                    lines.append(
                        f"\nChunk ID {id_to_shorthand(chunk['id'])}:\n{chunk['text']}"
                    )

    result = "\n".join(lines)
    return result


# Create a FastMCP server
try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("R2R Retrieval System")
except Exception as e:
    raise ImportError(
        "MCP is not installed. Please run `pip install mcp`"
    ) from e


# Search tool with filtering support
@mcp.tool()
@retry_on_auth_error
async def search(
    query: str,
    filters: dict | None = None,
    limit: float | None = None,  # Use float to accept JSON "number" type, convert to int internally
    use_semantic_search: bool | None = None,
    use_fulltext_search: bool | None = None,
) -> str:
    """
    Performs a search with optional filtering and configuration

    Args:
        query: The search query
        filters: Metadata filters (e.g., {"tags": {"$in": ["agents"]}})
        limit: Maximum number of results (server default if not specified)
        use_semantic_search: Enable semantic search (server default if not specified)
        use_fulltext_search: Enable fulltext search (server default if not specified)

    Returns:
        Formatted search results from the knowledge base
    """
    client = get_authenticated_client()

    # Only build search_settings if user provided any parameters
    # This preserves original behavior: search("query") → search(query=query) with NO search_settings
    kwargs = {"query": query}

    if any(
        param is not None
        for param in [filters, limit, use_semantic_search, use_fulltext_search]
    ):
        search_settings = {}

        if filters is not None:
            search_settings["filters"] = filters
        if limit is not None:
            search_settings["limit"] = int(limit)  # Convert to int for R2R API
        if use_semantic_search is not None:
            search_settings["use_semantic_search"] = use_semantic_search
        if use_fulltext_search is not None:
            search_settings["use_fulltext_search"] = use_fulltext_search

        kwargs["search_settings"] = search_settings

    search_response = client.retrieval.search(**kwargs)
    return format_search_results_for_llm(search_response.results)


# RAG query tool with filtering and generation config
@mcp.tool()
@retry_on_auth_error
async def rag(
    query: str,
    filters: dict | None = None,
    limit: float | None = None,  # Use float to accept JSON "number" type, convert to int internally
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: float | None = None,  # Use float to accept JSON "number" type, convert to int internally
) -> str:
    """
    Perform RAG query with optional filtering and generation config

    Args:
        query: The question to answer
        filters: Metadata filters (e.g., {"tags": {"$in": ["agents"]}})
        limit: Max search results to use (server default if not specified)
        model: LLM model to use (server default if not specified)
        temperature: Response randomness 0-1 (server default if not specified)
        max_tokens: Max response length (server default if not specified)

    Returns:
        Generated answer from RAG
    """
    client = get_authenticated_client()

    # Only build configs if user provided parameters
    # This preserves original behavior: rag("query") → rag(query=query) with NO configs
    kwargs = {"query": query}

    # Build search_settings if any search params provided
    if any(param is not None for param in [filters, limit]):
        search_settings = {}
        if filters is not None:
            search_settings["filters"] = filters
        if limit is not None:
            search_settings["limit"] = int(limit)  # Convert to int for R2R API
        kwargs["search_settings"] = search_settings

    # Build rag_generation_config if any generation params provided
    if any(param is not None for param in [model, temperature, max_tokens]):
        rag_config = {}
        if model is not None:
            rag_config["model"] = model
        if temperature is not None:
            rag_config["temperature"] = temperature
        if max_tokens is not None:
            rag_config["max_tokens"] = int(max_tokens)  # Convert to int for R2R API
        kwargs["rag_generation_config"] = rag_config

    rag_response = client.retrieval.rag(**kwargs)
    return rag_response.results.generated_answer  # type: ignore


# Document upload tool with upsert semantics
@mcp.tool()
@retry_on_auth_error
async def put_document(
    content: str,
    title: str,
    metadata: dict | None = None,
    document_id: str | None = None,
) -> str:
    """
    Upload or update a document with upsert semantics

    Args:
        content: The text content of the document
        title: Document title (used for ID generation if document_id not provided)
        metadata: Additional metadata (e.g., {"tags": ["agents"], "domain": "dev"})
        document_id: Optional document ID for explicit upsert

    Returns:
        Status message with document_id and operation type
    """
    client = get_authenticated_client()

    # Build metadata with title
    final_metadata = {"title": title}
    if metadata:
        final_metadata.update(metadata)

    # Generate UUID from title if not provided (enables upsert by title)
    if not document_id:
        # Use UUID5 to create deterministic UUID from title
        # Same title always generates same UUID for upsert semantics
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
        document_id = str(uuid.uuid5(namespace, title))

    # Try to create, if exists then update
    try:
        result = client.documents.create(
            raw_text=content,
            id=document_id,
            metadata=final_metadata,
            run_with_orchestration=True,
        )
        return f"Document created successfully.\nDocument ID: {document_id}\nOperation: CREATE"
    except Exception as e:
        error_msg = str(e)
        # Check if document already exists
        if "already exists" in error_msg.lower():
            # Document exists, delete and recreate for true upsert
            try:
                # Delete existing document
                client.documents.delete(id=document_id)
                
                # Recreate with new content
                result = client.documents.create(
                    raw_text=content,
                    id=document_id,
                    metadata=final_metadata,
                    run_with_orchestration=True,
                )
                return f"Document updated successfully.\nDocument ID: {document_id}\nOperation: UPDATE (delete + recreate)"
            except Exception as update_error:
                return f"Error updating document: {str(update_error)}"
        else:
            # Different error, re-raise
            return f"Error creating document: {error_msg}"


# List documents tool
@mcp.tool()
@retry_on_auth_error
async def list_documents(
    offset: float = 0,  # Use float to accept JSON "number" type, convert to int internally
    limit: float = 100,  # Use float to accept JSON "number" type, convert to int internally
    document_ids: list[str] | None = None,
    compact_view: bool = True,
    tags: list[str] | None = None,
    match_all_tags: bool = False,
) -> str:
    """
    List documents in the R2R knowledge base with pagination

    Args:
        offset: Number of documents to skip (default: 0)
        limit: Maximum number of documents to return (default: 100, max: 100)
        document_ids: Optional list of specific document IDs to retrieve
        compact_view: Show only ID and title (default: True - compact view)
        tags: Optional list of tags to filter by (e.g., ["agents", "r1"])
        match_all_tags: If True, document must have ALL tags; if False (default), document must have ANY tag

    Returns:
        Formatted list of documents
    """
    client = get_authenticated_client()

    # Build kwargs for list call
    kwargs = {"offset": int(offset), "limit": min(int(limit), 100)}  # Convert to int, cap at 100
    
    if document_ids:
        kwargs["ids"] = document_ids

    # List documents
    result = client.documents.list(**kwargs)
    
    # Filter by tags if provided
    filtered_results = result.results
    if tags and len(tags) > 0:
        provided_tags = set(tags)
        filtered_results = []
        
        for doc in result.results:
            # Extract tags from document metadata
            doc_tags = set()
            if hasattr(doc, 'metadata') and doc.metadata:
                tags_value = doc.metadata.get('tags')
                if tags_value:
                    if isinstance(tags_value, list):
                        doc_tags = set(tags_value)
                    elif isinstance(tags_value, str):
                        doc_tags = {tags_value}
            
            # Apply filter based on match mode
            if match_all_tags:
                # ALL mode: document must have all provided tags
                if provided_tags.issubset(doc_tags):
                    filtered_results.append(doc)
            else:
                # ANY mode: document must have at least one provided tag
                if len(provided_tags.intersection(doc_tags)) > 0:
                    filtered_results.append(doc)
    
    # Format results for display
    lines = []
    if tags:
        tag_mode = "ALL" if match_all_tags else "ANY"
        lines.append(f"Documents with {tag_mode} tags {tags} (showing {len(filtered_results)} of {result.total_entries} total):\n")
    else:
        lines.append(f"Documents (showing {len(filtered_results)} of {result.total_entries} total):\n")
    
    for doc in filtered_results:
        if compact_view:
            # Compact mode: just ID and title
            lines.append(f"ID: {doc.id} | Title: {doc.title or 'Untitled'}")
        else:
            # Full mode: all details
            lines.append(f"{'='*60}")
            lines.append(f"ID: {doc.id}")
            lines.append(f"Title: {doc.title or 'Untitled'}")
            
            # Show all metadata
            if hasattr(doc, 'metadata') and doc.metadata:
                lines.append("Metadata:")
                for key, value in doc.metadata.items():
                    # Format value based on type
                    if isinstance(value, list):
                        lines.append(f"  {key}: {', '.join(str(v) for v in value)}")
                    elif isinstance(value, dict):
                        lines.append(f"  {key}: {value}")
                    else:
                        lines.append(f"  {key}: {value}")
            
            lines.append(f"Status: {doc.ingestion_status}")
            lines.append(f"Size: {doc.size_in_bytes} bytes")
            lines.append(f"Created: {doc.created_at}")
            lines.append(f"Updated: {doc.updated_at}")
            
            if hasattr(doc, 'summary') and doc.summary:
                lines.append(f"Summary: {doc.summary[:200]}...")
    
    return "\n".join(lines)


# Get document tool
@mcp.tool()
@retry_on_auth_error
async def get_document(
    document_id: str | None = None,
    title: str | None = None,
) -> str:
    """
    Retrieve a document by ID or title
    
    Args:
        document_id: Document ID to retrieve
        title: Document title to search for (if document_id not provided)
    
    Returns:
        Formatted document details
    """
    client = get_authenticated_client()
    
    # Validate that at least one parameter is provided
    if not document_id and not title:
        return "Error: Must provide either document_id or title"
    
    # If only title provided, search for document by title using metadata filter
    if not document_id and title:
        try:
            # Use search API with title filter for more efficient lookup
            search_result = client.retrieval.search(
                query=title,
                search_settings={
                    "filters": {"title": {"$eq": title}},
                    "limit": 5,
                    "use_fulltext_search": True,  # Use fulltext for exact match
                }
            )
            
            # Extract document IDs from search results
            matching_docs = []
            if hasattr(search_result, 'results') and hasattr(search_result.results, 'chunk_search_results'):
                seen_doc_ids = set()
                for chunk in search_result.results.chunk_search_results:
                    if hasattr(chunk, 'metadata') and chunk.metadata:
                        doc_id = chunk.metadata.get('document_id')
                        doc_title = chunk.metadata.get('title')
                        if doc_id and doc_id not in seen_doc_ids:
                            seen_doc_ids.add(doc_id)
                            matching_docs.append((doc_id, doc_title))
            
            # Fallback: Use list API if search didn't work
            if not matching_docs:
                list_result = client.documents.list(limit=100)
                for doc in list_result.results:
                    if doc.title and doc.title.lower() == title.lower():
                        matching_docs.append((doc.id, doc.title))
            
            if not matching_docs:
                return f"Error: No document found with title '{title}'"
            
            if len(matching_docs) > 1:
                lines = [f"Warning: Found {len(matching_docs)} documents with title '{title}':"]
                for doc_id, doc_title in matching_docs:
                    lines.append(f"  - ID: {doc_id}")
                lines.append("\nPlease use document_id to retrieve a specific document.")
                return "\n".join(lines)
            
            # Found exactly one match
            document_id = matching_docs[0][0]
        except R2RException as e:
            # Re-raise authentication errors so the decorator can handle them
            if hasattr(e, 'status_code') and e.status_code in [401, 403]:
                raise
            # For other R2RExceptions, return error message
            return f"Error searching for document by title: {str(e)}"
        except Exception as e:
            return f"Error searching for document by title: {str(e)}"
    
    # Now we have document_id, download the original file
    try:
        # Download the original document content
        file_content = client.documents.download(id=document_id)
        
        # Read and decode the content
        content_bytes = file_content.read()
        content_text = content_bytes.decode('utf-8')
        
        # Build output with just document ID and content
        output_lines = [f"DOCUMENT ID: {document_id}", content_text]
        
        return "\n".join(output_lines)
        
    except R2RException as e:
        # Re-raise authentication errors so the decorator can handle them
        if hasattr(e, 'status_code') and e.status_code in [401, 403]:
            raise
        # For other R2RExceptions, return error message
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return f"Error: Document with ID '{document_id}' not found"
        return f"Error downloading document: {error_msg}"
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return f"Error: Document with ID '{document_id}' not found"
        return f"Error downloading document: {error_msg}"


# Delete document tool
@mcp.tool()
@retry_on_auth_error
async def delete_document(document_id: str) -> str:
    """
    Delete a document by ID
    
    Args:
        document_id: The unique identifier of the document to delete
    
    Returns:
        Status message confirming deletion or describing error
    """
    client = get_authenticated_client()
    
    try:
        # Delete the document
        client.documents.delete(id=document_id)
        return f"Document deleted successfully.\nDocument ID: {document_id}"
    except Exception as e:
        error_msg = str(e)
        
        # Handle common error cases with user-friendly messages
        if "not found" in error_msg.lower():
            return f"Error: Document with ID '{document_id}' not found"
        elif "permission" in error_msg.lower() or "denied" in error_msg.lower():
            return f"Error: Permission denied to delete document '{document_id}'"
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            return f"Error: Unable to communicate with R2R server. Please check connection."
        else:
            # Generic error fallback
            return f"Error deleting document: {error_msg}"


def main():
    """Main entry point for console script."""
    mcp.run()


# Run the server if executed directly
if __name__ == "__main__":
    main()

