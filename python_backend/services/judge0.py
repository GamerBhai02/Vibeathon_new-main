"""Judge0 API connector for code execution"""

import os
import httpx

JUDGE0_API_URL = os.getenv("JUDGE0_API_URL", "https://judge0-ce.p.rapidapi.com")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY")
JUDGE0_API_HOST = os.getenv("JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")

# Language mapping from friendly names to Judge0 IDs
LANGUAGE_MAP = {
    "python": 71,
    "javascript": 63,
    "typescript": 74,
    "java": 62,
    "c++": 54,
    "go": 60,
}

async def execute_code_judge0(language: str, code: str, stdin: str = None) -> dict:
    """Executes code using the Judge0 API."""
    if not JUDGE0_API_KEY or not JUDGE0_API_HOST:
        raise ValueError("JUDGE0_API_KEY or JUDGE0_API_HOST not set.")

    language_id = LANGUAGE_MAP.get(language.lower())
    if not language_id:
        raise ValueError(f"Unsupported language: {language}")

    headers = {
        "X-RapidAPI-Key": JUDGE0_API_KEY,
        "X-RapidAPI-Host": JUDGE0_API_HOST,
        "Content-Type": "application/json",
    }

    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin,
    }

    async with httpx.AsyncClient() as client:
        # Submit code
        response = await client.post(
            f"{JUDGE0_API_URL}/submissions",
            headers=headers,
            json=payload,
            params={"base64_encoded": "false", "wait": "true"},
            timeout=30.0,
        )
        response.raise_for_status()
        result = response.json()

    # Decode stdout and stderr if they are base64 encoded
    if result.get("stdout") and isinstance(result["stdout"], str):
        try:
            import base64
            result["stdout"] = base64.b64decode(result["stdout"]).decode()
        except Exception:
            pass # Ignore if not valid base64
            
    if result.get("stderr") and isinstance(result["stderr"], str):
        try:
            import base64
            result["stderr"] = base64.b64decode(result["stderr"]).decode()
        except Exception:
            pass

    return result
