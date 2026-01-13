"""IMS MCP Server - Model Context Protocol server for IMS (Instruction Management Systems).

This package provides a FastMCP server that connects to IMS
for advanced retrieval-augmented generation capabilities.

Environment Variables:
    R2R_API_BASE: IMS server URL (default: http://localhost:7272)
    R2R_COLLECTION: Collection name for queries (optional)
    R2R_API_KEY: API key for authentication (optional)
    
Note: Environment variables use R2R_ prefix for compatibility with underlying R2R SDK.
"""

__version__ = "1.0.10"
__author__ = "Igor Solomatov"

from ims_mcp.server import mcp

__all__ = ["mcp", "__version__"]

