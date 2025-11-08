"""Judge0 code execution service"""
import httpx
import os
from typing import Optional


JUDGE0_API_URL = "https://judge0-ce.p.rapidapi.com"


async def execute_code_judge0(
    language: str,
    code: str,
    stdin: Optional[str] = None,
) -> dict:
    """Execute code using Judge0 API"""
    
    api_key = os.getenv("JUDGE0_API_KEY")
    
    if not api_key:
        # Mock execution for development
        return {
            "stdout": "Mock output: Code executed successfully",
            "stderr": "",
            "status": "Accepted",
            "time": "0.001",
            "memory": "1024",
        }
    
    # Language ID mapping
    language_ids = {
        "python": 71,
        "javascript": 63,
        "java": 62,
        "cpp": 54,
        "c": 50,
    }
    
    language_id = language_ids.get(language.lower(), 71)
    
    # Submit code
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "Content-Type": "application/json",
    }
    
    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin or "",
    }
    
    async with httpx.AsyncClient() as client:
        # Submit
        response = await client.post(
            f"{JUDGE0_API_URL}/submissions",
            json=payload,
            headers=headers,
            params={"base64_encoded": "false"},
        )
        
        if response.status_code != 201:
            return {"error": "Submission failed", "status": "Error"}
        
        token = response.json()["token"]
        
        # Get result
        result_response = await client.get(
            f"{JUDGE0_API_URL}/submissions/{token}",
            headers=headers,
            params={"base64_encoded": "false"},
        )
        
        result = result_response.json()
        
        return {
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "status": result.get("status", {}).get("description", "Unknown"),
            "time": result.get("time", "0"),
            "memory": result.get("memory", "0"),
        }
