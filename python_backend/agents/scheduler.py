"""Agent for scheduling study sessions"""
import os
import json
import google.generativeai as genai
from datetime import datetime, timedelta

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class SchedulerAgent:
    """Schedules study sessions and sends reminders."""

    async def create_schedule(self, topics: list, start_date: str, end_date: str, hours_per_day: int, preferences: dict = None) -> dict:
        """Creates a detailed study schedule with time blocks."""
        
        if not GEMINI_API_KEY:
            # Return a mock schedule if no API key
            return {
                "schedule": [],
                "totalHours": 0,
                "message": "Mock schedule created"
            }
        
        preferences_str = ""
        if preferences:
            preferences_str = f"\nUser Preferences: {json.dumps(preferences)}"
        
        prompt = f"""
        You are an expert study scheduler. Create a detailed study schedule with specific time blocks.

        Topics: {', '.join([t.name if hasattr(t, 'name') else str(t) for t in topics])}
        Start Date: {start_date}
        End Date: {end_date}
        Available hours per day: {hours_per_day}{preferences_str}

        Create a JSON object with the following structure:
        {{
          "schedule": [
            {{
              "date": "YYYY-MM-DD",
              "startTime": "HH:MM",
              "endTime": "HH:MM",
              "topic": "Topic name",
              "activity": "Study activity description",
              "duration_minutes": 120
            }}
          ],
          "totalHours": 40,
          "weeklyBreakdown": {{
            "week1": {{"hours": 10, "topics": ["topic1"]}},
            "week2": {{"hours": 10, "topics": ["topic2"]}}
          }}
        }}

        Distribute study sessions evenly, include breaks, and vary activities (reading, practice, review).
        Respond with ONLY the JSON object, no additional text or markdown formatting.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(prompt)
        
        # Clean the response to extract JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        return json.loads(response_text)
