# Jira-Confluence Requirements Analysis Agent - User Guide

**Version:** 1.0.0
**Last Updated:** November 17, 2025

Welcome! This guide will help you get started with the Requirements Analysis Agent, whether you're using it locally on your machine or connecting to a remote deployment.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Setup Guide](#local-setup-guide)
4. [Remote Usage Guide](#remote-usage-guide)
5. [Common Workflows](#common-workflows)
6. [Configuration Guide](#configuration-guide)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

The Requirements Analysis Agent automates:
- ✅ **Story Analysis** - Extract requirements, identify gaps
- 📊 **Story Point Estimation** - AI-powered complexity estimates
- 🧪 **Test Case Generation** - Create comprehensive test suites
- 🔍 **Similarity Search** - Find related tickets and documentation
- 📝 **Technical Specs** - Generate Epic technical documentation

**Two Ways to Use:**
1. **Local:** Run on your own machine (full control, requires setup)
2. **Remote:** Connect to a shared agent server (easy, no setup)

---

## Prerequisites

### For Local Setup

**Required:**
- Python 3.11 or higher
- Node.js 18 or higher (for Atlassian MCP Server)
- Git
- 8GB+ RAM recommended
- Atlassian account with API token

**Optional:**
- Docker (for containerized deployment)
- CUDA GPU (for faster inference)

### For Remote Usage

**Required:**
- Python 3.11 or higher (just to run the client)
- Network access to agent server
- Atlassian API token (your own credentials)

---

## Local Setup Guide

Follow these step-by-step instructions to run the agent on your local machine.

### Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/your-org/jira-llama-stack-agent.git
cd jira-llama-stack-agent

# Verify you're in the right directory
ls -la
# You should see: config/, src/, requirements.txt, etc.
```

### Step 2: Set Up Python Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep llama-stack
# Should show: llama-stack, llama-stack-client
```

**Expected installation time:** 2-5 minutes

### Step 4: Install Atlassian MCP Server

```bash
# Install globally using npm
npm install -g @anthropic/atlassian-mcp-server

# Verify installation
npx @anthropic/atlassian-mcp-server --version
```

**Note:** If you don't want to install globally, the agent will use `npx` automatically.

### Step 5: Get Your Atlassian API Token

1. **Go to:** https://id.atlassian.com/manage-profile/security/api-tokens
2. **Click:** "Create API token"
3. **Label:** "Jira Llama Stack Agent"
4. **Copy** the token (you'll only see it once!)

**Keep this token secure!** It has access to your Jira and Confluence data.

### Step 6: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
nano .env  # or use your preferred editor (vim, code, etc.)
```

**Fill in these required values:**

```bash
# Atlassian Configuration
ATLASSIAN_INSTANCE_URL=https://your-company.atlassian.net
ATLASSIAN_EMAIL=your.email@company.com
ATLASSIAN_API_TOKEN=your-api-token-from-step-5

# Llama Stack Configuration
LLAMA_STACK_BASE_URL=http://localhost:5000

# Model Configuration (optional - uses defaults if not set)
MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
```

**Replace:**
- `your-company` with your Atlassian domain
- `your.email@company.com` with your Atlassian email
- `your-api-token-from-step-5` with the token you copied

**Save and close** the file (Ctrl+X, then Y, then Enter in nano)

### Step 7: Install and Configure Llama Stack

```bash
# Install Llama Stack (if not already installed)
pip install llama-stack llama-stack-client

# Initialize Llama Stack
llama stack init requirements-agent

# This creates a Llama Stack project directory
cd requirements-agent

# Download the Llama 3.3 70B model
# This will take 10-30 minutes depending on your internet speed
llama stack download-model meta-llama/Llama-3.3-70B-Instruct
```

**Note:** The model is approximately 40GB. Make sure you have enough disk space.

### Step 8: Start Llama Stack Server

```bash
# Start the Llama Stack server
llama stack run --config ../config/agent_config.yaml --mcp-config ../config/mcp_config.json

# You should see:
# ✓ Starting Llama Stack server...
# ✓ Model loaded: meta-llama/Llama-3.3-70B-Instruct
# ✓ Server running on http://localhost:5000
```

**Leave this terminal window open!** The server needs to stay running.

### Step 9: Test the Connection

Open a **new terminal window** (keep the server running in the first one):

```bash
# Navigate to the project directory
cd jira-llama-stack-agent

# Activate the virtual environment
source venv/bin/activate

# Run the health check
python example_usage.py
```

**Expected output:**

```
====================================================================
Example 4: Health Check
====================================================================

Checking system health...

Health Status:
   MCP Connection: ✅
   Llama Stack: ✅
   Overall: ✅
```

**If you see ✅ for all checks, you're ready to go!**

### Step 10: Run Your First Analysis

```bash
# Edit example_usage.py to use your ticket ID
nano example_usage.py

# Find this line (around line 30):
ticket_id = "PROJ-123"  # Replace with actual ticket ID

# Change "PROJ-123" to a real Jira ticket from your instance
# For example: "ENG-456"

# Save and run
python example_usage.py
```

**The agent will:**
1. Fetch the Jira ticket
2. Analyze requirements
3. Estimate story points
4. Generate test cases
5. Post results as a comment

**Check your Jira ticket** to see the AI-generated analysis comment!

---

## Remote Usage Guide

If someone has already set up a shared agent server, you can connect to it without running Llama Stack locally.

### Step 1: Install Client Library Only

```bash
# Create a directory for your scripts
mkdir jira-agent-client
cd jira-agent-client

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install only the client library
pip install llama-stack-client requests python-dotenv pyyaml
```

### Step 2: Configure Connection

```bash
# Create .env file
cat > .env <<EOF
# Remote Agent Server
LLAMA_STACK_BASE_URL=https://agent.company.com  # Ask your admin

# Your Atlassian Credentials
ATLASSIAN_INSTANCE_URL=https://your-company.atlassian.net
ATLASSIAN_EMAIL=your.email@company.com
ATLASSIAN_API_TOKEN=your-api-token

# Optional: Agent API Key (if server requires authentication)
AGENT_API_KEY=ask-your-admin
EOF

# Edit with your actual values
nano .env
```

### Step 3: Create Client Script

```bash
# Create a simple client script
cat > analyze_story.py <<'EOF'
#!/usr/bin/env python3
"""
Simple client script for remote agent usage.
"""

import asyncio
import os
from dotenv import load_dotenv
from llama_stack_client import LlamaStackClient

# Load environment variables
load_env()

# Get configuration
AGENT_URL = os.getenv("LLAMA_STACK_BASE_URL")

async def analyze_story(ticket_id: str):
    """Analyze a Jira story using the remote agent."""

    # Connect to remote agent
    client = LlamaStackClient(base_url=AGENT_URL)

    # Call the analysis endpoint
    response = await client.agents.create_turn(
        agent_id="jira-requirements-agent",
        messages=[
            {
                "role": "user",
                "content": f"Analyze Jira story {ticket_id} and post results as a comment"
            }
        ],
        session_id="user-session-123"
    )

    print(f"✅ Analysis complete for {ticket_id}")
    print(f"Response: {response}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze_story.py TICKET-ID")
        print("Example: python analyze_story.py PROJ-123")
        sys.exit(1)

    ticket_id = sys.argv[1]
    asyncio.run(analyze_story(ticket_id))
EOF

# Make it executable
chmod +x analyze_story.py
```

### Step 4: Run Remote Analysis

```bash
# Analyze a story
python analyze_story.py PROJ-123

# Or make it executable and run directly
./analyze_story.py PROJ-123
```

### Step 5: Check Results

The remote agent will:
1. Analyze the story
2. Post results to Jira
3. Return a summary

**Check your Jira ticket** for the analysis comment!

---

## Common Workflows

### Workflow 1: Analyze a Single Story

**Goal:** Get AI analysis for one Jira story

**Steps:**

1. **Identify the ticket** you want to analyze (e.g., `TEAM-456`)

2. **Create a script** or use Python interactive shell:

```python
import asyncio
from src.agent.core import RequirementsAgent

async def main():
    # Initialize agent
    agent = RequirementsAgent(config_path="config/agent_config.yaml")

    # Analyze the story
    results = await agent.analyze_story(
        ticket_id="TEAM-456",
        post_comment=True,      # Post results to Jira
        estimate_points=True,   # Estimate story points
        generate_tests=True     # Generate test cases
    )

    # Print results
    if results["success"]:
        analysis = results["analysis"]
        print(f"✅ Analysis Complete!")
        print(f"   Completeness: {analysis.completeness_score}/10")

        if results["estimation"]:
            est = results["estimation"]
            print(f"   Story Points: {est.estimated_points}")
            print(f"   Confidence: {est.confidence:.0%}")

        if results["tests"]:
            tests = results["tests"]
            print(f"   Test Cases: {tests.total_test_cases}")
            print(f"   - Unit: {len(tests.unit_tests)}")
            print(f"   - Integration: {len(tests.integration_tests)}")
            print(f"   - E2E: {len(tests.e2e_tests)}")
    else:
        print("❌ Analysis failed")

asyncio.run(main())
```

3. **Run the script:**

```bash
python your_script.py
```

4. **Check Jira** for the AI comment with analysis, estimation, and test cases

**Expected time:** 30-60 seconds per story

---

### Workflow 2: Batch Analyze Multiple Stories

**Goal:** Analyze all stories in a sprint or epic

**Steps:**

1. **Get the list of ticket IDs:**

```bash
# Option A: From a text file
cat > tickets.txt <<EOF
TEAM-101
TEAM-102
TEAM-103
TEAM-104
TEAM-105
EOF
```

2. **Create batch analysis script:**

```python
import asyncio
from src.agent.core import RequirementsAgent

async def batch_analyze():
    # Read ticket IDs from file
    with open("tickets.txt", "r") as f:
        ticket_ids = [line.strip() for line in f if line.strip()]

    print(f"📋 Analyzing {len(ticket_ids)} stories...")

    # Initialize agent
    agent = RequirementsAgent()

    # Batch analyze
    results = await agent.batch_analyze_stories(
        ticket_ids=ticket_ids,
        post_comments=True
    )

    # Print summary
    print(f"\n✅ Batch Analysis Complete!")
    print(f"   Successful: {results['successful']}/{results['total']}")
    print(f"   Failed: {results['failed']}/{results['total']}")

    # Print details
    for result in results['results']:
        status = "✅" if result['success'] else "❌"
        ticket = result['ticket_id']
        print(f"   {status} {ticket}")

asyncio.run(batch_analyze())
```

3. **Run:**

```bash
python batch_analyze.py
```

**Expected time:** ~1 minute per story (5 stories = ~5 minutes)

---

### Workflow 3: Generate Epic Technical Specification

**Goal:** Create a comprehensive technical design document for an Epic

**Steps:**

1. **Identify your Epic** (e.g., `TEAM-1000`)

2. **Create generation script:**

```python
import asyncio
from src.agent.core import RequirementsAgent

async def generate_epic_spec():
    # Initialize agent
    agent = RequirementsAgent()

    # Epic ID
    epic_id = "TEAM-1000"

    print(f"📝 Generating technical specification for {epic_id}...")

    # Generate spec
    results = await agent.generate_epic_spec(
        epic_id=epic_id,
        confluence_space="TECH",  # Your Confluence space key
        post_to_confluence=True
    )

    if results["success"]:
        print(f"\n✅ Technical Spec Created!")
        print(f"   Confluence URL: {results['confluence_url']}")
        print(f"\n   Open this URL to view the spec:")
        print(f"   {results['confluence_url']}")
    else:
        print("❌ Spec generation failed")

asyncio.run(generate_epic_spec())
```

3. **Run:**

```bash
python generate_epic_spec.py
```

4. **Review the Confluence page** and refine as needed

**Expected time:** 2-3 minutes

---

### Workflow 4: Custom Analysis Pipeline

**Goal:** Create a custom workflow with specific steps

**Example: Only analyze stories that are "Ready for Dev"**

```python
import asyncio
from src.agent.core import RequirementsAgent

async def custom_workflow():
    agent = RequirementsAgent()

    # Step 1: Get stories in "Ready for Dev" status
    # (Using Atlassian tools directly)
    jql = 'project = TEAM AND status = "Ready for Dev" ORDER BY created DESC'

    search_result = await agent.mcp_client.call_tool(
        "Atlassian:searchJiraIssuesUsingJql",
        {
            "jql": jql,
            "maxResults": 20,
            "fields": ["key", "summary", "status"]
        }
    )

    if not search_result.success:
        print("❌ Search failed")
        return

    issues = search_result.data.get("issues", [])
    print(f"📋 Found {len(issues)} stories in Ready for Dev")

    # Step 2: Analyze each one
    for issue in issues:
        ticket_id = issue["key"]
        print(f"\n🔍 Analyzing {ticket_id}...")

        # Step 3: Analyze story
        analysis = await agent.tools.analyze_user_story(ticket_id)

        if analysis:
            print(f"   Completeness: {analysis.completeness_score}/10")

            # Step 4: Only estimate if complete enough
            if analysis.completeness_score >= 7.0:
                estimation = await agent.tools.estimate_story_points(ticket_id)

                if estimation:
                    print(f"   Estimated: {estimation.estimated_points} points")

                    # Step 5: Post comment
                    comment = await agent.tools.format_analysis_comment(
                        ticket_id, analysis, estimation, None
                    )

                    await agent.mcp_client.call_tool(
                        "Atlassian:addCommentToJiraIssue",
                        {
                            "issueIdOrKey": ticket_id,
                            "body": comment
                        }
                    )
                    print(f"   ✅ Comment posted")
            else:
                print(f"   ⚠️  Story not complete enough (score: {analysis.completeness_score})")

asyncio.run(custom_workflow())
```

---

### Workflow 5: Interactive CLI Usage

**Goal:** Use the agent interactively

**Create an interactive script:**

```python
#!/usr/bin/env python3
"""
Interactive CLI for Requirements Analysis Agent
"""

import asyncio
from src.agent.core import RequirementsAgent

def print_menu():
    print("\n" + "="*60)
    print("Requirements Analysis Agent - Interactive Mode")
    print("="*60)
    print("\n1. Analyze single story")
    print("2. Batch analyze stories")
    print("3. Generate Epic spec")
    print("4. Health check")
    print("5. Exit")
    print()

async def main():
    agent = RequirementsAgent()

    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            ticket_id = input("Enter ticket ID (e.g., PROJ-123): ").strip()
            print(f"\n🔍 Analyzing {ticket_id}...")

            results = await agent.analyze_story(
                ticket_id=ticket_id,
                post_comment=True,
                estimate_points=True,
                generate_tests=True
            )

            if results["success"]:
                print(f"✅ Analysis complete! Check Jira for results.")
            else:
                print(f"❌ Analysis failed")

        elif choice == "2":
            print("Enter ticket IDs (comma-separated):")
            tickets_input = input("> ").strip()
            ticket_ids = [t.strip() for t in tickets_input.split(",")]

            print(f"\n📋 Analyzing {len(ticket_ids)} stories...")

            results = await agent.batch_analyze_stories(
                ticket_ids=ticket_ids,
                post_comments=True
            )

            print(f"✅ Complete: {results['successful']}/{results['total']}")

        elif choice == "3":
            epic_id = input("Enter Epic ID: ").strip()
            space = input("Confluence space key (default: TECH): ").strip() or "TECH"

            print(f"\n📝 Generating spec for {epic_id}...")

            results = await agent.generate_epic_spec(
                epic_id=epic_id,
                confluence_space=space,
                post_to_confluence=True
            )

            if results["success"]:
                print(f"✅ Spec created: {results['confluence_url']}")

        elif choice == "4":
            print("\n🏥 Running health check...")
            health = await agent.health_check()

            print(f"   MCP: {'✅' if health['mcp_connection'] else '❌'}")
            print(f"   Llama Stack: {'✅' if health['llama_stack'] else '❌'}")

        elif choice == "5":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
```

**Save as `interactive_agent.py` and run:**

```bash
python interactive_agent.py
```

---

## Configuration Guide

### Understanding `config/agent_config.yaml`

```yaml
# Core agent settings
agent:
  name: "jira-confluence-requirements-agent"
  version: "1.0.0"

# Llama Stack configuration
llama_stack:
  model:
    name: "meta-llama/Llama-3.3-70B-Instruct"
    temperature: 0.7        # Higher = more creative, Lower = more deterministic
    max_tokens: 4096        # Maximum response length

# Features - Enable/disable capabilities
features:
  auto_analysis:
    enabled: true
    trigger_on_story_create: true   # Auto-analyze new stories

  estimation:
    enabled: true
    story_point_scale: [1, 2, 3, 5, 8, 13]  # Fibonacci scale

  test_generation:
    enabled: true
    include_unit_tests: true
    include_integration_tests: true
    include_e2e_tests: true

# Quality thresholds
thresholds:
  completeness_score_minimum: 7.0           # Min score for "ready"
  estimation_confidence_minimum: 0.70       # Min confidence to auto-assign points
  similarity_score_minimum: 0.60            # Min score for related tickets
```

**Common Customizations:**

**1. Change story point scale:**
```yaml
estimation:
  story_point_scale: [1, 2, 4, 8, 16]  # Power of 2
  # or
  story_point_scale: [1, 2, 3, 4, 5]   # Linear
```

**2. Adjust quality thresholds:**
```yaml
thresholds:
  completeness_score_minimum: 8.0     # Stricter
  estimation_confidence_minimum: 0.80  # More confident
```

**3. Disable features:**
```yaml
features:
  test_generation:
    enabled: false  # Skip test generation
```

---

## Troubleshooting

### Issue 1: "MCP Connection Failed"

**Symptoms:**
```
❌ MCP Connection: Failed
Error: Could not connect to Atlassian
```

**Solutions:**

1. **Check your API token:**
```bash
# Verify token in .env
cat .env | grep ATLASSIAN_API_TOKEN

# Test token manually
curl -u "your-email@company.com:your-token" \
  "https://your-company.atlassian.net/rest/api/3/myself"

# Should return your user info
```

2. **Verify instance URL:**
```bash
# Should NOT have trailing slash
✅ ATLASSIAN_INSTANCE_URL=https://company.atlassian.net
❌ ATLASSIAN_INSTANCE_URL=https://company.atlassian.net/
```

3. **Check MCP server installation:**
```bash
npx @anthropic/atlassian-mcp-server --version
# Should show version number
```

4. **Test MCP server directly:**
```bash
# Set environment variables
export ATLASSIAN_INSTANCE_URL="https://your-company.atlassian.net"
export ATLASSIAN_EMAIL="your.email@company.com"
export ATLASSIAN_API_TOKEN="your-token"

# Run MCP server
npx @anthropic/atlassian-mcp-server
```

---

### Issue 2: "Llama Stack Server Not Running"

**Symptoms:**
```
❌ Llama Stack: Failed
Connection refused on localhost:5000
```

**Solutions:**

1. **Check if server is running:**
```bash
# Check if port 5000 is in use
lsof -i :5000
# or on Windows
netstat -ano | findstr :5000
```

2. **Start the server:**
```bash
cd requirements-agent
llama stack run --config ../config/agent_config.yaml
```

3. **Check for errors in server logs:**
```bash
# Look for error messages in the server terminal
# Common issues:
# - Model not downloaded
# - Out of memory
# - Port already in use
```

4. **Use different port:**
```bash
# In .env
LLAMA_STACK_BASE_URL=http://localhost:5001

# Start server on different port
llama stack run --port 5001 --config ../config/agent_config.yaml
```

---

### Issue 3: "Analysis Taking Too Long"

**Symptoms:**
- Analysis runs for 5+ minutes
- No results returned

**Solutions:**

1. **Check model size:**
```yaml
# Use smaller model for faster inference
llama_stack:
  model:
    name: "meta-llama/Llama-3.1-8B-Instruct"  # Smaller, faster
```

2. **Reduce token limit:**
```yaml
llama_stack:
  model:
    max_tokens: 2048  # Reduced from 4096
```

3. **Use GPU acceleration:**
```bash
# Check if GPU is available
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-enabled PyTorch if available
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

### Issue 4: "Generated Analysis is Low Quality"

**Symptoms:**
- Analysis is generic or not specific
- Missing key requirements
- Incorrect estimates

**Solutions:**

1. **Increase temperature for more creative analysis:**
```yaml
llama_stack:
  model:
    temperature: 0.8  # Increased from 0.7
```

2. **Provide more context in stories:**
- Ensure stories have descriptions
- Add acceptance criteria
- Link to related documentation

3. **Fine-tune prompts:**
```python
# Edit src/prompts/task_prompts.py
# Add more specific instructions for your domain
```

4. **Check similar stories:**
```python
# Agent uses similar stories for context
# Ensure you have historical data in Jira
```

---

### Issue 5: "Permission Denied Errors"

**Symptoms:**
```
❌ Permission denied: Cannot access project TEAM
```

**Solutions:**

1. **Verify Jira permissions:**
- Log into Jira with your account
- Try to manually access the ticket
- Ensure you have "Browse Projects" permission

2. **Check API token scope:**
- API tokens have the same permissions as your user account
- May need project administrator to grant access

3. **Test with accessible project:**
```python
# Start with a project you definitely have access to
results = await agent.analyze_story(ticket_id="MYPROJECT-1")
```

---

### Issue 6: "Out of Memory Errors"

**Symptoms:**
```
RuntimeError: CUDA out of memory
# or
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Use smaller model:**
```yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.1-8B-Instruct"  # Uses less memory
```

2. **Reduce batch size:**
```python
# Instead of analyzing 50 stories at once
# Break into smaller batches
for i in range(0, len(ticket_ids), 10):
    batch = ticket_ids[i:i+10]
    await agent.batch_analyze_stories(batch)
```

3. **Use CPU instead of GPU:**
```bash
# Set environment variable
export CUDA_VISIBLE_DEVICES=""

# Restart Llama Stack server
```

---

## FAQ

### Q: How much does it cost to run locally?

**A:** Local deployment is free, but requires:
- Hardware: 8GB+ RAM, 50GB+ storage, GPU recommended
- Electricity: ~$0.10-0.50/hour depending on hardware
- Time: Setup takes 1-2 hours initially

### Q: Can I use a different LLM model?

**A:** Yes! Edit `config/agent_config.yaml`:
```yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.1-8B-Instruct"  # Smaller, faster
    # or
    name: "mistralai/Mistral-7B-Instruct-v0.2"  # Alternative model
```

### Q: How accurate are the story point estimates?

**A:** Typically within 20-30% of actual effort, improving over time as the agent learns from your team's history. Always have a human review estimates.

### Q: Can I customize the analysis format?

**A:** Yes! Edit the prompt templates in `src/prompts/task_prompts.py` to change what the agent looks for and how it formats results.

### Q: Is my data sent to external servers?

**A:**
- **Local setup:** No, everything runs on your machine
- **Remote setup:** Only sent to your organization's agent server
- **Never sent to:** OpenAI, Anthropic, or other third parties

### Q: Can I use this with Jira Server (on-premise)?

**A:** The MCP server currently supports Jira Cloud only. For Jira Server, you'd need to modify the integration layer to use Jira Server REST APIs directly.

### Q: How do I update to a newer version?

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Update MCP server
npm update -g @anthropic/atlassian-mcp-server

# Restart Llama Stack server
```

### Q: Can multiple people use the same local installation?

**A:** Yes, but they need to:
1. Use their own API tokens (in their own `.env` file)
2. Connect to the shared Llama Stack server URL
3. Configure their own credentials

### Q: What if a story doesn't have enough information?

**A:** The agent will:
1. Analyze what's available
2. Flag the low completeness score (e.g., 4.5/10)
3. List specific missing information
4. Suggest questions for the product owner

---

## Next Steps

Now that you're set up, try these:

1. ✅ **Analyze your first story** - See how the agent works
2. 📊 **Review the results** - Check the Jira comment
3. 🔧 **Customize settings** - Adjust thresholds and features
4. 📈 **Batch analyze** - Process multiple stories
5. 📝 **Generate Epic spec** - Create technical documentation

**Need help?**
- Check the [Troubleshooting Guide](docs/guides/TROUBLESHOOTING.md)
- Read the [API Reference](docs/guides/API_REFERENCE.md)
- File an issue on GitHub

---

**Happy analyzing! 🚀**
