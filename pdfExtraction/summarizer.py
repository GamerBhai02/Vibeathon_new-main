import requests
import json
import os
import sys

# Use GEMINI_API_KEY for direct Gemini API calls
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def summarize_content(document_title: str, full_document_content: str) -> str:
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not found in environment variables.", file=sys.stderr)
        # Return a default JSON structure if API key is missing
        return json.dumps([{"topic": "Error: API Key Missing", "content": "Please set GEMINI_API_KEY environment variable."}])

    prompt = (
        f"The following is a document titled '{document_title}'. "
        "Please read the entire document and identify 10 to 15 of the most important topics discussed. "
        "For each topic, provide a concise summary. "
        "Return your response as a JSON array of objects, where each object has two keys: "
        "'topic' (for the topic name) and 'content' (for its summary). "
        "Ensure the output is valid JSON and contains only the array.\n\n"
        "Document Content:\n" + full_document_content
    )

    # Google Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status() # Raise an exception for HTTP errors
        result = response.json()
        # The Gemini API response structure is different
        # It returns a 'text' field within 'parts' of 'candidates'
        # Handle case where response might not have the expected structure
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                return candidate["content"]["parts"][0]["text"]
            else:
                # If content structure is different, try to get text directly
                if "content" in candidate and isinstance(candidate["content"], str):
                    return candidate["content"]
                else:
                    raise KeyError("Unexpected response structure")
        else:
            raise KeyError("No candidates in response")
    except requests.exceptions.RequestException as e:
        print(f"Error calling Google Gemini API: {e}", file=sys.stderr)
        return json.dumps([{"topic": "Error: API Call Failed", "content": str(e)}])
    except KeyError as e:
        print(f"Error parsing Google Gemini API response: {e}", file=sys.stderr)
        return json.dumps([{"topic": "Error: Invalid API Response", "content": str(e)}])