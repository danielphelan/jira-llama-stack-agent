# Documentation Index

Welcome to the complete documentation for the Jira-Confluence Requirements Analysis Agent!

---

## 📚 Documentation Overview

This documentation will help you:
- ✅ **Get started** quickly with local or remote setup
- 🔧 **Configure** the agent for your team's needs
- 📖 **Use** the API programmatically
- 🐛 **Troubleshoot** common issues
- 🚀 **Optimize** performance and quality

---

## 🚀 Getting Started

### New Users - Start Here!

1. **[Quick Start Guide](QUICK_START.md)** ⭐ **(Recommended)**
   - 10-minute setup for both local and remote
   - One-command examples
   - Minimal explanations, maximum results

2. **[User Guide](USER_GUIDE.md)** (Full Version)
   - Comprehensive setup instructions
   - Detailed workflows and examples
   - Step-by-step tutorials
   - FAQ section

**Choose Quick Start** if you want to try it immediately.
**Choose User Guide** if you want to understand everything in detail.

---

## 📖 Core Documentation

### [User Guide](USER_GUIDE.md)
**Complete guide for all users**

Topics covered:
- Prerequisites and installation
- Local setup (step-by-step)
- Remote usage (client-only setup)
- Common workflows (5 detailed examples)
- Configuration guide
- Troubleshooting basics
- FAQ

**Best for:** First-time users, team onboarding

---

### [Quick Start Guide](QUICK_START.md)
**Get running in 10 minutes**

Topics covered:
- Local setup (condensed)
- Remote setup (minimal)
- Common commands
- Quick fixes for errors
- One-liners for power users

**Best for:** Experienced developers, quick trials

---

## 🔧 Technical Documentation

### [API Reference](guides/API_REFERENCE.md)
**Complete API documentation**

Topics covered:
- Core Agent API (`RequirementsAgent`)
- Analysis Tools API (`AgentTools`)
- Atlassian Integration API (`AtlassianTools`)
- MCP Client API (`AtlassianMCPClient`)
- Data models and types
- Code examples

**Best for:** Developers integrating the agent, advanced users

---

### [Configuration Reference](guides/CONFIGURATION.md)
**Everything about configuration**

Topics covered:
- Environment variables (required & optional)
- Agent configuration (`agent_config.yaml`)
- MCP configuration (`mcp_config.json`)
- Feature flags
- Thresholds and quality gates
- Team customization
- Advanced settings
- Examples for different scenarios

**Best for:** DevOps, team leads, power users

---

### [Troubleshooting Guide](guides/TROUBLESHOOTING.md)
**Solutions for common problems**

Topics covered:
- Connection issues (MCP, Llama Stack)
- Authentication problems
- Performance issues
- Analysis quality issues
- Installation problems
- Configuration errors
- Runtime errors
- Getting help

**Best for:** When things go wrong

---

## 📂 Quick Links by Task

### I Want To...

