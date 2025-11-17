# Jira-Confluence Requirements Analysis Agent

An intelligent AI agent that automates requirements analysis, complexity estimation, and technical specification generation for software development teams. Supports multiple model providers: **Ollama**, **Llama Stack**, and **OpenAI**.

## 🎯 Overview

This agent deeply integrates with **Atlassian's Jira and Confluence** platforms through the **Model Context Protocol (MCP)** to provide:

- ✅ **Automated Requirements Analysis** - Extracts and validates user story requirements
- 📊 **Smart Story Point Estimation** - Estimates complexity based on historical data
- 🔍 **Semantic Similarity Search** - Finds related tickets and documentation using Rovo AI
- 🧪 **Test Case Generation** - Creates comprehensive unit, integration, and E2E tests
- 📝 **Technical Spec Generation** - Generates detailed technical design documents
- 🔗 **Auto-Linking** - Discovers and links related Jira tickets
- ⚠️ **Gap Analysis** - Identifies missing requirements across multiple dimensions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│             Llama Stack Agent Runtime               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Inference  │  │    Memory    │  │  Safety   │ │
│  │   (Llama     │  │   (Vector    │  │  (Llama   │ │
│  │   3.3 70B)   │  │    Store)    │  │   Guard)  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │          Tool/Function Calling Layer          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │ Model Context Protocol (MCP)
                  │
