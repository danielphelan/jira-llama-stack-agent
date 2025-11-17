"""
Atlassian MCP (Model Context Protocol) Client

This module provides a client for interacting with Atlassian services
(Jira, Confluence, Rovo) through the Anthropic MCP server.

The MCP server provides a standardized way for LLMs to interact with
external systems through a unified tool interface.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import httpx
from llama_stack_client import LlamaStackClient
from llama_stack_client.types import ToolDefinition

logger = logging.getLogger(__name__)


@dataclass
class MCPToolResult:
    """Result from an MCP tool execution."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    tool_name: Optional[str] = None
    execution_time_ms: Optional[float] = None


class AtlassianMCPClient:
    """
    Client for Atlassian MCP Server integration.

    Provides high-level methods for interacting with Jira, Confluence,
    and Rovo through the Model Context Protocol.

    Attributes:
        llama_client: Llama Stack client instance
        cloud_id: Atlassian cloud instance ID
        available_tools: List of available MCP tools
    """

    def __init__(
        self,
        llama_stack_url: str = "http://localhost:5000",
        cloud_id: Optional[str] = None,
        auto_discover_cloud_id: bool = True
    ):
        """
        Initialize the Atlassian MCP client.

        Args:
            llama_stack_url: Base URL of Llama Stack server
            cloud_id: Atlassian cloud instance ID (auto-discovered if None)
            auto_discover_cloud_id: Whether to auto-discover cloud ID
        """
        self.llama_client = LlamaStackClient(base_url=llama_stack_url)
        self.cloud_id = cloud_id
        self.available_tools: List[str] = []

        # Initialize connection
        self._initialize(auto_discover_cloud_id)

    def _initialize(self, auto_discover: bool = True) -> None:
        """
        Initialize the MCP connection and discover available tools.

        Args:
            auto_discover: Whether to auto-discover cloud ID
        """
        try:
            # Discover cloud ID if not provided
            if auto_discover and not self.cloud_id:
                self.cloud_id = self._discover_cloud_id()
                logger.info(f"Discovered Atlassian Cloud ID: {self.cloud_id}")

            # Discover available tools
            self._discover_tools()
            logger.info(f"Initialized MCP client with {len(self.available_tools)} tools")

        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise

    def _discover_cloud_id(self) -> str:
        """
        Auto-discover Atlassian cloud ID from accessible resources.

        Returns:
            Cloud ID string

        Raises:
            ValueError: If cloud ID cannot be discovered
        """
        try:
            result = self.call_tool_sync("Atlassian:getAccessibleAtlassianResources", {})

            if result.success and result.data:
                resources = result.data.get("resources", [])
                if resources:
                    cloud_id = resources[0].get("id")
                    return cloud_id

            raise ValueError("No accessible Atlassian resources found")

        except Exception as e:
            logger.error(f"Failed to discover cloud ID: {e}")
            raise ValueError(f"Could not auto-discover cloud ID: {e}")

    def _discover_tools(self) -> None:
        """Discover available MCP tools from the Llama Stack server."""
        try:
            # In a real implementation, this would query the MCP server
            # for available tools. For now, we'll define the known tools.
            self.available_tools = [
                # Jira tools
                "Atlassian:createJiraIssue",
                "Atlassian:getJiraIssue",
                "Atlassian:editJiraIssue",
                "Atlassian:addCommentToJiraIssue",
                "Atlassian:transitionJiraIssue",
                "Atlassian:searchJiraIssuesUsingJql",
                "Atlassian:getJiraIssueRemoteIssueLinks",
                "Atlassian:getVisibleJiraProjects",
                "Atlassian:getJiraProjectIssueTypesMetadata",
                "Atlassian:lookupJiraAccountId",

                # Confluence tools
                "Atlassian:createConfluencePage",
                "Atlassian:updateConfluencePage",
                "Atlassian:getConfluencePage",
                "Atlassian:getPagesInConfluenceSpace",
                "Atlassian:getConfluenceSpaces",
                "Atlassian:getConfluencePageDescendants",
                "Atlassian:createConfluenceFooterComment",
                "Atlassian:createConfluenceInlineComment",
                "Atlassian:getConfluencePageFooterComments",
                "Atlassian:searchConfluenceUsingCql",

                # Rovo search
                "Atlassian:search",

                # Authentication
                "Atlassian:atlassianUserInfo",
                "Atlassian:getAccessibleAtlassianResources",
                "Atlassian:fetch",
            ]

        except Exception as e:
            logger.warning(f"Failed to discover tools: {e}")
            self.available_tools = []

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        retries: int = 3
    ) -> MCPToolResult:
        """
        Call an MCP tool asynchronously.

        Args:
            tool_name: Name of the MCP tool (e.g., "Atlassian:getJiraIssue")
            parameters: Tool parameters as dictionary
            retries: Number of retry attempts for transient failures

        Returns:
            MCPToolResult with success status and data/error
        """
        import time
        start_time = time.time()

        # Add cloud_id to parameters if not present and required
        if "cloudId" not in parameters and self.cloud_id:
            parameters["cloudId"] = self.cloud_id

        for attempt in range(retries):
            try:
                # Call the tool through Llama Stack
                result = await self.llama_client.tools.call(
                    tool_name=tool_name,
                    parameters=parameters
                )

                execution_time = (time.time() - start_time) * 1000

                return MCPToolResult(
                    success=True,
                    data=result,
                    tool_name=tool_name,
                    execution_time_ms=execution_time
                )

            except Exception as e:
                error_msg = str(e).lower()

                # Handle specific error types
                if "rate limit" in error_msg:
                    if attempt < retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue

                elif "not found" in error_msg:
                    logger.warning(f"Resource not found: {parameters}")
                    return MCPToolResult(
                        success=False,
                        error="Resource not found",
                        tool_name=tool_name
                    )

                elif "permission" in error_msg or "unauthorized" in error_msg:
                    logger.error(f"Permission denied for tool: {tool_name}")
                    return MCPToolResult(
                        success=False,
                        error="Permission denied",
                        tool_name=tool_name
                    )

                # Log and retry for unknown errors
                logger.error(f"Tool execution failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    execution_time = (time.time() - start_time) * 1000
                    return MCPToolResult(
                        success=False,
                        error=str(e),
                        tool_name=tool_name,
                        execution_time_ms=execution_time
                    )

        return MCPToolResult(
            success=False,
            error="Max retries exceeded",
            tool_name=tool_name
        )

    def call_tool_sync(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        retries: int = 3
    ) -> MCPToolResult:
        """
        Call an MCP tool synchronously.

        Args:
            tool_name: Name of the MCP tool
            parameters: Tool parameters
            retries: Number of retry attempts

        Returns:
            MCPToolResult with success status and data/error
        """
        # Run async function in sync context
        return asyncio.run(self.call_tool(tool_name, parameters, retries))

    def is_tool_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool is available, False otherwise
        """
        return tool_name in self.available_tools

    def get_available_tools(self, category: Optional[str] = None) -> List[str]:
        """
        Get list of available tools, optionally filtered by category.

        Args:
            category: Tool category (jira, confluence, rovo, auth)

        Returns:
            List of tool names
        """
        if not category:
            return self.available_tools

        category_map = {
            "jira": ["Jira"],
            "confluence": ["Confluence"],
            "rovo": ["search"],
            "auth": ["atlassianUserInfo", "getAccessible", "fetch"]
        }

        keywords = category_map.get(category.lower(), [])
        return [
            tool for tool in self.available_tools
            if any(keyword in tool for keyword in keywords)
        ]

    async def test_connection(self) -> bool:
        """
        Test the MCP connection by fetching user info.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = await self.call_tool("Atlassian:atlassianUserInfo", {})

            if result.success:
                logger.info(f"MCP connection test successful: {result.data}")
                return True
            else:
                logger.error(f"MCP connection test failed: {result.error}")
                return False

        except Exception as e:
            logger.error(f"MCP connection test error: {e}")
            return False


# Singleton instance for global access
_mcp_client_instance: Optional[AtlassianMCPClient] = None


def get_mcp_client(
    llama_stack_url: Optional[str] = None,
    cloud_id: Optional[str] = None
) -> AtlassianMCPClient:
    """
    Get or create the global MCP client instance.

    Args:
        llama_stack_url: Llama Stack server URL (uses env var if None)
        cloud_id: Atlassian cloud ID (auto-discovered if None)

    Returns:
        AtlassianMCPClient instance
    """
    global _mcp_client_instance

    if _mcp_client_instance is None:
        url = llama_stack_url or os.getenv("LLAMA_STACK_BASE_URL", "http://localhost:5000")
        _mcp_client_instance = AtlassianMCPClient(
            llama_stack_url=url,
            cloud_id=cloud_id
        )

    return _mcp_client_instance
