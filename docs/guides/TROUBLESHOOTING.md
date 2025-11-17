# Troubleshooting Guide

Comprehensive troubleshooting for common issues with the Requirements Analysis Agent.

---

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Authentication Problems](#authentication-problems)
3. [Performance Issues](#performance-issues)
4. [Analysis Quality Issues](#analysis-quality-issues)
5. [Installation Problems](#installation-problems)
6. [Configuration Errors](#configuration-errors)
7. [Runtime Errors](#runtime-errors)
8. [Getting Help](#getting-help)

---

## Connection Issues

### Issue: MCP Connection Failed

**Symptoms:**
```
❌ MCP Connection: Failed
ConnectionError: Cannot connect to Atlassian MCP Server
```

**Diagnosis:**

1. **Check if MCP server is installed:**
```bash
npx @anthropic/atlassian-mcp-server --version
```

Expected: Version number displayed
If not: Install with `npm install -g @anthropic/atlassian-mcp-server`

2. **Test API credentials:**
```bash
curl -u "your-email@company.com:your-api-token" \
  "https://your-company.atlassian.net/rest/api/3/myself"
```

Expected: JSON with your user info
If 401: API token is invalid
If 403: Permissions issue

3. **Verify environment variables:**
```bash
cat .env | grep ATLASSIAN

# Should show:
# ATLASSIAN_INSTANCE_URL=https://company.atlassian.net
# ATLASSIAN_EMAIL=your.email@company.com
# ATLASSIAN_API_TOKEN=xxxxx
```

**Solutions:**

**Solution A: Regenerate API Token**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Revoke old token
3. Create new token
4. Update `.env` file
5. Restart agent

**Solution B: Check Instance URL Format**
```bash
# Correct format (no trailing slash, no paths)
✅ ATLASSIAN_INSTANCE_URL=https://company.atlassian.net
❌ ATLASSIAN_INSTANCE_URL=https://company.atlassian.net/
❌ ATLASSIAN_INSTANCE_URL=https://company.atlassian.net/jira
```

**Solution C: Test MCP Server Directly**
```bash
# Set environment variables
export ATLASSIAN_INSTANCE_URL="https://your-company.atlassian.net"
export ATLASSIAN_EMAIL="your.email@company.com"
export ATLASSIAN_API_TOKEN="your-token"

# Run MCP server
npx @anthropic/atlassian-mcp-server

# Should start without errors
```

If this works, the issue is in the agent configuration. Check `config/mcp_config.json`.

---

### Issue: Llama Stack Server Not Responding

**Symptoms:**
```
❌ Llama Stack: Failed
ConnectionRefusedError: [Errno 61] Connection refused
```

**Diagnosis:**

1. **Check if server is running:**
```bash
# On macOS/Linux
lsof -i :5000

# On Windows
netstat -ano | findstr :5000
```

Expected: Process listening on port 5000
If nothing: Server is not running

2. **Check server logs:**
```bash
# In the terminal where you started Llama Stack
# Look for error messages
```

**Solutions:**

**Solution A: Start the Server**
```bash
cd requirements-agent  # or your Llama Stack project directory
llama stack run --config ../config/agent_config.yaml --mcp-config ../config/mcp_config.json
```

**Solution B: Use Different Port**

If port 5000 is in use:
```bash
# In .env
LLAMA_STACK_BASE_URL=http://localhost:5001

# Start server
llama stack run --port 5001 --config ../config/agent_config.yaml
```

**Solution C: Check Firewall**
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add llama

# Linux (ufw)
sudo ufw allow 5000/tcp

# Windows
# Add firewall rule in Windows Defender Firewall settings
```

**Solution D: Remote Server Connection**

If connecting to remote server:
```bash
# Test connectivity
curl http://remote-server:5000/health

# If timeout, check:
# 1. Server is running
# 2. Network connectivity
# 3. Firewall rules
# 4. Server is listening on 0.0.0.0, not 127.0.0.1
```

---

## Authentication Problems

### Issue: Jira Permission Denied

**Symptoms:**
```
❌ Permission denied: Cannot access project TEAM
403 Forbidden
```

**Diagnosis:**

1. **Test manual access:**
   - Open browser
   - Go to your Jira instance
   - Try to view the ticket manually

   Can you see it? If no → Permissions issue

2. **Check project permissions:**
   - Go to Project Settings → Permissions
   - Verify your user has "Browse Projects" permission

3. **Test API access:**
```bash
curl -u "your-email:your-token" \
  "https://your-company.atlassian.net/rest/api/3/issue/TEAM-456"
```

**Solutions:**

**Solution A: Request Project Access**
1. Contact project administrator
2. Request "Browse Projects" permission
3. Wait for permission grant
4. Test again

**Solution B: Use Different Project**

Start with a project you definitely have access to:
```python
# Test with your personal project first
results = await agent.analyze_story("MYPROJ-1")
```

**Solution C: Check API Token Scope**

API tokens inherit user permissions. If your user account can't access the project, the token can't either.

---

### Issue: Confluence Access Denied

**Symptoms:**
```
❌ Cannot create page in space TECH
403 Forbidden
```

**Solutions:**

1. **Check space permissions:**
   - Go to Confluence
   - Navigate to space settings
   - Verify you have "Add Page" permission

2. **Use different space:**
```python
# Try a space where you're an admin
results = await agent.generate_epic_spec(
    epic_id="EPIC-100",
    confluence_space="YOURSPACE"  # Your personal space
)
```

3. **Request space permissions:**
   - Contact space administrator
   - Request "Add Page" and "Edit Page" permissions

---

## Performance Issues

### Issue: Analysis Taking Too Long

**Symptoms:**
- Analysis runs for 5+ minutes
- Timeout errors
- High CPU/memory usage

**Diagnosis:**

1. **Check model size:**
```bash
# See what model is loaded
cat config/agent_config.yaml | grep "name:"
```

70B model is large and slow without GPU.

2. **Check system resources:**
```bash
# On macOS/Linux
top
htop  # if installed

# On Windows
Task Manager
```

Look for:
- CPU: Should be < 80% sustained
- Memory: Should have 4GB+ free
- Swap: Should be minimal

**Solutions:**

**Solution A: Use Smaller Model**

Edit `config/agent_config.yaml`:
```yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.1-8B-Instruct"  # Much faster!
```

Trade-off: Slightly lower quality analysis, but 5-10x faster.

**Solution B: Enable GPU Acceleration**

If you have NVIDIA GPU:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, install CUDA PyTorch
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**Solution C: Reduce Token Limits**

Edit `config/agent_config.yaml`:
```yaml
llama_stack:
  model:
    max_tokens: 2048  # Reduced from 4096
```

**Solution D: Adjust Temperature**

Lower temperature = faster inference:
```yaml
llama_stack:
  model:
    temperature: 0.5  # Reduced from 0.7
```

**Solution E: Batch Processing**

Instead of analyzing 50 stories at once, batch in groups of 10:
```python
for i in range(0, len(ticket_ids), 10):
    batch = ticket_ids[i:i+10]
    await agent.batch_analyze_stories(batch)
    await asyncio.sleep(5)  # Brief pause between batches
```

---

### Issue: Out of Memory Errors

**Symptoms:**
```
RuntimeError: CUDA out of memory
MemoryError: Unable to allocate array
Process killed (signal 9)
```

**Diagnosis:**

```bash
# Check memory usage
free -h  # Linux
vm_stat  # macOS

# Check GPU memory (if using GPU)
nvidia-smi
```

**Solutions:**

**Solution A: Use Smaller Model**
```yaml
llama_stack:
  model:
    name: "meta-llama/Llama-3.1-8B-Instruct"
```

8B model uses ~8GB RAM vs 70B model using ~40GB RAM.

**Solution B: Use CPU-Only Mode**
```bash
# Disable GPU
export CUDA_VISIBLE_DEVICES=""

# Restart Llama Stack
llama stack run --config config/agent_config.yaml
```

**Solution C: Increase Swap**

Linux:
```bash
# Create 16GB swap file
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

macOS: Swap is automatic, but you may need more RAM.

**Solution D: Use Remote Server**

If your local machine doesn't have enough resources, connect to a remote Llama Stack server with more RAM/GPU.

---

## Analysis Quality Issues

### Issue: Generated Analysis is Generic/Low Quality

**Symptoms:**
- Analysis doesn't mention specific requirements
- Missing obvious gaps
- Estimates are way off
- Test cases are too simple

**Diagnosis:**

1. **Check input quality:**
   - Does the Jira story have a description?
   - Are there acceptance criteria?
   - Is there enough context?

2. **Check similar stories found:**
```python
analysis = await agent.tools.analyze_user_story("TEAM-456")
# Low quality if no similar stories were found
```

**Solutions:**

**Solution A: Improve Story Quality**

Before analyzing, ensure story has:
- Clear description (As a... I want... So that...)
- At least 3-5 acceptance criteria
- Labels and components set
- Links to related documentation

**Solution B: Increase Temperature**

More creative analysis:
```yaml
llama_stack:
  model:
    temperature: 0.8  # Increased from 0.7
```

**Solution C: Customize Prompts**

Edit `src/prompts/task_prompts.py` to add domain-specific guidance:
```python
def STORY_ANALYSIS_PROMPT(...):
    return f"""
    ... existing prompt ...

    ADDITIONAL CONTEXT:
    Our application is a financial trading platform.
    Always consider:
    - Regulatory compliance (SEC, FINRA)
    - Real-time data requirements
    - Audit logging
    - High availability needs
    """
```

**Solution D: Provide More Historical Data**

The agent learns from similar past stories. Ensure:
- Past stories are properly documented
- Story points are recorded
- Stories are linked to related documentation

**Solution E: Fine-Tune Model**

For best results, fine-tune the model on your company's historical stories:
```bash
# (Advanced - requires ML expertise)
llama stack fine-tune --data your-stories.jsonl --model meta-llama/Llama-3.3-70B-Instruct
```

---

### Issue: Story Point Estimates Way Off

**Symptoms:**
- Estimate: 2 points, Actual: 13 points
- Confidence is low (<0.5)
- No similar stories found

**Diagnosis:**

Check what similar stories were used:
```python
estimation = await agent.tools.estimate_story_points("TEAM-456")
print(f"Similar stories analyzed: {estimation.similar_stories_analyzed}")
print(f"Reasoning: {estimation.reasoning}")
```

**Solutions:**

**Solution A: Record Actual Story Points**

After completing stories, update with actual effort:
1. Go to Jira
2. Add a custom field "Actual Story Points"
3. Fill in after completion

The agent will learn from this data.

**Solution B: Adjust Team Velocity**
```python
estimation = await agent.tools.estimate_story_points(
    ticket_id="TEAM-456",
    team_velocity=25.0  # Your actual velocity
)
```

**Solution C: Review Low-Confidence Estimates**

Don't auto-assign points if confidence < 0.75:
```python
if estimation and estimation.confidence >= 0.75:
    # Use the estimate
    points = estimation.estimated_points
else:
    # Flag for planning poker
    print(f"Low confidence ({estimation.confidence}), needs team discussion")
```

**Solution D: Provide More Context**

Add more details to the story:
- Break down into subtasks
- Add technical notes
- Link to architecture docs
- Mention known complexity factors

---

## Installation Problems

### Issue: pip install failures

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement llama-stack-client
```

**Solutions:**

**Solution A: Upgrade pip**
```bash
pip install --upgrade pip setuptools wheel
```

**Solution B: Use Python 3.11+**
```bash
python --version
# Should be 3.11 or higher

# If not, install Python 3.11+
# Then create new venv with correct version
python3.11 -m venv venv
source venv/bin/activate
```

**Solution C: Install from Requirements**
```bash
# Install one by one to identify problem package
pip install llama-stack-client
pip install chromadb
pip install sentence-transformers
# etc.
```

**Solution D: Use Conda (Alternative)**
```bash
conda create -n jira-agent python=3.11
conda activate jira-agent
pip install -r requirements.txt
```

---

### Issue: MCP Server Installation Failed

**Symptoms:**
```
npm ERR! 404 Not Found - GET https://registry.npmjs.org/@anthropic/atlassian-mcp-server
```

**Solutions:**

**Solution A: Check Node.js Version**
```bash
node --version
# Should be v18 or higher

# If not, update Node.js
```

**Solution B: Use npx Instead**

You don't need to install globally. The agent uses `npx` by default:
```bash
# Just test that npx works
npx @anthropic/atlassian-mcp-server --version
```

**Solution C: Check npm Registry**
```bash
npm config get registry
# Should be: https://registry.npmjs.org/

# If different, reset:
npm config set registry https://registry.npmjs.org/
```

---

## Configuration Errors

### Issue: Invalid YAML Configuration

**Symptoms:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solutions:**

**Solution A: Validate YAML Syntax**
```bash
# Use online validator
# Copy config/agent_config.yaml content to:
# https://www.yamllint.com/

# Or use Python
python -c "import yaml; yaml.safe_load(open('config/agent_config.yaml'))"
```

**Solution B: Check Indentation**

YAML requires consistent indentation (2 spaces):
```yaml
✅ Correct:
llama_stack:
  model:
    name: "meta-llama/Llama-3.3-70B-Instruct"

❌ Wrong (mixed tabs/spaces):
llama_stack:
	model:
  name: "meta-llama/Llama-3.3-70B-Instruct"
```

**Solution C: Reset to Default**
```bash
# Restore from example
git checkout config/agent_config.yaml

# Or copy from backup
cp config/agent_config.yaml.example config/agent_config.yaml
```

---

### Issue: Environment Variables Not Loading

**Symptoms:**
```
KeyError: 'ATLASSIAN_API_TOKEN'
None value for required environment variable
```

**Solutions:**

**Solution A: Check .env File Location**
```bash
# Must be in project root
ls -la .env

# If not there:
cp .env.example .env
```

**Solution B: Load Manually in Code**
```python
from dotenv import load_dotenv
load_dotenv()  # Explicitly load

import os
print(os.getenv("ATLASSIAN_API_TOKEN"))  # Should print token
```

**Solution C: Export Variables Manually**
```bash
export ATLASSIAN_INSTANCE_URL="https://company.atlassian.net"
export ATLASSIAN_EMAIL="your.email@company.com"
export ATLASSIAN_API_TOKEN="your-token"

# Then run agent
python example_usage.py
```

---

## Runtime Errors

### Issue: JSON Parsing Errors

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
Failed to parse LLM response as JSON
```

**Cause:** LLM returned text instead of JSON, or malformed JSON.

**Solutions:**

**Solution A: Check Prompt**

Ensure prompt explicitly requests JSON:
```python
messages=[
    {
        "role": "system",
        "content": "You must respond with valid JSON only. No markdown, no explanations."
    },
    ...
]
```

**Solution B: Add JSON Extraction Fallback**

The agent already tries to extract JSON from markdown. Check logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Will show the actual LLM response
```

**Solution C: Increase max_tokens**

LLM may be cutting off mid-JSON:
```yaml
llama_stack:
  model:
    max_tokens: 6000  # Increased
```

**Solution D: Lower Temperature**

More deterministic = better JSON formatting:
```yaml
llama_stack:
  model:
    temperature: 0.3  # Lower = more structured
```

---

### Issue: Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
ImportError: cannot import name 'RequirementsAgent'
```

**Solutions:**

**Solution A: Check Working Directory**
```bash
pwd
# Should be in jira-llama-stack-agent/

# If not:
cd jira-llama-stack-agent
```

**Solution B: Activate Virtual Environment**
```bash
source venv/bin/activate
# Prompt should show (venv)
```

**Solution C: Install in Development Mode**
```bash
pip install -e .
```

**Solution D: Add to PYTHONPATH**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python example_usage.py
```

---

## Getting Help

If you're still stuck after trying these solutions:

### 1. Enable Debug Logging

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Run again and capture full logs.

### 2. Check Agent Health

```python
import asyncio
from src.agent.core import RequirementsAgent

async def check():
    agent = RequirementsAgent()
    health = await agent.health_check()
    print(health)

asyncio.run(check())
```

### 3. Test Components Individually

```python
# Test MCP connection
from src.integrations.mcp_client import get_mcp_client
mcp = get_mcp_client()
result = await mcp.test_connection()
print(f"MCP OK: {result}")

# Test Llama Stack
from llama_stack_client import LlamaStackClient
llama = LlamaStackClient(base_url="http://localhost:5000")
# Try a simple inference
```

### 4. Collect Diagnostic Info

```bash
# System info
python --version
node --version
pip list | grep llama
npm list -g --depth=0

# Configuration
cat config/agent_config.yaml
cat .env | grep -v TOKEN  # Don't share token!

# Logs
tail -n 100 logs/agent.log
```

### 5. File an Issue

Go to: https://github.com/your-org/jira-llama-stack-agent/issues

Include:
- Error message (full traceback)
- What you were trying to do
- Steps to reproduce
- Diagnostic info from above
- **DO NOT include API tokens or passwords!**

---

## Common Error Messages Quick Reference

| Error | Quick Fix |
|-------|-----------|
| `Connection refused` | Start Llama Stack server |
| `403 Forbidden` | Check API token and permissions |
| `404 Not Found` | Check ticket ID exists |
| `CUDA out of memory` | Use smaller model or CPU mode |
| `JSONDecodeError` | Lower temperature, check logs |
| `ModuleNotFoundError` | Activate venv, check working dir |
| `Rate limited` | Built-in retries should handle it, if not wait 60s |
| `Timeout` | Increase timeout or check network |

---

**Still need help?** Join our Slack channel: #jira-agent-support
