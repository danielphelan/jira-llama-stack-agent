"""
Jira-Confluence Requirements Analysis Agent
Built on Llama Stack Framework

An intelligent AI agent that automates requirements analysis, complexity estimation,
and technical specification generation for software development teams.
"""

__version__ = "1.0.0"
__author__ = "Llama Stack Team"

from src.agent.core import RequirementsAgent
from src.integrations.mcp_client import AtlassianMCPClient

__all__ = ["RequirementsAgent", "AtlassianMCPClient"]
