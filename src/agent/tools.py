"""
Agent Tool Implementations

This module implements the core analysis tools that the Llama Stack agent
can use for requirements analysis, estimation, and content generation.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from llama_stack_client import LlamaStackClient

from src.integrations.atlassian_tools import AtlassianTools, JiraIssue
from src.prompts.task_prompts import (
    STORY_ANALYSIS_PROMPT,
    ESTIMATION_PROMPT,
    TEST_GENERATION_PROMPT,
    TECHNICAL_SPEC_PROMPT,
    DESCRIPTION_GENERATION_PROMPT,
    AC_GENERATION_PROMPT
)

logger = logging.getLogger(__name__)


@dataclass
class StoryAnalysisResult:
    """Result from story analysis."""

    actors: List[str]
    actions: List[str]
    business_value: str
    implicit_requirements: List[str]
    assumptions: List[str]
    completeness_score: float
    missing_requirements: Dict[str, List[str]]
    acceptance_criteria_gaps: List[str]
    risks: List[Dict[str, str]]
    recommendations: List[str]
    questions_for_po: List[str]
    confidence: float


@dataclass
class EstimationResult:
    """Result from story point estimation."""

    estimated_points: int
    confidence: float
    confidence_interval: List[int]
    reasoning: str
    similar_stories_analyzed: int
    comparison_to_similar: str
    adjustment_factors: Dict[str, float]
    risk_factors: List[str]
    recommendations: List[str]


@dataclass
class TestSuiteResult:
    """Result from test case generation."""

    test_framework: str
    total_test_cases: int
    coverage_analysis: Dict[str, str]
    unit_tests: List[Dict[str, Any]]
    integration_tests: List[Dict[str, Any]]
    e2e_tests: List[Dict[str, Any]]
    qa_scenarios: List[Dict[str, Any]]
    missing_test_coverage: List[str]
    recommendations: List[str]


class AgentTools:
    """
    High-level analysis tools for the requirements agent.

    These tools use the Llama Stack LLM with prompts to perform
    complex analysis tasks.
    """

    def __init__(
        self,
        llama_client: LlamaStackClient,
        atlassian_tools: AtlassianTools,
        model_name: str = "meta-llama/Llama-3.3-70B-Instruct"
    ):
        """
        Initialize agent tools.

        Args:
            llama_client: Llama Stack client instance
            atlassian_tools: Atlassian integration tools
            model_name: LLM model to use
        """
        self.llama = llama_client
        self.atlassian = atlassian_tools
        self.model = model_name

    async def analyze_user_story(
        self,
        ticket_id: str
    ) -> Optional[StoryAnalysisResult]:
        """
        Analyze a user story and extract structured requirements.

        This implements FR-1.1 and FR-1.2 from the PRD.

        Args:
            ticket_id: Jira ticket identifier

        Returns:
            StoryAnalysisResult or None if analysis fails
        """
        logger.info(f"Analyzing story: {ticket_id}")

        # 1. Fetch story with context
        context = await self.atlassian.get_story_with_context(
            ticket_id,
            include_links=True,
            include_similar=True
        )

        if not context["issue"]:
            logger.error(f"Could not fetch issue {ticket_id}")
            return None

        issue = context["issue"]

        # 2. Prepare similar stories data
        similar_stories = [
            {
                "key": s.id,
                "title": s.title,
                "points": "Unknown",  # Would come from actual data
                "excerpt": s.excerpt
            }
            for s in context["similar_issues"]
        ]

        # 3. Generate analysis prompt
        prompt = STORY_ANALYSIS_PROMPT(
            title=issue.summary,
            description=issue.description or "",
            acceptance_criteria=issue.acceptance_criteria or "",
            labels=issue.labels,
            components=issue.components,
            similar_stories=similar_stories
        )

        # 4. Call LLM for analysis
        try:
            response = await self.llama.inference.chat_completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert requirements analyst. Provide detailed, structured analysis in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4096
            )

            # 5. Parse JSON response
            content = response.content[0].text if response.content else "{}"

            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis_data = json.loads(content)

            # 6. Create result object
            result = StoryAnalysisResult(
                actors=analysis_data.get("actors", []),
                actions=analysis_data.get("actions", []),
                business_value=analysis_data.get("business_value", ""),
                implicit_requirements=analysis_data.get("implicit_requirements", []),
                assumptions=analysis_data.get("assumptions", []),
                completeness_score=analysis_data.get("completeness_score", 0.0),
                missing_requirements=analysis_data.get("missing_requirements", {}),
                acceptance_criteria_gaps=analysis_data.get("acceptance_criteria_gaps", []),
                risks=analysis_data.get("risks", []),
                recommendations=analysis_data.get("recommendations", []),
                questions_for_po=analysis_data.get("questions_for_po", []),
                confidence=0.85  # Could be computed from analysis quality
            )

            logger.info(f"Analysis complete for {ticket_id}: score={result.completeness_score}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response content: {content}")
            return None
        except Exception as e:
            logger.error(f"Story analysis failed: {e}")
            return None

    async def estimate_story_points(
        self,
        ticket_id: str,
        team_velocity: float = 30.0
    ) -> Optional[EstimationResult]:
        """
        Estimate story points based on historical data.

        This implements FR-3.1 from the PRD.

        Args:
            ticket_id: Jira ticket identifier
            team_velocity: Team's average velocity (points per sprint)

        Returns:
            EstimationResult or None if estimation fails
        """
        logger.info(f"Estimating story points for: {ticket_id}")

        # 1. Get story context
        context = await self.atlassian.get_story_with_context(ticket_id)

        if not context["issue"]:
            return None

        issue = context["issue"]

        # 2. Extract acceptance criteria
        ac_list = []
        if issue.acceptance_criteria:
            # Simple split by lines, could be more sophisticated
            ac_list = [
                line.strip("- ").strip()
                for line in issue.acceptance_criteria.split("\n")
                if line.strip() and line.strip().startswith("-")
            ]

        # 3. Prepare similar stories with actual points
        similar_stories = []
        for similar in context["similar_issues"]:
            # In real implementation, fetch actual story points from these issues
            similar_stories.append({
                "key": similar.id,
                "title": similar.title,
                "points": 5,  # Placeholder - would fetch real value
                "actual_points": 5  # Actual effort if available
            })

        # 4. Generate estimation prompt
        prompt = ESTIMATION_PROMPT(
            story_summary=f"{issue.summary}\n\n{issue.description or ''}",
            acceptance_criteria=ac_list,
            similar_stories=similar_stories,
            team_velocity=team_velocity
        )

        # 5. Call LLM
        try:
            response = await self.llama.inference.chat_completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at story point estimation. Provide data-driven estimates in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # Lower temperature for more consistent estimates
                max_tokens=2048
            )

            content = response.content[0].text if response.content else "{}"

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            estimation_data = json.loads(content)

            result = EstimationResult(
                estimated_points=estimation_data.get("estimated_points", 3),
                confidence=estimation_data.get("confidence", 0.0),
                confidence_interval=estimation_data.get("confidence_interval", [2, 5]),
                reasoning=estimation_data.get("reasoning", ""),
                similar_stories_analyzed=estimation_data.get("similar_stories_analyzed", 0),
                comparison_to_similar=estimation_data.get("comparison_to_similar", ""),
                adjustment_factors=estimation_data.get("adjustment_factors", {}),
                risk_factors=estimation_data.get("risk_factors", []),
                recommendations=estimation_data.get("recommendations", [])
            )

            logger.info(f"Estimation complete: {result.estimated_points} points (confidence: {result.confidence})")
            return result

        except Exception as e:
            logger.error(f"Estimation failed: {e}")
            return None

    async def generate_test_cases(
        self,
        ticket_id: str,
        tech_stack: Optional[Dict[str, str]] = None
    ) -> Optional[TestSuiteResult]:
        """
        Generate comprehensive test cases for a story.

        This implements FR-6.1 from the PRD.

        Args:
            ticket_id: Jira ticket identifier
            tech_stack: Technology stack information

        Returns:
            TestSuiteResult or None if generation fails
        """
        logger.info(f"Generating test cases for: {ticket_id}")

        # 1. Get story details
        context = await self.atlassian.get_story_with_context(ticket_id)

        if not context["issue"]:
            return None

        issue = context["issue"]

        # 2. Extract acceptance criteria
        ac_list = []
        if issue.acceptance_criteria:
            ac_list = [
                line.strip("- ").strip()
                for line in issue.acceptance_criteria.split("\n")
                if line.strip() and line.strip().startswith("-")
            ]

        # 3. Default tech stack if not provided
        if not tech_stack:
            tech_stack = {
                "backend": "Node.js/Express",
                "frontend": "React",
                "database": "PostgreSQL"
            }

        test_framework = "Jest"  # Default, could be configured

        # 4. Generate test prompt
        prompt = TEST_GENERATION_PROMPT(
            story_title=issue.summary,
            acceptance_criteria=ac_list,
            tech_stack=tech_stack,
            test_framework=test_framework
        )

        # 5. Call LLM
        try:
            response = await self.llama.inference.chat_completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a QA expert. Generate comprehensive test suites in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=6000  # Tests can be verbose
            )

            content = response.content[0].text if response.content else "{}"

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            test_data = json.loads(content)

            result = TestSuiteResult(
                test_framework=test_data.get("test_framework", test_framework),
                total_test_cases=test_data.get("total_test_cases", 0),
                coverage_analysis=test_data.get("coverage_analysis", {}),
                unit_tests=test_data.get("unit_tests", []),
                integration_tests=test_data.get("integration_tests", []),
                e2e_tests=test_data.get("e2e_tests", []),
                qa_scenarios=test_data.get("qa_scenarios", []),
                missing_test_coverage=test_data.get("missing_test_coverage", []),
                recommendations=test_data.get("recommendations", [])
            )

            logger.info(f"Generated {result.total_test_cases} test cases for {ticket_id}")
            return result

        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return None

    async def format_analysis_comment(
        self,
        ticket_id: str,
        analysis: StoryAnalysisResult,
        estimation: Optional[EstimationResult] = None,
        tests: Optional[TestSuiteResult] = None
    ) -> str:
        """
        Format analysis results as a Jira comment in markdown.

        Args:
            ticket_id: Jira ticket ID
            analysis: Story analysis results
            estimation: Optional estimation results
            tests: Optional test generation results

        Returns:
            Formatted markdown comment
        """
        comment = f"""🤖 **AI Requirements Analysis**

