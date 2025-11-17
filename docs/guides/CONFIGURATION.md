# Configuration Reference

Complete configuration guide for the Requirements Analysis Agent.

---

## Table of Contents

1. [Configuration Files Overview](#configuration-files-overview)
2. [Environment Variables](#environment-variables)
3. [Agent Configuration](#agent-configuration)
4. [MCP Configuration](#mcp-configuration)
5. [Feature Flags](#feature-flags)
6. [Thresholds and Tuning](#thresholds-and-tuning)
7. [Advanced Configuration](#advanced-configuration)
8. [Examples](#examples)

---

## Configuration Files Overview

The agent uses three main configuration sources:

| File | Purpose | Format | Required |
|------|---------|--------|----------|
| `.env` | Secrets and credentials | ENV | Yes |
| `config/agent_config.yaml` | Agent behavior and features | YAML | Yes |
| `config/mcp_config.json` | MCP server settings | JSON | Yes |

**Configuration Priority:**
1. Environment variables (highest)
2. Command-line arguments
3. Configuration files
4. Default values (lowest)

---

## Environment Variables

### Required Variables

#### Atlassian Configuration

```bash
# Your Atlassian instance URL (no trailing slash)
ATLASSIAN_INSTANCE_URL=https://your-company.atlassian.net

# Your Atlassian account email
ATLASSIAN_EMAIL=your.email@company.com

# API token from https://id.atlassian.com/manage-profile/security/api-tokens
ATLASSIAN_API_TOKEN=your-api-token-here
```

**Getting API Token:**
1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Label it: "Jira Llama Stack Agent"
4. Copy token (shown only once!)
5. Paste into `.env`

#### Llama Stack Configuration

```bash
# Llama Stack server URL
LLAMA_STACK_BASE_URL=http://localhost:5000

# Optional: API key if server requires authentication
LLAMA_STACK_API_KEY=
```

---

### Optional Variables

#### Cloud ID

```bash
# Atlassian cloud ID (auto-discovered if not set)
ATLASSIAN_CLOUD_ID=12345-abcde-67890

# To find your cloud ID:
# 1. Go to https://your-company.atlassian.net/_edge/tenant_info
# 2. Look for "cloudId" field
```

**When to set:** Only if auto-discovery fails

#### Model Configuration

```bash
# Model to use (default: meta-llama/Llama-3.3-70B-Instruct)
MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct

# Embedding model for vector search
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

#### Storage

```bash
# Vector store persistence directory
CHROMA_PERSIST_DIR=./data/chroma

# Collection name for embeddings
CHROMA_COLLECTION_NAME=project_knowledge
```

#### Logging

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file path
LOG_FILE=./logs/agent.log
```

#### Notifications (Optional)

```bash
# Slack webhook for notifications
SLACK_WEBHOOK_URL=

# SMTP for email notifications
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
```

#### Feature Flags (Override YAML)

```bash
# Enable/disable features via environment
ENABLE_AUTO_ANALYSIS=true
ENABLE_AUTO_GENERATION=true
ENABLE_TEST_GENERATION=true
ENABLE_TECHNICAL_SPECS=true
```

---

## Agent Configuration

`config/agent_config.yaml` controls all agent behavior.

### Basic Structure

```yaml
agent:
  name: "jira-confluence-requirements-agent"
  version: "1.0.0"
  description: "AI-powered requirements analysis"

llama_stack:
  # Model settings
  # Memory settings
  # Safety settings

atlassian:
  # MCP server settings
  # Jira settings
  # Confluence settings

features:
  # Feature flags

workflow:
  # Workflow settings

thresholds:
  # Quality thresholds

customization:
  # Team-specific settings
```

---

### Llama Stack Configuration

#### Model Settings

```yaml
llama_stack:
  model:
    # Model name/ID
    name: "meta-llama/Llama-3.3-70B-Instruct"
    model_id: "meta-llama/Llama-3.3-70B-Instruct"

    # Sampling temperature (0.0 - 1.0)
    # Lower = more deterministic, Higher = more creative
    temperature: 0.7

    # Maximum tokens in response
    max_tokens: 4096

    # Top-p sampling (0.0 - 1.0)
    top_p: 0.9
```

**Model Options:**

| Model | Size | Speed | Quality | RAM Required |
|-------|------|-------|---------|--------------|
| Llama-3.3-70B-Instruct | 70B | Slow | Excellent | 40GB+ |
| Llama-3.1-8B-Instruct | 8B | Fast | Good | 8GB |
| Llama-3.1-70B-Instruct | 70B | Slow | Excellent | 40GB+ |

**Temperature Guide:**

- `0.0-0.3`: Very deterministic, consistent (good for structured output)
- `0.4-0.6`: Balanced, reliable
- `0.7-0.8`: Creative, diverse (default)
- `0.9-1.0`: Very creative, unpredictable

#### Memory Settings

```yaml
llama_stack:
  memory:
    # Vector store provider
    provider: "chromadb"

    # Collection name for storing embeddings
    collection_name: "project_knowledge"

    # Embedding model for similarity search
    embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

    # Persistence directory
    persist_directory: "./data/chroma"
```

#### Safety Settings

```yaml
llama_stack:
  safety:
    # Enable Llama Guard content filtering
    enabled: true

    # Safety model
    model: "llama-guard-3-8b"

    # Shield level: low, medium, high
    shield_level: "medium"
```

#### Inference Settings

```yaml
llama_stack:
  inference:
    # Inference provider
    provider: "meta-llama"

    # Base URL (can be overridden by env var)
    base_url: "http://localhost:5000"
```

---

### Atlassian Configuration

#### MCP Server

```yaml
atlassian:
  mcp_server:
    # Enable MCP integration
    enabled: true

    # Transport: "sse" (Server-Sent Events) or "stdio"
    transport: "sse"

  # Cloud ID (auto-discovered if null)
  cloud_id: null
```

#### Confluence Settings

```yaml
atlassian:
  confluence:
    # Default space for technical specs
    default_space_key: "TECH"

    # Template page ID for specs (optional)
    tech_spec_template_id: null
```

#### Jira Settings

```yaml
atlassian:
  jira:
    # Default project key (auto-detected if null)
    default_project_key: null
```

---

### Feature Flags

Enable or disable agent capabilities.

#### Auto-Analysis

```yaml
features:
  auto_analysis:
    # Enable automatic analysis
    enabled: true

    # Trigger on new story creation
    trigger_on_story_create: true

    # Trigger on story updates
    trigger_on_story_update: true

    # Minimum confidence to auto-comment
    min_confidence_to_auto_comment: 0.70
```

#### Auto-Generation

```yaml
features:
  auto_generation:
    # Generate missing descriptions
    description:
      enabled: true
      require_approval: true  # Flag for human review
      confidence_threshold: 0.75
      max_length: 2000

    # Generate missing acceptance criteria
    acceptance_criteria:
      enabled: true
      require_approval: true
      confidence_threshold: 0.80
      min_criteria_count: 3
      max_criteria_count: 15
```

#### Estimation

```yaml
features:
  estimation:
    # Enable story point estimation
    enabled: true

    # Historical data window (days)
    historical_window_days: 180

    # Minimum similar stories needed
    min_similar_stories: 3

    # Story point scale (Fibonacci recommended)
    story_point_scale: [1, 2, 3, 5, 8, 13]

    # Default points if estimation fails
    default_story_points: 3
```

**Story Point Scales:**

```yaml
# Fibonacci (recommended)
story_point_scale: [1, 2, 3, 5, 8, 13]

# Powers of 2
story_point_scale: [1, 2, 4, 8, 16]

# Linear
story_point_scale: [1, 2, 3, 4, 5]

# T-shirt sizes (map to numbers separately)
story_point_scale: [1, 3, 5, 8, 13]  # XS, S, M, L, XL
```

#### Test Generation

```yaml
features:
  test_generation:
    # Enable test case generation
    enabled: true

    # Test types to generate
    include_unit_tests: true
    include_integration_tests: true
    include_e2e_tests: true

    # Minimum test cases per acceptance criterion
    min_test_cases_per_ac: 2
```

#### Technical Specifications

```yaml
features:
  technical_specs:
    # Enable Epic spec generation
    enabled: true

    # Auto-generate for new Epics
    auto_generate_for_epics: true

    # Include architecture diagrams
    include_architecture_diagrams: true

    # Include sequence diagrams
    include_sequence_diagrams: true

    # Include test strategy
    include_test_strategy: true
```

#### Similarity Search

```yaml
features:
  similarity_search:
    # Enable Rovo search
    enabled: true

    # Maximum results to return
    max_results: 10

    # Minimum similarity score (0.0-1.0)
    min_similarity_score: 0.60

    # Search Confluence docs
    search_confluence: true

    # Search Jira issues
    search_jira: true
```

---

### Workflow Configuration

```yaml
workflow:
  # Status transitions after agent actions
  story_status_after_analysis: "Ready for Estimation"
  epic_status_after_spec: "Ready for Planning"

  # Statuses that require approval before transition
  require_approval_statuses: ["In Analysis", "Needs Review"]

  # Automation flags
  auto_transition_status: false
  auto_assign_story_points: false
  auto_link_tickets: true
  auto_create_confluence_pages: true
```

---

### Thresholds and Quality Gates

```yaml
thresholds:
  # Minimum completeness score (0.0-10.0)
  # Stories below this are flagged as incomplete
  completeness_score_minimum: 7.0

  # Minimum estimation confidence (0.0-1.0)
  # Estimates below this require human review
  estimation_confidence_minimum: 0.70

  # Minimum similarity score (0.0-1.0)
  # Results below this are filtered out
  similarity_score_minimum: 0.60

  # Minimum test coverage (0.0-1.0)
  # Test suites below this are flagged
  test_coverage_minimum: 0.85

  # Performance thresholds (seconds)
  max_analysis_time_seconds: 30
  max_spec_generation_time_seconds: 120
```

**Adjusting Thresholds:**

**Stricter (Higher Quality):**
```yaml
thresholds:
  completeness_score_minimum: 8.5
  estimation_confidence_minimum: 0.85
  similarity_score_minimum: 0.75
```

**Looser (More Permissive):**
```yaml
thresholds:
  completeness_score_minimum: 6.0
  estimation_confidence_minimum: 0.60
  similarity_score_minimum: 0.50
```

---

### Customization

Team-specific settings.

#### Estimation Weights

```yaml
customization:
  # Default weights for all teams
  default_estimation_weights:
    api_complexity: 1.0
    database_changes: 1.0
    ui_complexity: 1.0
    testing_complexity: 1.0
    integration_complexity: 1.0
```

**Per-Team Weights (Advanced):**

```yaml
customization:
  # Override weights per team
  team_estimation_weights:
    backend-team:
      api_complexity: 1.5       # Backend team weights APIs higher
      database_changes: 1.3
      ui_complexity: 0.5        # Lower weight for UI
    frontend-team:
      api_complexity: 0.8
      database_changes: 0.5
      ui_complexity: 1.5        # Frontend team weights UI higher
```

#### Story Point Scale

```yaml
customization:
  # Use Fibonacci scale
  use_fibonacci_scale: true

  # Story point scale (used if use_fibonacci_scale is false)
  story_point_scale: [1, 2, 3, 5, 8, 13]
```

#### Test Frameworks

```yaml
customization:
  # Test framework by language
  test_frameworks:
    javascript: "jest"
    typescript: "jest"
    python: "pytest"
    java: "junit"
    go: "testing"
    ruby: "rspec"
    csharp: "nunit"
```

---

### Notifications

```yaml
notifications:
  # Slack notifications
  slack:
    enabled: false
    webhook_url: null
    notify_on_analysis_complete: true
    notify_on_spec_created: true

  # Email notifications
  email:
    enabled: false
    smtp_server: null
    smtp_port: 587
    notify_on_analysis_complete: true
    notify_on_spec_created: true
```

---

### Logging

```yaml
logging:
  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: "INFO"

  # Log format: "standard" or "json"
  format: "json"

  # Output: "stdout", "file", or "both"
  output: "stdout"

  # Log file path (if output includes "file")
  log_file: "./logs/agent.log"
```

---

### Monitoring

```yaml
monitoring:
  # Enable Prometheus metrics
  enabled: true

  # Metrics HTTP port
  metrics_port: 9090

  # Enable health check endpoint
  health_check_enabled: true
```

---

## MCP Configuration

`config/mcp_config.json` configures the MCP server.

### Basic Configuration

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/atlassian-mcp-server"
      ],
      "env": {
        "ATLASSIAN_INSTANCE_URL": "${ATLASSIAN_INSTANCE_URL}",
        "ATLASSIAN_EMAIL": "${ATLASSIAN_EMAIL}",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    }
  }
}
```

**Key Fields:**

- `command`: How to run MCP server (`npx` or path to executable)
- `args`: Command-line arguments
- `env`: Environment variables (uses `${VAR}` syntax for substitution)

### Alternative: Installed MCP Server

If you installed MCP server globally:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "atlassian-mcp-server",
      "args": [],
      "env": {
        "ATLASSIAN_INSTANCE_URL": "${ATLASSIAN_INSTANCE_URL}",
        "ATLASSIAN_EMAIL": "${ATLASSIAN_EMAIL}",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    }
  }
}
```

### stdio vs SSE Transport

**Server-Sent Events (SSE) - Default:**
```json
{
  "mcpServers": {
    "atlassian": {
      "transport": "sse",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

**stdio (Standard Input/Output):**
```json
{
  "mcpServers": {
    "atlassian": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/atlassian-mcp-server"]
    }
  }
}
```

---

## Advanced Configuration

### Multiple Atlassian Instances

```yaml
atlassian:
  instances:
    production:
      cloud_id: "prod-cloud-id"
      instance_url: "https://company.atlassian.net"
    staging:
      cloud_id: "staging-cloud-id"
      instance_url: "https://company-staging.atlassian.net"

  # Default instance to use
  default_instance: "production"
```

### Custom Prompts Directory

```yaml
prompts:
  # Directory containing custom prompt templates
  templates_dir: "./custom_prompts"

  # Override specific prompts
  overrides:
    story_analysis: "./custom_prompts/analysis.txt"
    estimation: "./custom_prompts/estimation.txt"
```

### Rate Limiting

```yaml
rate_limiting:
  # Requests per minute
  requests_per_minute: 60

  # Burst allowance
  burst_size: 10

  # Retry configuration
  max_retries: 3
  backoff_multiplier: 2  # Exponential backoff
```

### Caching

```yaml
caching:
  # Enable response caching
  enabled: true

  # Cache TTL (seconds)
  ttl: 3600

  # Cache backend: "memory", "redis", "disk"
  backend: "memory"

  # Redis connection (if backend is "redis")
  redis_url: "redis://localhost:6379"
```

---

## Examples

### Example 1: High-Quality, Slower Analysis

```yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.3-70B-Instruct"
    temperature: 0.8
    max_tokens: 6000

thresholds:
  completeness_score_minimum: 8.5
  estimation_confidence_minimum: 0.85
  similarity_score_minimum: 0.75

features:
  test_generation:
    min_test_cases_per_ac: 3
```

### Example 2: Fast, Good-Enough Analysis

```yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.1-8B-Instruct"
    temperature: 0.5
    max_tokens: 2048

thresholds:
  completeness_score_minimum: 6.0
  estimation_confidence_minimum: 0.60

features:
  test_generation:
    include_integration_tests: false
    include_e2e_tests: false
```

### Example 3: Strict Quality Gates

```yaml
workflow:
  auto_transition_status: false  # Never auto-transition
  auto_assign_story_points: false  # Always require human approval

thresholds:
  completeness_score_minimum: 9.0
  estimation_confidence_minimum: 0.90

features:
  auto_generation:
    description:
      require_approval: true
    acceptance_criteria:
      require_approval: true
```

### Example 4: Automated Workflow

```yaml
workflow:
  auto_transition_status: true
  auto_assign_story_points: true  # Auto-assign if confidence >= threshold
  auto_link_tickets: true

features:
  auto_analysis:
    trigger_on_story_create: true
    trigger_on_story_update: true

thresholds:
  estimation_confidence_minimum: 0.75  # Lower threshold for auto-assign
```

---

## Configuration Validation

Validate your configuration:

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/agent_config.yaml'))"

# Validate JSON syntax
python -c "import json; json.load(open('config/mcp_config.json'))"

# Test configuration loading
python -c "
from src.agent.core import RequirementsAgent
agent = RequirementsAgent(config_path='config/agent_config.yaml')
print('✅ Configuration valid')
"
```

---

## Environment-Specific Configurations

### Development

```yaml
# config/dev_config.yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.1-8B-Instruct"  # Faster

logging:
  level: "DEBUG"

thresholds:
  completeness_score_minimum: 5.0  # Lower for testing
```

### Production

```yaml
# config/prod_config.yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.3-70B-Instruct"  # Best quality

logging:
  level: "INFO"
  output: "file"

thresholds:
  completeness_score_minimum: 7.5

monitoring:
  enabled: true
```

**Usage:**

```python
# Development
agent = RequirementsAgent(config_path="config/dev_config.yaml")

# Production
agent = RequirementsAgent(config_path="config/prod_config.yaml")
```

---

## Best Practices

1. **Never commit `.env`** - It contains secrets
2. **Version control configs** - Commit `agent_config.yaml` and `mcp_config.json`
3. **Use environment variables** - For secrets and instance-specific values
4. **Start conservative** - Use default settings, then tune
5. **Monitor thresholds** - Adjust based on team feedback
6. **Document changes** - Comment why you changed settings
7. **Test after changes** - Run health check after configuration updates

---

## Configuration Troubleshooting

**Issue: Configuration not loading**
```bash
# Check file exists
ls -la config/agent_config.yaml

# Check syntax
python -c "import yaml; print(yaml.safe_load(open('config/agent_config.yaml')))"
```

**Issue: Environment variables not working**
```bash
# Check .env is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('ATLASSIAN_API_TOKEN'))"
```

**Issue: Changes not taking effect**
- Restart Llama Stack server
- Restart agent
- Check you're editing the correct config file

---

For more help, see the [Troubleshooting Guide](TROUBLESHOOTING.md).
