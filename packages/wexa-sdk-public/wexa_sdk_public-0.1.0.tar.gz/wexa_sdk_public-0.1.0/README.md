# wexa-sdk-public (Python)

Official Python SDK for the Wexa API - Public Version.

**This is the public SDK package that does NOT include authentication features (login/signup).**  
For internal use with authentication, use `wexa-sdk` instead.

## Installation

```bash
pip install wexa-sdk-public
```

## Quick Start

```python
from wexa_sdk import WexaClient

# Initialize with your API key
client = WexaClient(
    base_url="https://api.wexa.ai",
    api_key="your-api-key-here"
)

# Use the SDK
projects = client.projects.get_all()
```

## Authentication

**This package requires an API key.** You must obtain an API key from Wexa before using this SDK.

```python
client = WexaClient(
    base_url="https://api.wexa.ai",
    api_key="your-api-key"  # Required!
)
```

## Available Modules

| Module | Description |
|--------|-------------|
| `projects` | Project management |
| `agentflows` | Agent flow operations |
| `executions` | Execution management |
| `tables` | Table operations |
| `connectors` | Connector management |
| `schedules` | Schedule management |
| `llm` | LLM API calls |
| `files` | File operations |
| `inbox` | Inbox management |
| `knowledgebase` | Knowledge base operations |
| `tags` | Tag management |
| `skills` | Skills management |
| `marketplace` | Marketplace operations |
| `analytics` | Analytics operations |

## Note

- **No Authentication Module**: This package does NOT include `identity.auth.login()` or `identity.auth.signup()`
- **API Key Required**: You must provide an API key when initializing the client
- **For Internal Use**: If you need login/signup features, use `wexa-sdk` package instead

## Configuration

Environment variables:
- `WEXA_BASE_URL` (e.g. `https://api.wexa.ai`)
- `WEXA_API_KEY` (Your API key)

## License

Apache-2.0. See `LICENSE`.
