# FAR Search Tool for LangChain

[![PyPI version](https://badge.fury.io/py/far-search-tool.svg)](https://pypi.org/project/far-search-tool/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Tool-green.svg)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **LangChain tool** for semantic search over **Federal Acquisition Regulations (FAR)**.

Enable your AI agents to search and understand U.S. government contracting regulations, procurement rules, and compliance requirements.

**Keywords**: langchain, government contracting, FAR, federal acquisition regulations, procurement, compliance, AI agent tools, RAG, semantic search

## Installation

```bash
pip install far-search-tool
```

## 🚀 Quick Start (30 seconds)

### Step 1: Install

```bash
pip install far-search-tool
```

### Step 2: Use It

```python
from far_search import FARSearchTool

# Auto-registers on first use - no API key needed!
tool = FARSearchTool()
result = tool.invoke({"query": "small business set aside requirements"})
print(result)
```

**That's it!** On first use, you'll see:

```
============================================================
✅ FAR Search Tool - Auto-registered!
============================================================
📋 Your API key: far_live_abc123...
📊 Free tier: 500 queries/month
📖 Upgrade: https://rapidapi.com/yschang/api/far-rag-...
💾 Save your key: export FAR_API_KEY=far_live_abc123...
============================================================
```

### With RapidAPI Key (Higher Limits)

For production use with higher rate limits, get an API key from [RapidAPI](https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search).

```python
from far_search import FARSearchTool

tool = FARSearchTool(rapidapi_key="your-rapidapi-key")

result = tool.invoke({
    "query": "cybersecurity requirements for contractors"
})
```

### Use with LangChain Agents

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from far_search import FARSearchTool

# Initialize LLM and tool
llm = ChatOpenAI(model="gpt-4")
tools = [FARSearchTool()]

# Create agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Ask about regulations
response = agent.run(
    "What are the FAR requirements for small business subcontracting plans?"
)
print(response)
```

### Use with LangGraph

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from far_search import FARSearchTool

# Create agent with FAR search capability
agent = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    tools=[FARSearchTool()]
)

# Query the agent
result = agent.invoke({
    "messages": [("user", "What cybersecurity clauses should I include in a DoD contract?")]
})
```

## Pricing & Plans

| Plan | Price | Queries/Month | Best For |
|------|-------|---------------|----------|
| **Free** | $0 | 500 | Testing & Prototyping |
| **Pro** | $29/mo | 5,000 | Startups & Live Apps |
| **Ultra** | $199/mo | 150,000 | Enterprise & Agencies |

**Your first run auto-registers you on the free tier.** No sign-up needed!

When you approach your monthly limit (50%, 80%, 100%), you'll see usage warnings with a link to [upgrade on RapidAPI](https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search).

## For Government Contractors

FAR Search Tool helps government contractors verify compliance requirements before proposal submission.

**Problem**: LLMs hallucinate FAR citations. A wrong citation in a $5M proposal costs $500K+.

**Solution**: FAR Search Tool provides ground-truth, official FAR clauses with acquisition.gov citations.

**Use Cases**:
- Verify compliance requirements before proposal submission
- Auto-generate accurate FAR clause references
- Audit AI-generated contract language
- Train compliance teams on regulatory changes

**Compliance Benefits**:
- Supports DFARS audit trails (via [Agent Observability](https://github.com/blueskylineassets/agent-observability))
- SOC 2 compliant data handling
- 100% legal FAR data (public domain)

[Read the Government Contractor Guide](./docs/govcon-guide.md)

## Features

- **Semantic Search**: Find relevant regulations using natural language queries
- **Pre-vectorized Data**: 617 FAR clauses with pre-computed embeddings for fast search
- **LLM-Optimized Output**: Results formatted for easy consumption by language models
- **Retry Logic**: Built-in handling for transient failures
- **Auto-Registration**: Just instantiate and use - no signup required
- **Usage Warnings**: Get notified at 50%, 80%, 100% of your monthly quota

## API Reference

### FARSearchTool

```python
FARSearchTool(
    rapidapi_key: str = None,      # Optional RapidAPI key for paid tier
    base_url: str = None,          # Override API URL (for self-hosted)
    timeout: int = 30,             # Request timeout in seconds
    max_retries: int = 2           # Retry attempts on failure
)
```

### Input Schema

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | required | Natural language search query |
| `top_k` | int | 5 | Number of results (1-20) |

### Output

Returns a formatted string containing matching FAR clauses with:
- Clause ID and title
- Relevance score
- Source reference
- URL to official documentation
- Clause text (truncated if long)

## Example Queries

- "Small business set aside requirements"
- "Cybersecurity contract clauses"
- "Payment terms for government contracts"
- "Contractor ethics and conduct rules"
- "Cost accounting standards"
- "Intellectual property rights in contracts"
- "Subcontracting plan requirements"
- "Contract termination procedures"


## Error Handling

```python
from far_search import FARSearchTool, FARAPIError, FARRateLimitError

tool = FARSearchTool()

try:
    result = tool.invoke({"query": "my query"})
except FARRateLimitError:
    print("Rate limit exceeded. Upgrade your plan or wait.")
except FARAPIError as e:
    print(f"API error: {e}")
```

## Compliance & Audit Logging

For government contractors and regulated industries, maintain audit trails of all FAR searches using [Agent Observability](https://pypi.org/project/agent-observability/):

```python
from far_search import FARSearchTool
from agent_observability import AgentLogger

# Initialize - auto-registers on first use, no API key needed!
far_tool = FARSearchTool()
logger = AgentLogger()

# Search and log for compliance
query = "cybersecurity requirements FAR 52.204"
results = far_tool.invoke({"query": query})

# Log the search for audit trail
logger.log("far_search", {
    "query": query,
    "results_count": len(results) if isinstance(results, list) else 1,
    "contract": "GS-00F-0001X",
    "purpose": "compliance_check"
})

# First log auto-registers and shows:
# ✅ Agent Observability - Auto-registered!
# 📋 Your API key: ao_live_abc123...
```

**Why log FAR searches?**

- **DFARS Compliance**: Government contracts often require audit trails
- **Cost Tracking**: Know how much time is spent on regulatory research
- **Team Analytics**: See what your team searches most frequently
- **SOC 2 / ISO 27001**: Demonstrate due diligence in compliance

**Setup (30 seconds):**

```bash
pip install agent-observability
```

That's it! No API key needed - auto-registers on first use. **Free tier: 100K logs/month.**

Learn more: [Agent Observability](https://pypi.org/project/agent-observability/)

## Requirements

- Python 3.9+
- langchain >= 0.1.0
- requests >= 2.28.0
- pydantic >= 2.0.0

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [API Documentation](https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search)
- [GitHub Repository](https://github.com/blueskylineassets/far-search-tool)
- [FAR Official Website](https://www.acquisition.gov/browse/index/far)

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

