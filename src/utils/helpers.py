"""
Helper utilities for the agent.
"""

import os
import re
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


def load_env(env_file: str = ".env") -> bool:
    """
    Load environment variables from .env file.

    Args:
        env_file: Path to .env file

    Returns:
        True if loaded successfully, False otherwise
    """
    env_path = Path(env_file)

    if env_path.exists():
        load_dotenv(env_path)
        return True
    else:
        # Try to load from parent directories
        for parent in env_path.parents:
            parent_env = parent / ".env"
            if parent_env.exists():
                load_dotenv(parent_env)
                return True

    return False


def parse_ticket_id(text: str) -> Optional[str]:
    """
    Extract Jira ticket ID from text.

    Args:
        text: Text containing ticket ID

    Returns:
        Ticket ID if found, None otherwise

    Examples:
        >>> parse_ticket_id("PROJ-123")
        'PROJ-123'
        >>> parse_ticket_id("Check out PROJ-456 for details")
        'PROJ-456'
        >>> parse_ticket_id("https://company.atlassian.net/browse/TEAM-789")
        'TEAM-789'
    """
    # Match patterns like PROJ-123 or TEAM-456
    pattern = r'([A-Z]+-\d+)'
    match = re.search(pattern, text)

    if match:
        return match.group(1)

    return None


def validate_ticket_id(ticket_id: str) -> bool:
    """
    Validate Jira ticket ID format.

    Args:
        ticket_id: Ticket ID to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[A-Z]+-\d+$'
    return bool(re.match(pattern, ticket_id))


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def extract_json_from_markdown(text: str) -> str:
    """
    Extract JSON from markdown code blocks.

    Args:
        text: Text potentially containing JSON in code blocks

    Returns:
        Extracted JSON string or original text
    """
    # Try to extract from ```json blocks
    if "```json" in text:
        parts = text.split("```json")
        if len(parts) > 1:
            json_part = parts[1].split("```")[0].strip()
            return json_part

    # Try to extract from ``` blocks
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            json_part = parts[1].strip()
            # Check if it looks like JSON
            if json_part.startswith("{") or json_part.startswith("["):
                return json_part

    return text


def format_list_markdown(items: list, prefix: str = "-") -> str:
    """
    Format a list as markdown.

    Args:
        items: List of items
        prefix: List prefix (- or * or number)

    Returns:
        Formatted markdown string
    """
    if not items:
        return "None"

    return "\n".join([f"{prefix} {item}" for item in items])


def get_env_or_default(key: str, default: str = "") -> str:
    """
    Get environment variable with default fallback.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)
