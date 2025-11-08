"""YouTube Search Service"""

import os
import httpx
from typing import List, Dict, Any

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

async def search_youtube(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Searches YouTube for videos related to a query."""
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY environment variable not set.")

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()

    data = response.json()

    results = [
        {
            "title": item["snippet"]["title"],
            "videoId": item["id"]["videoId"],
            "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
        }
        for item in data.get("items", [])
    ]

    return results
