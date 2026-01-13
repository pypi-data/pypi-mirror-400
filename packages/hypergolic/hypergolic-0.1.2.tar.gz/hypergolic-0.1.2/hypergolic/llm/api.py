import os
from pathlib import Path
import requests

from .schemas import APIResponse, Message
from ..tools.tool_list import ALL_TOOLS_FORMATTED

BASE_API_URL = os.environ.get("HYPERGOLIC_API_URL", "https://api.anthropic.com")
HYPERGOLIC_API_KEY = os.environ.get("HYPERGOLIC_API_KEY")
MAX_TOKENS = 8192


def load_system_prompt() -> str:
    """Load the system prompt from the prompts directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"
    try:
        return prompt_path.read_text().strip()
    except FileNotFoundError:
        # Fallback to a minimal system prompt if file not found
        return "You are a helpful AI coding assistant with access to command-line tools."


def call_messages_api(messages: list[Message]) -> APIResponse:
    if not HYPERGOLIC_API_KEY:
        raise Exception("HYPERGOLIC_API_KEY not set")
    elif not BASE_API_URL:
        raise Exception("HYPERGOLIC_API_URL not set")

    url = f"{BASE_API_URL}/v1/messages"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": HYPERGOLIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }
    
    # Prepare tools with cache control on the last tool
    tools = ALL_TOOLS_FORMATTED.copy()
    if tools:
        # Mark the last tool for caching
        tools[-1] = {**tools[-1], "cache_control": {"type": "ephemeral"}}
    
    # Load system prompt
    system_prompt = load_system_prompt()
    
    data = {
        "model": "claude-sonnet-4-5",
        "max_tokens": MAX_TOKENS,
        "messages": [m.model_dump(exclude_none=True) for m in messages],
        "tools": tools,
        "system": system_prompt,
    }
    
    response = requests.post(url, headers=headers, json=data)
    return APIResponse(**response.json())
