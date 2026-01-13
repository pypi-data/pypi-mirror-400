import requests
import logging
import json
from typing import Dict, Any, Union

def ollama_call(
    user_prompt: str,
    format: Union[str, Dict[str, Any]],
    verbose: bool = False,
    stream: bool = False,
    temperature: float = 0.8,
    model: str ="gemma3:12b",
    timeout: int = 180
) -> Any:
    LLM_PROMPT = user_prompt
    if verbose:
        print(f"OLLAMA_CALL -> Current System Prompt: {LLM_PROMPT}")

    OLLAMA_URL = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": user_prompt,
        "stream": stream,
        "options": {
            "temperature": temperature,
        },
        "format": format
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        stream=stream,
        timeout=timeout
    )
    response.raise_for_status()
    response_data = response.json()
    final_response = response_data.get("response", "")

    if verbose:
        print(f"OLLAMA_CALL -> Response Received: {final_response}")

    return response_data
