"""
Requirements Analysis Agent Core

This module implements the main agent orchestration logic that coordinates
all analysis workflows.
"""

import logging
import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional

from src.providers import ModelProviderFactory, BaseModelProvider
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
        cloud_id: Optional[str] = None,
        provider_override: Optional[str] = None
    ):
        """
        Initialize the Requirements Agent.

        Args:
            config_path: Path to agent configuration file
            llama_stack_url: Legacy parameter for backward compatibility (deprecated)
            cloud_id: Atlassian cloud ID (auto-discovered if None)
            provider_override: Override configured provider (e.g., "ollama", "llama_stack", "openai")
        """
        self.config = self._load_config(config_path)

        # Initialize model provider using the factory pattern
        self.model_provider = self._initialize_provider(provider_override, llama_stack_url)

        # Initialize MCP client (still needs base URL for backward compatibility)
        base_url = self._get_base_url_for_mcp(llama_stack_url)
        self.mcp_client = get_mcp_client(llama_stack_url=base_url, cloud_id=cloud_id)

        # Initialize Atlassian tools
        self.atlassian = AtlassianTools(self.mcp_client)

        # Initialize agent tools with model provider
        self.tools = AgentTools(
            model_provider=self.model_provider,
            atlassian_tools=self.atlassian
        )

        logger.info(f"Requirements Agent initialized with {self.model_provider.__class__.__name__}")

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

    def _initialize_provider(
        self,
        provider_override: Optional[str] = None,
        llama_stack_url: Optional[str] = None
    ) -> BaseModelProvider:
        """
        Initialize the model provider based on configuration.

        Args:
            provider_override: Override the configured provider
            llama_stack_url: Legacy URL parameter (for backward compatibility)

        Returns:
            Initialized model provider instance
        """
        # Get provider configuration
        provider_config = self.config.get("model_provider", {})

        # Determine which provider to use
        provider_type = provider_override or provider_config.get("provider", "ollama")

        # Get provider-specific config
        provider_settings = provider_config.get(provider_type, {})

        # Handle environment variable substitution for API keys
        if "api_key" in provider_settings:
            api_key = provider_settings["api_key"]
            if isinstance(api_key, str) and api_key.startswith("${") and api_key.endswith("}"):
                env_var = api_key[2:-1]
                provider_settings["api_key"] = os.getenv(env_var)

        # Override base_url if llama_stack_url provided (backward compatibility)
        if llama_stack_url and provider_type == "llama_stack":
            provider_settings["base_url"] = llama_stack_url

        # Build final config for factory
        factory_config = {
            "provider": provider_type,
            **provider_settings
        }

        try:
            provider = ModelProviderFactory.create(factory_config)
            logger.info(f"Initialized {provider_type} provider with model: {provider.get_model_name()}")
            return provider
        except Exception as e:
            logger.error(f"Failed to initialize {provider_type} provider: {e}")
            # Fallback to Ollama with default settings
            logger.warning("Falling back to Ollama provider with default settings")
            fallback_config = {
                "provider": "ollama",
                "model_name": "llama3.3:70b",
                "base_url": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 4096
            }
            return ModelProviderFactory.create(fallback_config)

    def _get_base_url_for_mcp(self, llama_stack_url: Optional[str] = None) -> str:
        """
        Get base URL for MCP client (for backward compatibility).

        Args:
            llama_stack_url: Optional override URL

        Returns:
            Base URL string
        """
        if llama_stack_url:
            return llama_stack_url

        # Try to get from provider config
        provider_config = self.config.get("model_provider", {})
        provider_type = provider_config.get("provider", "ollama")

        # Get the base URL from the active provider's config
        provider_settings = provider_config.get(provider_type, {})
        return provider_settings.get("base_url", "http://localhost:5000")

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
            "model_provider": False,
            "overall": False
        }

        try:
            # Check MCP connection
            health["mcp_connection"] = await self.mcp_client.test_connection()

            # Check model provider
            health["model_provider"] = await self.model_provider.health_check()

            health["overall"] = health["mcp_connection"] and health["model_provider"]

        except Exception as e:
            logger.error(f"Health check failed: {e}")

        return health
