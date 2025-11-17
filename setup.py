"""
Setup configuration for Jira-Confluence Requirements Analysis Agent.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="jira-llama-stack-agent",
    version="1.0.0",
    author="Llama Stack Team",
    author_email="team@example.com",
    description="AI-powered requirements analysis and technical specification agent for Jira and Confluence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/jira-llama-stack-agent",
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "ruff>=0.1.9",
            "mypy>=1.8.0",
        ],
        "web": [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.26.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jira-agent=src.agent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json"],
    },
    keywords="jira confluence llama-stack requirements-analysis ai agent automation",
    project_urls={
        "Bug Reports": "https://github.com/your-org/jira-llama-stack-agent/issues",
        "Source": "https://github.com/your-org/jira-llama-stack-agent",
        "Documentation": "https://github.com/your-org/jira-llama-stack-agent#readme",
    },
)