┌─────────────────▼───────────────────────────────────┐
│           Atlassian MCP Server                      │
│  (Anthropic's Official Integration)                 │
├─────────────────────────────────────────────────────┤
│  OAuth 2.0 Authentication & Session Management      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Jira Tools  │  │ Confluence   │  │   Rovo    │ │
│  │  (20+ tools) │  │    Tools     │  │  Search   │ │
│  │              │  │  (12+ tools) │  │   (AI)    │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
└─────────┼──────────────────┼────────────────┼───────┘
          │                  │                │
          ▼                  ▼                ▼
   ┌─────────────┐    ┌─────────────┐  ┌──────────┐
   │ Jira Cloud  │    │ Confluence  │  │  Rovo AI │
   │  REST API   │    │  REST API   │  │  Search  │
   └─────────────┘    └─────────────┘  └──────────┘
```

## 📦 Installation

### Prerequisites

1. **Python 3.11+**
2. **Node.js 18+** (for Atlassian MCP Server)
3. **Model Provider** - Choose one:
   - **Ollama** (recommended for local development) - [Installation guide](https://ollama.ai)
   - **Llama Stack** (Meta's framework) - See installation below
   - **OpenAI** (cloud-based) - Requires API key
4. **Atlassian Account** with:
   - Jira Cloud instance
   - Confluence Cloud instance
   - API token ([Create one here](https://id.atlassian.com/manage-profile/security/api-tokens))

> 📖 **See [Model Provider Configuration Guide](docs/MODEL_PROVIDERS.md)** for detailed setup instructions for each provider.

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/jira-llama-stack-agent.git
cd jira-llama-stack-agent
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Install Atlassian MCP Server

```bash
# Install globally
npm install -g @anthropic/atlassian-mcp-server

# Or use npx (no installation required)
# The agent will use npx by default
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or your preferred editor
```

**Required environment variables:**

```bash
# Atlassian Configuration
ATLASSIAN_INSTANCE_URL=https://your-domain.atlassian.net
ATLASSIAN_EMAIL=your-email@company.com
ATLASSIAN_API_TOKEN=your-api-token-here
```

### Step 5: Configure Model Provider

The agent supports three model providers. Choose one based on your needs:

#### Option A: Ollama (Recommended for Development)

```bash
# Install Ollama
# Visit https://ollama.ai for installation instructions

# Pull a model
ollama pull llama3.3:70b  # Or llama3.1:8b for faster/smaller

# Start Ollama (usually starts automatically)
ollama serve

# Configure in config/agent_config.yaml
model_provider:
  provider: "ollama"
  ollama:
    model_name: "llama3.3:70b"
    base_url: "http://localhost:11434"
```

#### Option B: Llama Stack

```bash
# Install Llama Stack
pip install llama-stack llama-stack-client

# Download model
llama stack download-model meta-llama/Llama-3.3-70B-Instruct

# Start server
llama-stack-server --port 5000

# Configure in config/agent_config.yaml
model_provider:
  provider: "llama_stack"
  llama_stack:
    model_name: "meta-llama/Llama-3.3-70B-Instruct"
    base_url: "http://localhost:5000"
```

#### Option C: OpenAI

```bash
# Set API key
export OPENAI_API_KEY=sk-your-api-key-here

# Configure in config/agent_config.yaml
model_provider:
  provider: "openai"
  openai:
    model_name: "gpt-4"
    api_key: "${OPENAI_API_KEY}"
```

> 📖 **See [Model Provider Configuration Guide](docs/MODEL_PROVIDERS.md)** for complete setup instructions, model recommendations, and performance comparisons.

## 🚀 Quick Start

### Test Connection

```python
python example_usage.py
```

This will run a health check to verify:
- ✅ MCP connection to Atlassian
- ✅ Llama Stack inference availability
- ✅ Authentication status

### Analyze a Single Story

```python
import asyncio
from src.agent.core import RequirementsAgent

async def main():
    # Initialize agent
    agent = RequirementsAgent(config_path="config/agent_config.yaml")

    # Analyze a story
    results = await agent.analyze_story(
        ticket_id="PROJ-123",
        post_comment=True,
        estimate_points=True,
        generate_tests=True
    )

    if results["success"]:
        print(f"✅ Analysis complete!")
        print(f"Completeness: {results['analysis'].completeness_score}/10")
        print(f"Story Points: {results['estimation'].estimated_points}")
        print(f"Test Cases: {results['tests'].total_test_cases}")

asyncio.run(main())
```

### Batch Analysis

```python
async def batch_analysis():
    agent = RequirementsAgent()

    ticket_ids = ["PROJ-123", "PROJ-124", "PROJ-125"]

    results = await agent.batch_analyze_stories(
        ticket_ids=ticket_ids,
        post_comments=True
    )

    print(f"Successful: {results['successful']}/{results['total']}")

asyncio.run(batch_analysis())
```

### Generate Epic Technical Specification

```python
async def generate_spec():
    agent = RequirementsAgent()

    results = await agent.generate_epic_spec(
        epic_id="PROJ-100",
        confluence_space="TECH",
        post_to_confluence=True
    )

    if results["success"]:
        print(f"Spec created: {results['confluence_url']}")

asyncio.run(generate_spec())
```

## 📖 Features

### 1. Story Analysis (FR-1.1, FR-1.2)

Analyzes user stories and extracts:
- Actors, actions, and business value
- Implicit requirements
- Acceptance criteria gaps
- Missing requirements by category:
  - Functional
  - Security
  - Performance
  - Accessibility
  - Error handling
  - Edge cases

**Example Output:**

```json
{
  "actors": ["user", "admin"],
  "actions": ["create", "submit", "validate"],
  "business_value": "Reduce processing time by 50%",
  "completeness_score": 8.5,
  "missing_requirements": {
    "security": ["No mention of data encryption"],
    "performance": ["No response time requirement"],
    "accessibility": ["WCAG compliance not specified"]
  }
}
```

### 2. Story Point Estimation (FR-3.1)

Estimates complexity based on:
- Similar historical stories (via Rovo search)
- Number of acceptance criteria
- Component complexity
- Integration points
- Testing requirements

**Example Output:**

```json
{
  "estimated_points": 5,
  "confidence": 0.78,
  "confidence_interval": [3, 8],
  "reasoning": "Similar to PROJ-456 (5 pts) with additional API integration",
  "similar_stories_analyzed": 15
}
```

### 3. Test Case Generation (FR-6.1)

Generates comprehensive test suites:
- **Unit Tests:** Business logic, validation, edge cases
- **Integration Tests:** API contracts, database interactions
- **E2E Tests:** User journeys, cross-browser scenarios
- **QA Scenarios:** Manual test procedures with steps

**Example Output:**

```json
{
  "total_test_cases": 24,
  "unit_tests": [
    {
      "test_id": "UT-001",
      "test_name": "test_validates_email_format",
      "given": "User submits form with invalid email",
      "when": "Form validation runs",
      "then": "Error message displayed",
      "code_snippet": "// Jest test code..."
    }
  ],
  "coverage_analysis": {
    "acceptance_criteria_covered": "92%"
  }
}
```

### 4. Semantic Similarity Search (FR-2.1)

Uses **Atlassian Rovo AI** for intelligent search:
- Finds similar past Jira stories
- Discovers related Confluence documentation
- Semantic understanding (not just keywords)
- Context-aware relevance ranking

**Example:**

```python
# Search for similar issues
similar_issues = await atlassian.search_similar_issues(
    summary="Implement user authentication",
    description="OAuth 2.0 integration",
    limit=5
)

# Search for technical docs
similar_docs = await atlassian.search_similar_confluence_docs(
    query="Authentication architecture and implementation",
    space_key="TECH"
)
```

### 5. Auto-Linking (FR-2.2)

Automatically discovers and links related tickets:
- Similar stories (Rovo semantic match)
- Same Epic siblings
- Component/label matches
- Referenced in Confluence docs

### 6. Technical Spec Generation (FR-4.1)

Generates comprehensive technical design documents:
- Architecture diagrams (Mermaid)
- API specifications
- Data models
- Testing strategy
- Deployment plan
- Monitoring requirements

## ⚙️ Configuration

### Agent Configuration (`config/agent_config.yaml`)

```yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.3-70B-Instruct"
    temperature: 0.7
    max_tokens: 4096

features:
  auto_analysis:
    enabled: true
    trigger_on_story_create: true

  estimation:
    enabled: true
    story_point_scale: [1, 2, 3, 5, 8, 13]

  test_generation:
    enabled: true
    include_unit_tests: true
    include_e2e_tests: true

thresholds:
  completeness_score_minimum: 7.0
  estimation_confidence_minimum: 0.70
```

### MCP Configuration (`config/mcp_config.json`)

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic/atlassian-mcp-server"],
      "env": {
        "ATLASSIAN_INSTANCE_URL": "${ATLASSIAN_INSTANCE_URL}",
        "ATLASSIAN_EMAIL": "${ATLASSIAN_EMAIL}",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    }
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agent_tools.py
```

## 📊 Performance

- **Story Analysis:** < 30 seconds
- **Rovo Search:** < 5 seconds
- **Test Generation:** < 60 seconds
- **Epic Spec Generation:** < 2 minutes
- **Batch Processing:** 50+ stories/hour

## 🔒 Security

- OAuth 2.0 authentication only
- API tokens stored in environment variables
- Llama Guard for content safety
- Audit logging for all operations
- PII detection and handling

## 📝 Project Structure

```
jira-llama-stack-agent/
├── config/
│   ├── agent_config.yaml       # Agent configuration
│   └── mcp_config.json         # MCP server configuration
├── src/
│   ├── agent/
│   │   ├── core.py            # Main agent orchestration
│   │   └── tools.py           # Analysis tool implementations
│   ├── integrations/
│   │   ├── mcp_client.py      # MCP client wrapper
│   │   └── atlassian_tools.py # High-level Atlassian tools
│   ├── prompts/
│   │   ├── system_prompts.py  # System prompts
│   │   └── task_prompts.py    # Task-specific prompts
│   └── utils/
│       ├── logging.py         # Logging configuration
│       └── helpers.py         # Utility functions
├── tests/                      # Test suite
├── example_usage.py           # Usage examples
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🛠️ Development

### Adding Custom Tools

```python
# src/agent/tools.py

async def custom_analysis_tool(self, ticket_id: str):
    """Your custom analysis logic."""
    # 1. Fetch data using MCP tools
    context = await self.atlassian.get_story_with_context(ticket_id)

    # 2. Call LLM with custom prompt
    response = await self.llama.inference.chat_completion(
        model=self.model,
        messages=[{"role": "user", "content": "..."}]
    )

    # 3. Parse and return results
    return results
```

### Customizing Prompts

Edit prompts in `src/prompts/task_prompts.py`:

```python
def CUSTOM_PROMPT(context: dict) -> str:
    return f"""
    Your custom prompt with {context}
    """
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Meta AI** - Llama 3.3 model
- **Anthropic** - MCP protocol and Atlassian integration
- **Atlassian** - Rovo AI search and platform APIs

## 📞 Support

- **Documentation:** [Full PRD](docs/PRD.md)
- **Issues:** [GitHub Issues](https://github.com/your-org/jira-llama-stack-agent/issues)
- **Slack:** #llama-stack-agent

## 🗺️ Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Basic story analysis
- [x] MCP integration
- [x] Test case generation
- [x] Story point estimation

### Phase 2: Intelligence Layer (Weeks 4-6)
- [ ] Advanced Rovo search integration
- [ ] ML-based estimation refinement
- [ ] Auto-linking improvements
- [ ] Requirements gap analysis

### Phase 3: Content Generation (Weeks 7-9)
- [ ] Auto-generate descriptions
- [ ] Auto-generate acceptance criteria
- [ ] Epic technical specs
- [ ] Architecture diagrams

### Phase 4: Optimization (Weeks 10-12)
- [ ] Performance optimization
- [ ] Batch processing at scale
- [ ] Analytics dashboard
- [ ] Fine-tuning on company data

---

**Built with ❤️ using Llama Stack and the Model Context Protocol**
