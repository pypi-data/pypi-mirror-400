# MotionOS Python SDK

> **Enterprise-grade SDK for AI memory and context management**

[![PyPI version](https://badge.fury.io/py/motionos.svg)](https://pypi.org/project/motionos/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

## Features

- 🧠 **Memory Ingestion** - Store decisions, preferences, facts, and events
- 🔍 **Intent-Based Retrieval** - Query with purpose: explore, recall, decide, inject
- 📊 **Explainability** - Understand why specific memories were retrieved
- ⏰ **Timeline Operations** - Walk causality chains, check validity, rollback
- 🔒 **Enterprise Security** - Role-based access, key validation
- 🧪 **Simulation Mode** - Full offline testing with deterministic mocks
- ⚡ **Async Support** - Both sync and async clients available

## Installation

```bash
pip install motionos
# or
poetry add motionos
```

## Quick Start

```python
from motionos import MotionOS

# Initialize client
client = MotionOS(
    api_key=os.environ["MOTIONOS_API_KEY"],
    project_id=os.environ["MOTIONOS_PROJECT_ID"],
)

# Ingest a memory
result = client.ingest(
    raw_text="User prefers dark mode with reduced motion",
    memory_type="preference",
    metadata={"category": "ui", "source": "settings"},
)

# Retrieve with intent
memories = client.retrieve(
    query="What are the user preferences for UI?",
    intent="recall",
    limit=5,
)

print(memories["context"])
```

## Async Usage

```python
from motionos import AsyncMotionOS

async def main():
    client = AsyncMotionOS(
        api_key=os.environ["MOTIONOS_API_KEY"],
        project_id=os.environ["MOTIONOS_PROJECT_ID"],
    )
    
    result = await client.ingest("User completed onboarding")
    memories = await client.retrieve("What did the user complete?")
```

## Core Concepts

### Memory Types

| Type | Description | Use Case |
|------|-------------|----------|
| `decision` | User choices and selections | Subscription upgrades, feature toggles |
| `preference` | User preferences and settings | Dark mode, notification preferences |
| `fact` | Factual information | Account creation dates, user profiles |
| `event` | Actions and occurrences | Completed onboarding, purchases |

### Retrieval Intents

```python
# Exploration - broad context building
client.retrieve(query="...", intent="explore")

# Recall - specific memory retrieval
client.retrieve(query="...", intent="recall")

# Decision - context for making choices
client.retrieve(query="...", intent="decide")

# Inject - context for AI prompts
client.retrieve(query="...", intent="inject")
```

## Advanced Usage

### Fluent Retrieval Builder

```python
from motionos.retrieval import RetrievalBuilder

result = (
    RetrievalBuilder()
    .query("What decisions has the user made?")
    .with_intent("recall")
    .limit_to(10)
    .include_explanation()
    .for_domain("user-context")
    .execute(client)
)
```

### Timeline Operations

```python
from motionos.timeline import TimelineClient

timeline = TimelineClient(client)

# Walk causality chain
walk = timeline.walk(version_id, depth=5)

# Check if memory is still valid
validity = timeline.check_validity(version_id)

# Rollback to previous version
timeline.rollback(version_id)
```

### Simulation Mode

```python
from motionos.simulation import MockMotionOS, Scenarios

# Create mock client for testing
client = MockMotionOS.create(Scenarios.happy_path())

# Works completely offline
client.ingest("test data")
client.retrieve("query")

# Test error scenarios
flaky_client = MockMotionOS.create(Scenarios.unstable(0.25))
```

### Error Handling

```python
from motionos.errors import (
    MotionOSError,
    RateLimitError,
    ValidationError,
)

try:
    client.ingest(data)
except RateLimitError as e:
    time.sleep(e.retry_after_ms / 1000)
    # Retry...
except ValidationError as e:
    print(f"Invalid: {e}")
```

### Retry with Backoff

```python
from motionos.retry import with_retry_sync, RetryStrategies

result = with_retry_sync(
    lambda: client.retrieve(query),
    options=RetryStrategies.aggressive().options,
)
```

## Security

### API Key Types

| Key Type | Prefix | Use Case |
|----------|--------|----------|
| Secret | `sb_secret_` | Server-side, full access |
| Publishable | `sb_publishable_` | Read-only access |

### Environment Variables

```bash
export MOTIONOS_API_KEY="sb_secret_..."
export MOTIONOS_PROJECT_ID="your-project-id"
```

## Runtime Support

| Runtime | Status | Notes |
|---------|--------|-------|
| CPython 3.9+ | ✅ Full | All operations |
| AWS Lambda | ✅ Full | Serverless-optimized |
| Google Cloud Functions | ✅ Full | Serverless-optimized |
| Azure Functions | ✅ Full | Serverless-optimized |
| Jupyter | ✅ Full | Interactive support |

## API Reference

See the [full API documentation](./docs/API.md) for detailed reference.

## License

MIT License - see [LICENSE](./LICENSE).