**Get Started**
- → [Quick Start - Local](QUICK_START.md#local-quick-start)
- → [Quick Start - Remote](QUICK_START.md#remote-quick-start)
- → [Full Setup Guide](USER_GUIDE.md#local-setup-guide)

**Analyze Stories**
- → [Analyze Single Story](USER_GUIDE.md#workflow-1-analyze-a-single-story)
- → [Batch Analyze](USER_GUIDE.md#workflow-2-batch-analyze-multiple-stories)
- → [Custom Pipeline](guides/API_REFERENCE.md#example-1-custom-analysis-pipeline)

**Generate Content**
- → [Epic Technical Specs](USER_GUIDE.md#workflow-3-generate-epic-technical-specification)
- → [Test Cases](guides/API_REFERENCE.md#generate_test_cases)
- → [Estimates](guides/API_REFERENCE.md#estimate_story_points)

**Configure**
- → [Environment Variables](guides/CONFIGURATION.md#environment-variables)
- → [Feature Flags](guides/CONFIGURATION.md#feature-flags)
- → [Thresholds](guides/CONFIGURATION.md#thresholds-and-quality-gates)
- → [Customize Prompts](guides/CONFIGURATION.md#custom-prompts-directory)

**Troubleshoot**
- → [Connection Problems](guides/TROUBLESHOOTING.md#connection-issues)
- → [Performance Issues](guides/TROUBLESHOOTING.md#performance-issues)
- → [Low Quality Results](guides/TROUBLESHOOTING.md#analysis-quality-issues)
- → [Error Messages](guides/TROUBLESHOOTING.md#common-error-messages-quick-reference)

**Integrate**
- → [API Reference](guides/API_REFERENCE.md)
- → [Python Examples](guides/API_REFERENCE.md#examples)
- → [Data Models](guides/API_REFERENCE.md#data-models)

---

## 🎯 Documentation by Role

### Software Engineers
**Start here:** [Quick Start](QUICK_START.md)
**Then read:** [API Reference](guides/API_REFERENCE.md)
**Useful:** [Common Workflows](USER_GUIDE.md#common-workflows)

### Product Managers
**Start here:** [User Guide - Overview](USER_GUIDE.md#overview)
**Then read:** [Workflow 1: Analyze Story](USER_GUIDE.md#workflow-1-analyze-a-single-story)
**Useful:** [What the agent does](../README.md#features)

### DevOps / Platform Engineers
**Start here:** [Configuration Reference](guides/CONFIGURATION.md)
**Then read:** [Troubleshooting](guides/TROUBLESHOOTING.md)
**Useful:** [Remote Setup](USER_GUIDE.md#remote-usage-guide)

### QA Engineers
**Start here:** [Test Generation](guides/API_REFERENCE.md#generate_test_cases)
**Then read:** [User Guide - Workflow 1](USER_GUIDE.md#workflow-1-analyze-a-single-story)
**Useful:** [Configuration - Test Settings](guides/CONFIGURATION.md#test-generation)

### Team Leads
**Start here:** [User Guide - Overview](USER_GUIDE.md#overview)
**Then read:** [Configuration - Thresholds](guides/CONFIGURATION.md#thresholds-and-quality-gates)
**Useful:** [Customization](guides/CONFIGURATION.md#customization)

---

## 📊 Documentation Stats

| Document | Pages | Topics | Best For |
|----------|-------|--------|----------|
| [Quick Start](QUICK_START.md) | ~8 | 10 | Quick setup |
| [User Guide](USER_GUIDE.md) | ~50 | 30+ | Learning |
| [API Reference](guides/API_REFERENCE.md) | ~40 | 20+ | Integration |
| [Configuration](guides/CONFIGURATION.md) | ~35 | 40+ | Tuning |
| [Troubleshooting](guides/TROUBLESHOOTING.md) | ~30 | 25+ | Fixing |

**Total:** ~160 pages of documentation

---

## 🔍 Search the Documentation

Can't find what you're looking for? Try these:

### Command-Line Search

```bash
# Search all docs
grep -r "your search term" docs/

# Search specific doc
grep -i "mcp connection" docs/USER_GUIDE.md

# Find section headings
grep -r "^##" docs/ | grep -i "your topic"
```

### Common Search Terms

**Setup:**
- "installation"
- "getting started"
- "prerequisites"
- ".env"

**Configuration:**
- "config"
- "yaml"
- "environment variable"
- "feature flag"

**API:**
- "analyze_story"
- "generate_test"
- "estimate"
- "RequirementsAgent"

**Errors:**
- "connection failed"
- "permission denied"
- "timeout"
- "out of memory"

---

## 🆘 Getting Help

### Self-Service

1. **Check FAQ:** [User Guide FAQ](USER_GUIDE.md#faq)
2. **Search docs:** Use `grep` (see above)
3. **Check examples:** [Common Workflows](USER_GUIDE.md#common-workflows)
4. **Try troubleshooting:** [Troubleshooting Guide](guides/TROUBLESHOOTING.md)

### Community Support

1. **GitHub Issues:** https://github.com/your-org/jira-llama-stack-agent/issues
   - Search existing issues first
   - Use issue templates
   - Include logs and config (redact secrets!)

2. **Slack Channel:** #jira-agent-support
   - Quick questions
   - Share tips
   - Report bugs

3. **Email:** support@your-company.com
   - For sensitive issues
   - Enterprise customers

---

## 📝 Contributing to Documentation

Found a typo? Want to add an example? We welcome contributions!

**How to contribute:**

1. **Fork the repository**
2. **Edit the markdown files** in `docs/`
3. **Submit a pull request**

**Documentation style guide:**
- Use clear, simple language
- Include code examples
- Add emoji for visual scanning
- Test all commands before documenting
- Keep examples up-to-date

---

## 📖 Additional Resources

### External Documentation

- **Llama Stack:** https://llama-stack.readthedocs.io/
- **Atlassian API:** https://developer.atlassian.com/cloud/
- **MCP Protocol:** https://github.com/anthropics/mcp
- **Jira REST API:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **Confluence REST API:** https://developer.atlassian.com/cloud/confluence/rest/v2/

### Video Tutorials

*(Coming soon)*

- Getting Started (5 min)
- Configuration Deep Dive (15 min)
- Advanced Workflows (20 min)

### Blog Posts

*(Coming soon)*

- "How we reduced story analysis time by 80%"
- "Tuning the agent for your team"
- "Best practices for AI-powered requirements"

---

## 🗺️ Documentation Roadmap

### Planned Additions

- [ ] Video tutorials
- [ ] Interactive configuration tool
- [ ] More code examples
- [ ] Architecture deep dive
- [ ] Performance tuning guide
- [ ] Security best practices
- [ ] Multi-tenant setup guide
- [ ] Monitoring and observability guide

### Recent Updates

- **2025-11-17:** Initial documentation release
  - User Guide
  - Quick Start
  - API Reference
  - Configuration Reference
  - Troubleshooting Guide

---

## 📄 Document Versions

| Document | Version | Last Updated |
|----------|---------|--------------|
| User Guide | 1.0.0 | 2025-11-17 |
| Quick Start | 1.0.0 | 2025-11-17 |
| API Reference | 1.0.0 | 2025-11-17 |
| Configuration | 1.0.0 | 2025-11-17 |
| Troubleshooting | 1.0.0 | 2025-11-17 |

---

**Happy learning! 🎓**

Need help? Start with the [Quick Start Guide](QUICK_START.md) or ask in #jira-agent-support!
