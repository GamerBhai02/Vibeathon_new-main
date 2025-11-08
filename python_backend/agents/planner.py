"""Agent for generating study plans"""
import os
import json
import re
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class PlannerAgent:
    """Generates personalized study plans."""

    async def generate_plan(self, topics: list, exam_type: str, exam_date: str, hours_per_day: int) -> dict:
        """Creates a structured study plan."""
        
        if not GEMINI_API_KEY:
            # Return a mock plan if no API key
            return {
                "startDate": "2024-01-01",
                "endDate": exam_date,
                "weeklyGoal": "Complete study plan",
                "blocks": []
            }
        
        prompt = f"""
        You are an expert study planner. Your task is to create a detailed, personalized study plan based on a list of topics, an exam type, an exam date, and the user's available study time.

        The output must be a valid JSON object with the following structure:
        - "startDate": The recommended start date of the plan (e.g., "YYYY-MM-DD").
        - "endDate": The recommended end date of the plan (e.g., "YYYY-MM-DD").
        - "weeklyGoal": A concise, motivating goal for each week.
        - "blocks": A list of study blocks. Each block should be an object with:
            - "day": The day of the week (e.g., "Monday").
            - "date": The specific date for the study block (e.g., "YYYY-MM-DD").
            - "topic": The topic to be studied during this block.
            - "duration_hours": The duration of the study block in hours.
            - "activities": A list of suggested activities for the block (e.g., "Review notes", "Practice problems", "Watch a video lecture").

        Analyze the topics and create a logical sequence. Allocate more time to more complex topics if possible. Distribute the study sessions across the available days.
        
        Topics: {', '.join([t.name for t in topics])}
        Exam Type: {exam_type}
        Exam Date: {exam_date}
        Available study time: {hours_per_day} hours per day
        
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
