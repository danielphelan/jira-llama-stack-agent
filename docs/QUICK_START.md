# Quick Start Guide - 10 Minutes to First Analysis

This guide gets you analyzing Jira stories in 10 minutes or less.

---

## Choose Your Path

### 🏠 Local Setup (Full Features)
**Time:** 10-15 minutes (+ model download)
**Best for:** Individual developers, full control

[👉 Jump to Local Quick Start](#local-quick-start)

### ☁️ Remote Connection (Easiest)
**Time:** 5 minutes
**Best for:** Teams with shared server

[👉 Jump to Remote Quick Start](#remote-quick-start)

---

## Local Quick Start

### 1. Clone and Install (2 minutes)

```bash
# Clone repo
git clone https://github.com/your-org/jira-llama-stack-agent.git
cd jira-llama-stack-agent

# Create environment and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install MCP server
npm install -g @anthropic/atlassian-mcp-server
```

### 2. Configure (3 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Fill in these 3 values:**
```bash
ATLASSIAN_INSTANCE_URL=https://YOUR-COMPANY.atlassian.net
ATLASSIAN_EMAIL=YOUR-EMAIL@company.com
ATLASSIAN_API_TOKEN=YOUR-TOKEN  # Get from: https://id.atlassian.com/manage-profile/security/api-tokens
```

**Save** (Ctrl+X, Y, Enter)

### 3. Start Llama Stack (30 seconds)

```bash
# In a new terminal
llama stack run --config config/agent_config.yaml
```

**Keep this terminal open!**

### 4. Analyze Your First Story (30 seconds)

```bash
# In another terminal
python3 -c "
import asyncio
from src.agent.core import RequirementsAgent

async def quick_test():
    agent = RequirementsAgent()
    results = await agent.analyze_story(
        ticket_id='PROJ-123',  # 👈 CHANGE THIS to your ticket
        post_comment=True,
        estimate_points=True,
        generate_tests=True
    )
    print('✅ Done! Check Jira for results.' if results['success'] else '❌ Failed')

asyncio.run(quick_test())
"
```

**That's it!** Check your Jira ticket for the AI analysis.

---

## Remote Quick Start

### 1. Install Client (1 minute)

```bash
# Create directory
mkdir jira-agent-client && cd jira-agent-client

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install llama-stack-client python-dotenv
```

### 2. Configure (2 minutes)

```bash
# Create config
cat > .env <<EOF
LLAMA_STACK_BASE_URL=https://agent.company.com  # 👈 Get from your admin

ATLASSIAN_INSTANCE_URL=https://your-company.atlassian.net
ATLASSIAN_EMAIL=your.email@company.com
ATLASSIAN_API_TOKEN=your-token
EOF

nano .env  # Edit with your values
```

### 3. Create Quick Script (1 minute)

```bash
cat > analyze.py <<'EOF'
import asyncio, os
from llama_stack_client import LlamaStackClient
from dotenv import load_dotenv

load_dotenv()

async def analyze(ticket_id):
    client = LlamaStackClient(base_url=os.getenv("LLAMA_STACK_BASE_URL"))
    response = await client.agents.create_turn(
        agent_id="jira-requirements-agent",
        messages=[{"role": "user", "content": f"Analyze {ticket_id}"}],
        session_id="quick-session"
    )
    print(f"✅ Analysis complete for {ticket_id}")

if __name__ == "__main__":
    import sys
    asyncio.run(analyze(sys.argv[1] if len(sys.argv) > 1 else "PROJ-123"))
EOF
```

### 4. Analyze (10 seconds)

```bash
python analyze.py PROJ-123  # 👈 Your ticket ID
```

**Done!** Check Jira for results.

---

## Common Commands

### Analyze One Story
```bash
python -c "
import asyncio
from src.agent.core import RequirementsAgent

asyncio.run(
    RequirementsAgent().analyze_story('PROJ-123', post_comment=True)
)
"
```

### Analyze Multiple Stories
```bash
python -c "
import asyncio
from src.agent.core import RequirementsAgent

asyncio.run(
    RequirementsAgent().batch_analyze_stories(
        ['PROJ-123', 'PROJ-124', 'PROJ-125'],
        post_comments=True
    )
)
"
```

### Generate Epic Spec
```bash
python -c "
import asyncio
from src.agent.core import RequirementsAgent

asyncio.run(
    RequirementsAgent().generate_epic_spec(
        'EPIC-100',
        confluence_space='TECH',
        post_to_confluence=True
    )
)
"
```

### Health Check
```bash
python -c "
import asyncio
from src.agent.core import RequirementsAgent

async def check():
    health = await RequirementsAgent().health_check()
    print('✅ All systems go!' if health['overall'] else '❌ Issues detected')

asyncio.run(check())
"
```

---

## Troubleshooting Quick Fixes

### ❌ "MCP Connection Failed"
```bash
# Check your API token
curl -u "your-email:your-token" \
  "https://your-company.atlassian.net/rest/api/3/myself"
```

### ❌ "Llama Stack Not Running"
```bash
# Check if running
lsof -i :5000

# Start server
llama stack run --config config/agent_config.yaml
```

### ❌ "ModuleNotFoundError"
```bash
# Activate environment
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### ❌ "Permission Denied"
- Verify you can access the Jira ticket manually
- Check your API token has correct permissions

---

## Next Steps

**Once you've analyzed your first story:**

1. 📖 Read the [Full User Guide](USER_GUIDE.md) for detailed workflows
2. 🔧 Customize [Configuration](guides/CONFIGURATION.md)
3. 📊 Check [API Reference](guides/API_REFERENCE.md)
4. 🐛 See [Troubleshooting](guides/TROUBLESHOOTING.md) for more help

---

## One-Liners for Power Users

```bash
# Quick analysis with inline code
python -c "import asyncio; from src.agent.core import RequirementsAgent; asyncio.run(RequirementsAgent().analyze_story('PROJ-123', True, True, True))"

# Batch from JQL query
python -c "import asyncio; from src.agent.core import RequirementsAgent; asyncio.run(RequirementsAgent().batch_analyze_stories(['PROJ-{}'.format(i) for i in range(100, 110)]))"

# Health check
python -c "import asyncio; from src.agent.core import RequirementsAgent; print('✅' if asyncio.run(RequirementsAgent().health_check())['overall'] else '❌')"
```

---

**Ready to go! 🚀**

For detailed documentation, see the [Full User Guide](USER_GUIDE.md).
