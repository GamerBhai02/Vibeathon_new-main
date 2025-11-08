"""Claude API connector"""
import os
import httpx

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

async def call_anthropic_api(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    model: str = "claude-3-haiku-20240307",
) -> str:
    """Calls the Anthropic API with a system prompt and user prompt."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data, timeout=90.0)

    response.raise_for_status() 
    response_json = response.json()
    return response_json["content"][0]["text"]
