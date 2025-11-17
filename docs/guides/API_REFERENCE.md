# API Reference - Requirements Analysis Agent

Complete API documentation for programmatic usage of the Requirements Analysis Agent.

---

## Table of Contents

1. [Core Agent API](#core-agent-api)
2. [Analysis Tools API](#analysis-tools-api)
3. [Atlassian Integration API](#atlassian-integration-api)
4. [MCP Client API](#mcp-client-api)
5. [Data Models](#data-models)
6. [Examples](#examples)

---

## Core Agent API

### RequirementsAgent

Main orchestration class for all agent operations.

#### Constructor

```python
from src.agent.core import RequirementsAgent

agent = RequirementsAgent(
    config_path: str = "config/agent_config.yaml",
    llama_stack_url: Optional[str] = None,
    cloud_id: Optional[str] = None
)
```

**Parameters:**
- `config_path`: Path to YAML configuration file
- `llama_stack_url`: Llama Stack server URL (overrides config)
- `cloud_id`: Atlassian cloud ID (auto-discovered if None)

**Example:**
```python
# Use default configuration
agent = RequirementsAgent()

# Custom configuration
agent = RequirementsAgent(
    config_path="config/custom_config.yaml",
    llama_stack_url="http://remote-server:5000",
    cloud_id="12345-abcde"
)
```

---

#### analyze_story()

Perform complete story analysis workflow.

```python
async def analyze_story(
    ticket_id: str,
    post_comment: bool = True,
    estimate_points: bool = True,
    generate_tests: bool = True
) -> Dict[str, Any]
```

**Parameters:**
- `ticket_id`: Jira ticket identifier (e.g., "PROJ-123")
- `post_comment`: Whether to post analysis as Jira comment
- `estimate_points`: Whether to estimate story points
- `generate_tests`: Whether to generate test cases

**Returns:**
```python
{
    "ticket_id": str,
    "success": bool,
    "analysis": StoryAnalysisResult,      # or None
    "estimation": EstimationResult,        # or None
    "tests": TestSuiteResult,             # or None
    "comment_posted": bool
}
```

**Example:**
```python
results = await agent.analyze_story(
    ticket_id="TEAM-456",
    post_comment=True,
    estimate_points=True,
    generate_tests=True
)

if results["success"]:
    analysis = results["analysis"]
    print(f"Completeness: {analysis.completeness_score}/10")

    if results["estimation"]:
        print(f"Story Points: {results['estimation'].estimated_points}")

    if results["tests"]:
        print(f"Test Cases: {results['tests'].total_test_cases}")
```

---

#### batch_analyze_stories()

Analyze multiple stories in batch.

```python
async def batch_analyze_stories(
    ticket_ids: List[str],
    post_comments: bool = True
) -> Dict[str, Any]
```

**Parameters:**
- `ticket_ids`: List of Jira ticket identifiers
- `post_comments`: Whether to post comments to Jira

**Returns:**
```python
{
    "total": int,
    "successful": int,
    "failed": int,
    "results": List[Dict[str, Any]]  # Individual story results
}
```

**Example:**
```python
tickets = ["TEAM-100", "TEAM-101", "TEAM-102"]
results = await agent.batch_analyze_stories(tickets, post_comments=True)

print(f"Processed: {results['successful']}/{results['total']}")

for result in results["results"]:
    print(f"{result['ticket_id']}: {'✅' if result['success'] else '❌'}")
```

---

#### generate_epic_spec()

Generate technical specification for an Epic.

```python
async def generate_epic_spec(
    epic_id: str,
    confluence_space: Optional[str] = None,
    post_to_confluence: bool = True
) -> Dict[str, Any]
```

**Parameters:**
- `epic_id`: Jira Epic identifier
- `confluence_space`: Confluence space key (from config if None)
- `post_to_confluence`: Whether to create Confluence page

**Returns:**
```python
{
    "epic_id": str,
    "success": bool,
    "spec_content": str,          # Markdown content
    "confluence_url": str         # or None
}
```

**Example:**
```python
results = await agent.generate_epic_spec(
    epic_id="TEAM-1000",
    confluence_space="TECH",
    post_to_confluence=True
)

if results["success"]:
    print(f"Spec created: {results['confluence_url']}")
```

---

#### health_check()

Perform health check on all components.

```python
async def health_check() -> Dict[str, bool]
```

**Returns:**
```python
{
    "mcp_connection": bool,
    "llama_stack": bool,
    "overall": bool
}
```

**Example:**
```python
health = await agent.health_check()

if health["overall"]:
    print("✅ All systems operational")
else:
    print("❌ Issues detected")
    if not health["mcp_connection"]:
        print("   - MCP connection failed")
    if not health["llama_stack"]:
        print("   - Llama Stack unavailable")
```

---

## Analysis Tools API

### AgentTools

Low-level analysis tools using LLM.

```python
from src.agent.tools import AgentTools
from llama_stack_client import LlamaStackClient
from src.integrations.atlassian_tools import AtlassianTools

tools = AgentTools(
    llama_client: LlamaStackClient,
    atlassian_tools: AtlassianTools,
    model_name: str = "meta-llama/Llama-3.3-70B-Instruct"
)
```

---

#### analyze_user_story()

Analyze user story and extract requirements.

```python
async def analyze_user_story(
    ticket_id: str
) -> Optional[StoryAnalysisResult]
```

**Parameters:**
- `ticket_id`: Jira ticket identifier

**Returns:**
```python
StoryAnalysisResult(
    actors: List[str],
    actions: List[str],
    business_value: str,
    implicit_requirements: List[str],
    assumptions: List[str],
    completeness_score: float,  # 0.0 - 10.0
    missing_requirements: Dict[str, List[str]],
    acceptance_criteria_gaps: List[str],
    risks: List[Dict[str, str]],
    recommendations: List[str],
    questions_for_po: List[str],
    confidence: float  # 0.0 - 1.0
)
```

**Example:**
```python
analysis = await tools.analyze_user_story("TEAM-456")

if analysis:
    print(f"Actors: {', '.join(analysis.actors)}")
    print(f"Completeness: {analysis.completeness_score}/10")

    if analysis.missing_requirements:
        print("\nMissing Requirements:")
        for category, items in analysis.missing_requirements.items():
            print(f"  {category}:")
            for item in items:
                print(f"    - {item}")
```

---

#### estimate_story_points()

Estimate story complexity in points.

```python
async def estimate_story_points(
    ticket_id: str,
    team_velocity: float = 30.0
) -> Optional[EstimationResult]
```

**Parameters:**
- `ticket_id`: Jira ticket identifier
- `team_velocity`: Team's average velocity (points per sprint)

**Returns:**
```python
EstimationResult(
    estimated_points: int,
    confidence: float,
    confidence_interval: List[int],
    reasoning: str,
    similar_stories_analyzed: int,
    comparison_to_similar: str,
    adjustment_factors: Dict[str, float],
    risk_factors: List[str],
    recommendations: List[str]
)
```

**Example:**
```python
estimation = await tools.estimate_story_points(
    ticket_id="TEAM-456",
    team_velocity=35.0
)

if estimation:
    print(f"Estimated Points: {estimation.estimated_points}")
    print(f"Confidence: {estimation.confidence:.0%}")
    print(f"Range: {estimation.confidence_interval[0]}-{estimation.confidence_interval[1]}")
    print(f"\nReasoning: {estimation.reasoning}")
```

---

#### generate_test_cases()

Generate comprehensive test suite.

```python
async def generate_test_cases(
    ticket_id: str,
    tech_stack: Optional[Dict[str, str]] = None
) -> Optional[TestSuiteResult]
```

**Parameters:**
- `ticket_id`: Jira ticket identifier
- `tech_stack`: Technology stack info (optional)

**Returns:**
```python
TestSuiteResult(
    test_framework: str,
    total_test_cases: int,
    coverage_analysis: Dict[str, str],
    unit_tests: List[Dict[str, Any]],
    integration_tests: List[Dict[str, Any]],
    e2e_tests: List[Dict[str, Any]],
    qa_scenarios: List[Dict[str, Any]],
    missing_test_coverage: List[str],
    recommendations: List[str]
)
```

**Example:**
```python
tests = await tools.generate_test_cases(
    ticket_id="TEAM-456",
    tech_stack={
        "backend": "Node.js",
        "frontend": "React",
        "database": "PostgreSQL"
    }
)

if tests:
    print(f"Total Tests: {tests.total_test_cases}")
    print(f"  Unit: {len(tests.unit_tests)}")
    print(f"  Integration: {len(tests.integration_tests)}")
    print(f"  E2E: {len(tests.e2e_tests)}")

    for test in tests.unit_tests[:3]:
        print(f"\n{test['test_name']}:")
        print(f"  Given: {test['given']}")
        print(f"  When: {test['when']}")
        print(f"  Then: {test['then']}")
```

---

#### format_analysis_comment()

Format analysis results as Jira markdown comment.

```python
async def format_analysis_comment(
    ticket_id: str,
    analysis: StoryAnalysisResult,
    estimation: Optional[EstimationResult] = None,
    tests: Optional[TestSuiteResult] = None
) -> str
```

**Returns:** Formatted markdown string

**Example:**
```python
comment = await tools.format_analysis_comment(
    ticket_id="TEAM-456",
    analysis=analysis,
    estimation=estimation,
    tests=tests
)

print(comment)
# 🤖 AI Requirements Analysis
# ✅ Completeness Score: 8.5/10
# ...
```

---

## Atlassian Integration API

### AtlassianTools

High-level Atlassian operations.

```python
from src.integrations.atlassian_tools import AtlassianTools
from src.integrations.mcp_client import AtlassianMCPClient

atlassian = AtlassianTools(mcp_client: AtlassianMCPClient)
```

---

#### get_story_with_context()

Fetch story with full context.

```python
async def get_story_with_context(
    ticket_id: str,
    include_links: bool = True,
    include_similar: bool = True
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "issue": JiraIssue,
    "confluence_docs": List[ConfluencePage],
    "similar_issues": List[SearchResult],
    "links": List[Dict[str, Any]]
}
```

**Example:**
```python
context = await atlassian.get_story_with_context(
    ticket_id="TEAM-456",
    include_links=True,
    include_similar=True
)

issue = context["issue"]
print(f"Story: {issue.summary}")
print(f"Status: {issue.status}")
print(f"Similar issues found: {len(context['similar_issues'])}")
```

---

#### search_similar_issues()

Search for similar Jira issues using Rovo AI.

```python
async def search_similar_issues(
    summary: str,
    description: str = "",
    limit: int = 5,
    min_score: float = 0.6
) -> List[SearchResult]
```

**Example:**
```python
similar = await atlassian.search_similar_issues(
    summary="Implement user authentication",
    description="Add OAuth 2.0 support",
    limit=10,
    min_score=0.7
)

for result in similar:
    print(f"{result.title} (score: {result.score:.2f})")
    print(f"  {result.url}")
```

---

#### create_technical_spec()

Create technical spec in Confluence.

```python
async def create_technical_spec(
    epic_id: str,
    content: str,
    space_key: str = "TECH",
    title: Optional[str] = None
) -> Optional[str]
```

**Returns:** Confluence page URL or None

**Example:**
```python
spec_content = """
# Technical Specification

## Overview
...
"""

url = await atlassian.create_technical_spec(
    epic_id="TEAM-1000",
    content=spec_content,
    space_key="TECH",
    title="Authentication System Design"
)

if url:
    print(f"Spec created: {url}")
```

---

## MCP Client API

### AtlassianMCPClient

Low-level MCP tool execution.

```python
from src.integrations.mcp_client import AtlassianMCPClient

mcp = AtlassianMCPClient(
    llama_stack_url: str = "http://localhost:5000",
    cloud_id: Optional[str] = None,
    auto_discover_cloud_id: bool = True
)
```

---

#### call_tool()

Call an MCP tool asynchronously.

```python
async def call_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    retries: int = 3
) -> MCPToolResult
```

**Parameters:**
- `tool_name`: MCP tool name (e.g., "Atlassian:getJiraIssue")
- `parameters`: Tool parameters as dictionary
- `retries`: Number of retry attempts

**Returns:**
```python
MCPToolResult(
    success: bool,
    data: Optional[Dict[str, Any]],
    error: Optional[str],
    tool_name: Optional[str],
    execution_time_ms: Optional[float]
)
```

**Example:**
```python
# Get a Jira issue
result = await mcp.call_tool(
    "Atlassian:getJiraIssue",
    {
        "issueIdOrKey": "TEAM-456",
        "fields": ["summary", "description", "status"]
    }
)

if result.success:
    issue_data = result.data
    print(f"Summary: {issue_data['fields']['summary']}")
else:
    print(f"Error: {result.error}")
```

---

#### Available MCP Tools

**Jira Tools:**
- `Atlassian:createJiraIssue`
- `Atlassian:getJiraIssue`
- `Atlassian:editJiraIssue`
- `Atlassian:addCommentToJiraIssue`
- `Atlassian:transitionJiraIssue`
- `Atlassian:searchJiraIssuesUsingJql`
- `Atlassian:getJiraIssueRemoteIssueLinks`
- `Atlassian:getVisibleJiraProjects`

**Confluence Tools:**
- `Atlassian:createConfluencePage`
- `Atlassian:updateConfluencePage`
- `Atlassian:getConfluencePage`
- `Atlassian:getPagesInConfluenceSpace`
- `Atlassian:searchConfluenceUsingCql`

**Rovo Search:**
- `Atlassian:search` - Semantic search across Jira and Confluence

**Example: Search with JQL**
```python
result = await mcp.call_tool(
    "Atlassian:searchJiraIssuesUsingJql",
    {
        "jql": "project = TEAM AND status = 'In Progress' ORDER BY created DESC",
        "maxResults": 20,
        "fields": ["key", "summary", "status", "assignee"]
    }
)

if result.success:
    issues = result.data.get("issues", [])
    for issue in issues:
        print(f"{issue['key']}: {issue['fields']['summary']}")
```

---

## Data Models

### JiraIssue

```python
@dataclass
class JiraIssue:
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
```

### ConfluencePage

```python
@dataclass
class ConfluencePage:
    id: str
    title: str
    space_key: str
    space_name: str
    body: str
    url: str
    version: int
    raw_data: Dict[str, Any]
```

### SearchResult

```python
@dataclass
class SearchResult:
    id: str
    title: str
    excerpt: str
    url: str
    score: float
    type: str  # "jira" or "confluence"
    raw_data: Dict[str, Any]
```

---

## Examples

### Example 1: Custom Analysis Pipeline

```python
import asyncio
from src.agent.core import RequirementsAgent

async def custom_pipeline():
    agent = RequirementsAgent()

    # Step 1: Analyze story
    analysis = await agent.tools.analyze_user_story("TEAM-456")

    # Step 2: Only proceed if complete enough
    if analysis and analysis.completeness_score >= 7.0:
        # Step 3: Estimate points
        estimation = await agent.tools.estimate_story_points("TEAM-456")

        # Step 4: Generate tests only if high confidence
        if estimation and estimation.confidence >= 0.75:
            tests = await agent.tools.generate_test_cases("TEAM-456")

            # Step 5: Post combined results
            comment = await agent.tools.format_analysis_comment(
                "TEAM-456", analysis, estimation, tests
            )

            await agent.mcp_client.call_tool(
                "Atlassian:addCommentToJiraIssue",
                {"issueIdOrKey": "TEAM-456", "body": comment}
            )

asyncio.run(custom_pipeline())
```

### Example 2: Find Stories Needing Analysis

```python
async def find_incomplete_stories():
    agent = RequirementsAgent()

    # Search for stories missing acceptance criteria
    result = await agent.mcp_client.call_tool(
        "Atlassian:searchJiraIssuesUsingJql",
        {
            "jql": "project = TEAM AND status = 'To Do' AND 'Acceptance Criteria' is EMPTY",
            "maxResults": 50
        }
    )

    if result.success:
        issues = result.data.get("issues", [])
        print(f"Found {len(issues)} stories needing analysis")

        # Batch analyze
        ticket_ids = [issue["key"] for issue in issues]
        await agent.batch_analyze_stories(ticket_ids, post_comments=True)

asyncio.run(find_incomplete_stories())
```

### Example 3: Weekly Sprint Analysis Report

```python
async def weekly_sprint_report():
    agent = RequirementsAgent()

    # Get all stories in current sprint
    result = await agent.mcp_client.call_tool(
        "Atlassian:searchJiraIssuesUsingJql",
        {
            "jql": "project = TEAM AND sprint in openSprints()",
            "fields": ["key", "summary", "status", "customfield_10016"]  # story points
        }
    )

    if result.success:
        issues = result.data.get("issues", [])

        total_points = 0
        analyzed_count = 0

        for issue in issues:
            ticket_id = issue["key"]

            # Analyze each story
            analysis = await agent.tools.analyze_user_story(ticket_id)

            if analysis:
                analyzed_count += 1

                # Get or estimate points
                points = issue["fields"].get("customfield_10016")
                if not points:
                    estimation = await agent.tools.estimate_story_points(ticket_id)
                    points = estimation.estimated_points if estimation else 0

                total_points += points

        print(f"Sprint Analysis Report")
        print(f"  Stories: {analyzed_count}/{len(issues)}")
        print(f"  Total Points: {total_points}")
        print(f"  Avg Points/Story: {total_points/len(issues):.1f}")

asyncio.run(weekly_sprint_report())
```

---

## Error Handling

All async methods can raise exceptions. Wrap in try-except:

```python
try:
    results = await agent.analyze_story("TEAM-456")
    if results["success"]:
        print("✅ Success")
    else:
        print("❌ Analysis failed but didn't raise exception")
except Exception as e:
    print(f"❌ Error: {e}")
    # Log error, notify user, etc.
```

---

## Rate Limiting

The MCP client includes automatic retry logic for rate limits:
- Exponential backoff: 2s, 4s, 8s
- Max 3 retries by default
- Customize with `retries` parameter

```python
result = await mcp.call_tool(
    "Atlassian:getJiraIssue",
    {"issueIdOrKey": "TEAM-456"},
    retries=5  # More retries
)
```

---

For more examples, see `example_usage.py` in the repository root.
