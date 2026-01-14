# VerifAI SDK

[![PyPI version](https://badge.fury.io/py/verifai-sdk.svg)](https://pypi.org/project/verifai-sdk/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**VerifAI SDK** provides automatic tracing and evaluation for your AI/LLM applications. With one line of code, capture all LLM calls and send them to the VerifAI platform for analysis.

## Installation

```bash
pip install verifai-sdk
```

## Quick Start

```python
import verifai
from openai import OpenAI

# 1. Initialize (one line!)
verifai.auto_instrument(
    project_name="my_project",
    capture_content=True
)

# 2. Use your AI libraries as usual
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Traces are automatically sent to VerifAI! ✨
```

## Configuration

Set your API key as an environment variable:

```bash
export VERIFAI_API_KEY="your_api_key_here"
export VERIFAI_API_URL="http://localhost:8000"  # Optional
```

## Supported Frameworks

- ✅ OpenAI
- ✅ Anthropic
- ✅ LangChain
- ✅ LlamaIndex
- ✅ Custom agents (via `@verifai.trace` decorator)

## Manual Tracing

For custom agent logic:

```python
@verifai.trace
def my_agent(query: str):
    # Your agent logic here
    return result
```

## License

Apache 2.0
