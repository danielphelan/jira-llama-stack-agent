"""
High-level Atlassian Tools

This module provides high-level wrapper functions that compose multiple
MCP calls into useful operations for requirements analysis.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from src.integrations.mcp_client import AtlassianMCPClient, MCPToolResult

logger = logging.getLogger(__name__)


@dataclass
class JiraIssue:
    """Represents a Jira issue with relevant fields."""

    key: str
    id: str
    summary: str
    description: Optional[str]
    issue_type: str
    status: str
    priority: Optional[str]
    assignee: Optional[str]
    reporter: Optional[str]
    labels: List[str]
    components: List[str]
    story_points: Optional[float]
    acceptance_criteria: Optional[str]
    raw_data: Dict[str, Any]


@dataclass
class ConfluencePage:
    """Represents a Confluence page."""

    id: str
    title: str
    space_key: str
    space_name: str
    body: str
    url: str
    version: int
    raw_data: Dict[str, Any]


@dataclass
class SearchResult:
    """Represents a search result from Rovo."""

    id: str
    title: str
    excerpt: str
    url: str
    score: float
    type: str  # "jira" or "confluence"
    raw_data: Dict[str, Any]


class AtlassianTools:
    """
    High-level tools for Atlassian operations.

    Wraps multiple MCP calls into cohesive workflows for:
    - Story analysis
    - Similarity search
    - Technical spec creation
    - Auto-linking
    """

    def __init__(self, mcp_client: AtlassianMCPClient):
        """
        Initialize Atlassian tools.

        Args:
            mcp_client: AtlassianMCPClient instance
        """
        self.mcp = mcp_client

    async def get_story_with_context(
        self,
        ticket_id: str,
        include_links: bool = True,
        include_similar: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch a Jira story with full context including linked docs and similar issues.

        Args:
            ticket_id: Jira ticket identifier (e.g., PROJ-123)
            include_links: Whether to fetch linked Confluence pages
            include_similar: Whether to search for similar issues

        Returns:
            Dictionary with issue, confluence_docs, and similar_issues
        """
        context = {
            "issue": None,
            "confluence_docs": [],
            "similar_issues": [],
            "links": []
        }

        # 1. Get main issue
        issue_result = await self.mcp.call_tool(
            "Atlassian:getJiraIssue",
            {
                "issueIdOrKey": ticket_id,
                "fields": [
                    "summary", "description", "status", "priority",
                    "assignee", "reporter", "labels", "components",
                    "issuetype", "customfield_10016"  # Story points field
                ]
            }
        )

        if not issue_result.success:
            logger.error(f"Failed to fetch issue {ticket_id}: {issue_result.error}")
            return context

        issue_data = issue_result.data
        context["issue"] = self._parse_jira_issue(issue_data)

        # 2. Get remote links (Confluence pages)
        if include_links:
            links_result = await self.mcp.call_tool(
                "Atlassian:getJiraIssueRemoteIssueLinks",
                {"issueIdOrKey": ticket_id}
            )

            if links_result.success and links_result.data:
                context["links"] = links_result.data.get("remoteLinks", [])

                # Fetch linked Confluence pages
                for link in context["links"]:
                    if "confluence" in link.get("object", {}).get("url", "").lower():
                        page_id = self._extract_page_id(link["object"]["url"])
                        if page_id:
                            page = await self.get_confluence_page(page_id)
                            if page:
                                context["confluence_docs"].append(page)

        # 3. Search for similar issues using Rovo
        if include_similar:
            similar = await self.search_similar_issues(
                context["issue"].summary,
                context["issue"].description or "",
                limit=5
            )
            context["similar_issues"] = similar

        return context

    async def search_similar_issues(
        self,
        summary: str,
        description: str = "",
        limit: int = 5,
        min_score: float = 0.6
    ) -> List[SearchResult]:
        """
        Search for similar Jira issues using Rovo semantic search.

        Args:
            summary: Issue summary/title
            description: Issue description
            limit: Maximum number of results
            min_score: Minimum relevance score (0-1)

        Returns:
            List of SearchResult objects
        """
        # Construct natural language query for Rovo
        query = f"""
        Find similar Jira issues to:
        {summary}

        Context: {description[:500]}

        Focus on: completed stories, related features, similar implementations
        """

        result = await self.mcp.call_tool(
            "Atlassian:search",
            {
                "query": query.strip()
            }
        )

        if not result.success:
            logger.warning(f"Rovo search failed: {result.error}")
            return []

        # Parse and filter results
        search_results = []
        for item in result.data.get("results", [])[:limit]:
            score = item.get("score", 0.0)
            if score >= min_score:
                search_results.append(SearchResult(
                    id=item.get("id", ""),
                    title=item.get("title", ""),
                    excerpt=item.get("excerpt", ""),
                    url=item.get("url", ""),
                    score=score,
                    type=item.get("type", "jira"),
                    raw_data=item
                ))

        return search_results

    async def search_similar_confluence_docs(
        self,
        query: str,
        space_key: Optional[str] = None,
        limit: int = 5
    ) -> List[ConfluencePage]:
        """
        Search for similar Confluence documentation using Rovo.

        Args:
            query: Natural language search query
            space_key: Optional Confluence space to limit search
            limit: Maximum results

        Returns:
            List of ConfluencePage objects
        """
        search_query = f"""
        Find Confluence technical documentation related to:
        {query}

        Include: architecture decisions, technical specs, implementation guides
        """

        if space_key:
            search_query += f"\nSpace: {space_key}"

        result = await self.mcp.call_tool(
            "Atlassian:search",
            {"query": search_query.strip()}
        )

        if not result.success:
            logger.warning(f"Confluence search failed: {result.error}")
            return []

        # Filter for Confluence results and fetch full pages
        pages = []
        for item in result.data.get("results", [])[:limit]:
            if item.get("type") == "confluence":
                page_id = self._extract_page_id(item.get("url", ""))
                if page_id:
                    page = await self.get_confluence_page(page_id)
                    if page:
                        pages.append(page)

        return pages

    async def get_confluence_page(self, page_id: str) -> Optional[ConfluencePage]:
        """
        Fetch a Confluence page by ID.

        Args:
            page_id: Confluence page ID

        Returns:
            ConfluencePage object or None if not found
        """
        result = await self.mcp.call_tool(
            "Atlassian:getConfluencePage",
            {"pageId": page_id}
        )

        if not result.success:
            logger.warning(f"Failed to fetch Confluence page {page_id}: {result.error}")
            return None

        data = result.data
        return ConfluencePage(
            id=data.get("id", ""),
            title=data.get("title", ""),
            space_key=data.get("space", {}).get("key", ""),
            space_name=data.get("space", {}).get("name", ""),
            body=data.get("body", {}).get("storage", {}).get("value", ""),
            url=data.get("_links", {}).get("webui", ""),
            version=data.get("version", {}).get("number", 1),
            raw_data=data
        )

    async def create_technical_spec(
        self,
        epic_id: str,
        content: str,
        space_key: str = "TECH",
        title: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a technical specification document in Confluence and link to Epic.

        Args:
            epic_id: Jira Epic identifier
            content: Technical spec content (HTML or markdown)
            space_key: Confluence space key
            title: Optional custom title (defaults to Epic summary)

        Returns:
            URL of created Confluence page, or None if failed
        """
        # 1. Get Epic details
        epic_result = await self.mcp.call_tool(
            "Atlassian:getJiraIssue",
            {
                "issueIdOrKey": epic_id,
                "fields": ["summary", "description"]
            }
        )

        if not epic_result.success:
            logger.error(f"Failed to fetch epic {epic_id}: {epic_result.error}")
            return None

        epic_summary = epic_result.data.get("fields", {}).get("summary", "Technical Spec")
        page_title = title or f"Technical Spec: {epic_summary}"

        # 2. Get Confluence space
        spaces_result = await self.mcp.call_tool(
            "Atlassian:getConfluenceSpaces",
            {"keys": [space_key]}
        )

        if not spaces_result.success or not spaces_result.data.get("results"):
            logger.error(f"Confluence space {space_key} not found")
            return None

        space_id = spaces_result.data["results"][0]["id"]

        # 3. Create Confluence page
        page_result = await self.mcp.call_tool(
            "Atlassian:createConfluencePage",
            {
                "spaceId": space_id,
                "title": page_title,
                "body": content
            }
        )

        if not page_result.success:
            logger.error(f"Failed to create Confluence page: {page_result.error}")
            return None

        page_url = page_result.data.get("_links", {}).get("webui", "")

        # 4. Add comment to Epic with link
        await self.mcp.call_tool(
            "Atlassian:addCommentToJiraIssue",
            {
                "issueIdOrKey": epic_id,
                "body": f"📝 Technical specification created: {page_url}"
            }
        )

        logger.info(f"Created technical spec for {epic_id}: {page_url}")
        return page_url

    async def auto_link_related_tickets(
        self,
        ticket_id: str,
        max_links: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Automatically find and link related Jira tickets.

        Args:
            ticket_id: Current ticket to find links for
            max_links: Maximum number of links to create

        Returns:
            List of created link objects
        """
        # Get current ticket context
        context = await self.get_story_with_context(
            ticket_id,
            include_links=False,
            include_similar=True
        )

        if not context["issue"]:
            return []

        created_links = []
        for similar in context["similar_issues"][:max_links]:
            # Determine relationship type based on score
            link_type = "relates to"
            if similar.score > 0.85:
                link_type = "is similar to"

            # Create the link (in a real implementation)
            # Note: MCP doesn't have direct link creation, would use editJiraIssue
            logger.info(f"Would link {ticket_id} to {similar.id} ({link_type})")
            created_links.append({
                "target": similar.id,
                "type": link_type,
                "score": similar.score
            })

        return created_links

    def _parse_jira_issue(self, data: Dict[str, Any]) -> JiraIssue:
        """Parse Jira API response into JiraIssue object."""
        fields = data.get("fields", {})

        return JiraIssue(
            key=data.get("key", ""),
            id=data.get("id", ""),
            summary=fields.get("summary", ""),
            description=fields.get("description", ""),
            issue_type=fields.get("issuetype", {}).get("name", ""),
            status=fields.get("status", {}).get("name", ""),
            priority=fields.get("priority", {}).get("name"),
            assignee=fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            reporter=fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
            labels=fields.get("labels", []),
            components=[c.get("name", "") for c in fields.get("components", [])],
            story_points=fields.get("customfield_10016"),  # Common story points field
            acceptance_criteria=fields.get("customfield_10100"),  # Common AC field
            raw_data=data
        )

    def _extract_page_id(self, url: str) -> Optional[str]:
        """Extract Confluence page ID from URL."""
        import re
        # Match patterns like /pages/123456 or pageId=123456
        patterns = [
            r'/pages/(\d+)',
            r'pageId=(\d+)',
            r'/(\d+)$'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None