✅ **Completeness Score:** {analysis.completeness_score}/10
📊 **Confidence:** {int(analysis.confidence * 100)}%

---

### 📋 Requirements Summary

**Actors:** {', '.join(analysis.actors) if analysis.actors else 'None identified'}
**Actions:** {', '.join(analysis.actions) if analysis.actions else 'None identified'}
**Business Value:** {analysis.business_value or 'Not clearly stated'}

### ⚠️ Missing Requirements

"""

        # Add missing requirements by category
        for category, items in analysis.missing_requirements.items():
            if items:
                comment += f"\n**{category.replace('_', ' ').title()}:**\n"
                for item in items:
                    comment += f"- {item}\n"

        # Add estimation if available
        if estimation:
            comment += f"""
---

### 🎯 Story Point Estimate

**Recommended Points:** {estimation.estimated_points}
**Confidence:** {int(estimation.confidence * 100)}%
**Range:** {estimation.confidence_interval[0]}-{estimation.confidence_interval[1]} points

**Reasoning:** {estimation.reasoning}

**Similar Stories Analyzed:** {estimation.similar_stories_analyzed}
"""

        # Add test summary if available
        if tests:
            comment += f"""
---

### 🧪 Test Cases Generated

**Total Test Cases:** {tests.total_test_cases}
- Unit Tests: {len(tests.unit_tests)}
- Integration Tests: {len(tests.integration_tests)}
- E2E Tests: {len(tests.e2e_tests)}
- QA Scenarios: {len(tests.qa_scenarios)}

**Coverage:** {tests.coverage_analysis.get('acceptance_criteria_covered', 'N/A')} of acceptance criteria
"""

        # Add recommendations
        if analysis.recommendations:
            comment += "\n### 💡 Recommendations\n\n"
            for rec in analysis.recommendations:
                comment += f"- {rec}\n"

        # Add questions for PO
        if analysis.questions_for_po:
            comment += "\n### ❓ Questions for Product Owner\n\n"
            for question in analysis.questions_for_po:
                comment += f"- {question}\n"

        comment += f"""
---

*Analysis generated by Llama Stack Requirements Agent*
*Last updated: {self._get_timestamp()}*
"""

        return comment

    def _get_timestamp(self) -> str:
        """Get current timestamp in readable format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
