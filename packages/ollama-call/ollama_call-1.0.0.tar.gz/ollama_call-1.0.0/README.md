# ollama-call

A simple Python wrapper for Ollama API calls.

## Installation

```bash
pip install ollama-call
```

## Usage

```python
from ollama_call import ollama_call

response = ollama_call(
    user_prompt="Hello, how are you?",
    format="json",
    model="gemma3:12b"
)

print(response)
```

## Features

- Simple function-based API
- Supports JSON output format
- Supports streaming (via `stream=True`)
- Custom temperature and timeout settings
