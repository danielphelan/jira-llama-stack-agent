"""
Requirements Analysis Agent Core

This module implements the main agent orchestration logic that coordinates
all analysis workflows.
"""

import logging
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from llama_stack_client import LlamaStackClient

from src.integrations.mcp_client import AtlassianMCPClient, get_mcp_client
from src.integrations.atlassian_tools import AtlassianTools
from src.agent.tools import AgentTools
from src.prompts.system_prompts import SYSTEM_PROMPT, AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)


class RequirementsAgent:
    """
    Main Requirements Analysis Agent.

    Orchestrates all analysis workflows including:
    - Story analysis and completeness checking
    - Story point estimation
    - Test case generation
    - Technical specification creation
    - Auto-linking and similarity search
    """

    def __init__(
        self,
        config_path: str = "config/agent_config.yaml",
        llama_stack_url: Optional[str] = None,
        cloud_id: Optional[str] = None
    ):
        """
        Initialize the Requirements Agent.

        Args:
            config_path: Path to agent configuration file
            llama_stack_url: Llama Stack server URL (from config if None)
            cloud_id: Atlassian cloud ID (auto-discovered if None)
        """
        self.config = self._load_config(config_path)

        # Initialize Llama Stack client
        llama_url = llama_stack_url or self.config.get("llama_stack", {}).get("inference", {}).get("base_url", "http://localhost:5000")
        self.llama_client = LlamaStackClient(base_url=llama_url)

        # Initialize MCP client
        self.mcp_client = get_mcp_client(llama_stack_url=llama_url, cloud_id=cloud_id)

        # Initialize Atlassian tools
        self.atlassian = AtlassianTools(self.mcp_client)

        # Initialize agent tools
        model_name = self.config.get("llama_stack", {}).get("model", {}).get("name", "meta-llama/Llama-3.3-70B-Instruct")
        self.tools = AgentTools(
            llama_client=self.llama_client,
            atlassian_tools=self.atlassian,
            model_name=model_name
        )

        logger.info("Requirements Agent initialized successfully")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load agent configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return {}

    async def analyze_story(
        self,
        ticket_id: str,
        post_comment: bool = True,
        estimate_points: bool = True,
        generate_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Perform complete story analysis workflow.

        This is the main entry point for analyzing a Jira story.

        Args:
            ticket_id: Jira ticket identifier (e.g., PROJ-123)
            post_comment: Whether to post analysis as Jira comment
            estimate_points: Whether to estimate story points
            generate_tests: Whether to generate test cases

        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting complete analysis for {ticket_id}")

        results = {
            "ticket_id": ticket_id,
            "success": False,
            "analysis": None,
            "estimation": None,
            "tests": None,
            "comment_posted": False
        }

        try:
            # 1. Analyze user story
            analysis = await self.tools.analyze_user_story(ticket_id)
            if not analysis:
                logger.error(f"Story analysis failed for {ticket_id}")
                return results

            results["analysis"] = analysis
            logger.info(f"Story analysis complete: completeness={analysis.completeness_score}")

            # 2. Estimate story points if requested
            if estimate_points and self._should_estimate(analysis):
                estimation = await self.tools.estimate_story_points(ticket_id)
                if estimation:
                    results["estimation"] = estimation
                    logger.info(f"Estimation complete: {estimation.estimated_points} points")

            # 3. Generate test cases if requested
            if generate_tests and self._should_generate_tests(analysis):
                tests = await self.tools.generate_test_cases(ticket_id)
                if tests:
                    results["tests"] = tests
                    logger.info(f"Test generation complete: {tests.total_test_cases} tests")

            # 4. Post comment to Jira if requested
            if post_comment:
                comment = await self.tools.format_analysis_comment(
                    ticket_id,
                    analysis,
                    results.get("estimation"),
                    results.get("tests")
                )

                comment_result = await self.mcp_client.call_tool(
                    "Atlassian:addCommentToJiraIssue",
                    {
                        "issueIdOrKey": ticket_id,
                        "body": comment
                    }
                )

                if comment_result.success:
                    results["comment_posted"] = True
                    logger.info(f"Posted analysis comment to {ticket_id}")
                else:
                    logger.error(f"Failed to post comment: {comment_result.error}")

            results["success"] = True
            return results

        except Exception as e:
            logger.error(f"Analysis workflow failed for {ticket_id}: {e}")
            return results

    async def generate_epic_spec(
        self,
        epic_id: str,
        confluence_space: Optional[str] = None,
        post_to_confluence: bool = True
    ) -> Dict[str, Any]:
        """
        Generate technical specification for an Epic.

        Args:
            epic_id: Jira Epic identifier
            confluence_space: Confluence space key (from config if None)
            post_to_confluence: Whether to create Confluence page

        Returns:
            Dictionary with spec generation results
        """
        logger.info(f"Generating technical spec for Epic {epic_id}")

        results = {
            "epic_id": epic_id,
            "success": False,
            "spec_content": None,
            "confluence_url": None
        }

        try:
            # 1. Get Epic and child stories
            epic_context = await self.atlassian.get_story_with_context(epic_id)

            if not epic_context["issue"]:
                logger.error(f"Could not fetch Epic {epic_id}")
                return results

            # 2. Search for similar projects
            similar_projects = await self.atlassian.search_similar_confluence_docs(
                query=epic_context["issue"].summary,
                limit=5
            )

            # 3. Generate technical spec content
            # (Would use TECHNICAL_SPEC_PROMPT and LLM here)
            spec_content = "# Technical Specification\n\n(Generated content would go here)"
            results["spec_content"] = spec_content

            # 4. Post to Confluence if requested
            if post_to_confluence:
                space_key = confluence_space or self.config.get("atlassian", {}).get("confluence", {}).get("default_space_key", "TECH")

                confluence_url = await self.atlassian.create_technical_spec(
                    epic_id=epic_id,
                    content=spec_content,
                    space_key=space_key
                )

                if confluence_url:
                    results["confluence_url"] = confluence_url
                    logger.info(f"Created technical spec: {confluence_url}")

            results["success"] = True
            return results

        except Exception as e:
            logger.error(f"Epic spec generation failed for {epic_id}: {e}")
            return results

    async def batch_analyze_stories(
        self,
        ticket_ids: list,
        post_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze multiple stories in batch.

        Args:
            ticket_ids: List of Jira ticket identifiers
            post_comments: Whether to post comments to Jira

        Returns:
            Dictionary with batch results
        """
        logger.info(f"Starting batch analysis of {len(ticket_ids)} stories")

        results = {
            "total": len(ticket_ids),
            "successful": 0,
            "failed": 0,
            "results": []
        }

        for ticket_id in ticket_ids:
            try:
                result = await self.analyze_story(
                    ticket_id,
                    post_comment=post_comments
                )

                results["results"].append(result)

                if result["success"]:
                    results["successful"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                logger.error(f"Batch analysis failed for {ticket_id}: {e}")
                results["failed"] += 1

        logger.info(f"Batch analysis complete: {results['successful']}/{results['total']} successful")
        return results

    def _should_estimate(self, analysis) -> bool:
        """
        Determine if story should be estimated based on completeness.

        Args:
            analysis: StoryAnalysisResult

        Returns:
            True if story should be estimated
        """
        min_score = self.config.get("thresholds", {}).get("completeness_score_minimum", 7.0)
        return analysis.completeness_score >= min_score

    def _should_generate_tests(self, analysis) -> bool:
        """
        Determine if tests should be generated.

        Args:
            analysis: StoryAnalysisResult

        Returns:
            True if tests should be generated
        """
        # Generate tests if story has acceptance criteria or is reasonably complete
        return analysis.completeness_score >= 6.0

    async def health_check(self) -> Dict[str, bool]:
        """
        Perform health check on all components.

        Returns:
            Dictionary with component health status
        """
        health = {
            "mcp_connection": False,
            "llama_stack": False,
            "overall": False
        }

        try:
            # Check MCP connection
            health["mcp_connection"] = await self.mcp_client.test_connection()

            # Check Llama Stack (would implement actual health check)
            health["llama_stack"] = True  # Placeholder

            health["overall"] = health["mcp_connection"] and health["llama_stack"]

        except Exception as e:
            logger.error(f"Health check failed: {e}")

        return health
