"""
Integration modules for external services.

This package contains integrations for:
- Atlassian MCP Server (Jira, Confluence, Rovo)
- Vector stores (ChromaDB)
- LLM providers
"""

from src.integrations.mcp_client import AtlassianMCPClient
from src.integrations.atlassian_tools import AtlassianTools

__all__ = ["AtlassianMCPClient", "AtlassianTools"]
