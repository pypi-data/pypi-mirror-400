# FAR Search AutoGPT Plugin

[![PyPI version](https://badge.fury.io/py/far-search-autogpt.svg)](https://pypi.org/project/far-search-autogpt/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AutoGPT plugin** for searching Federal Acquisition Regulations (FAR).

Enable your AutoGPT agent to search government contracting regulations, verify compliance requirements, and cite accurate FAR clauses.

## Installation

```bash
pip install far-search-autogpt
```

## Setup

### Option 1: Auto-Registration (Recommended)

Just install and use - the plugin auto-registers on first search:

```bash
pip install far-search-autogpt
# Add to your AutoGPT plugins
# First search will auto-register and display your API key
```

### Option 2: With API Key

```bash
# Get an API key
curl -X POST https://far-rag-api-production.up.railway.app/v1/register \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-autogpt-agent"}'

# Set environment variable
export FAR_API_KEY=far_live_...

# Install and use
pip install far-search-autogpt
```

## Usage

The plugin provides these commands to your AutoGPT agent:

### Search FAR

```python
plugin = FARSearchPlugin()

# Search for relevant regulations
result = plugin.search_far("cybersecurity requirements for DoD contracts")
print(result)
```

### Get Specific Clause

```python
# Get a specific clause by ID
result = plugin.get_far_clause("52.204-2")
print(result)
```

## AutoGPT Integration

Add to your AutoGPT configuration:

```yaml
# .env or config
ALLOWLISTED_PLUGINS=far-search-autogpt
```

Then your agent can use commands like:
- "Search FAR for small business requirements"
- "Get FAR clause 52.203-1"
- "Verify compliance requirements for cybersecurity"

## Use Cases

- **Proposal Writing**: Find relevant FAR clauses for government proposals
- **Compliance Verification**: Verify AI-generated FAR citations
- **Contract Analysis**: Research regulatory requirements
- **Training**: Learn about federal acquisition rules

## Pricing

| Plan | Price | Queries/Month |
|------|-------|---------------|
| **Free** | $0 | 500 |
| **Pro** | $29/mo | 5,000 |
| **Ultra** | $199/mo | 150,000 |

Auto-registers on first use. Upgrade at [RapidAPI](https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search).

## Related Packages

| Package | Use Case |
|---------|----------|
| **far-search** | Lightweight core SDK |
| **far-search-tool** | LangChain tool |
| **far-search-autogpt** (this) | AutoGPT plugin |
| **far-search-crewai** | CrewAI multi-agent tool |
| **far-oracle** | MCP Server for Claude Desktop |

## License

MIT License - see [LICENSE](LICENSE) for details.

