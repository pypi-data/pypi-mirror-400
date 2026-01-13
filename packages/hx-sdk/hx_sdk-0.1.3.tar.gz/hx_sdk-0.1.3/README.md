# HX SDK

Python SDK for HexelStudio.

## Installation

```bash
pip install hx-sdk
```

## Configuration

Just set your API key — org, workspace, and environment are automatically extracted from the token:

```bash
export HX_API_KEY="your-api-key"
```

Optionally override the base URL:
```bash
export HX_BASE_URL="https://api.hexelstudio.com"  # default
```

## Usage

```python
from hx import Client

client = Client()

# Knowledge search
results = client.knowledge.search("ks_support", "refund policy")

# Memory operations
client.memory.add(
    "ms_support",
    messages=[
        {"role": "user", "content": "I prefer email"},
        {"role": "assistant", "content": "Noted!"}
    ],
    user_id="user_123"
)

memories = client.memory.search("ms_support", "preferences", user_id="user_123")

# Access tenant info from token (if needed)
print(client.org_id)
print(client.workspace_id)
print(client.environment_id)
```

## Documentation

See [docs.hexelstudio.com](https://docs.hexelstudio.com/sdk/python) for full API reference.
