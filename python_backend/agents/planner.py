"""Agent for generating study plans"""
from ..services.anthropic import call_anthropic_api
import json

class PlannerAgent:
    """Generates personalized study plans."""

    async def generate_plan(self, topics: list, exam_type: str, exam_date: str, hours_per_day: int) -> dict:
        """Creates a structured study plan."""
        
        system_prompt = """
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
        """

        user_prompt = f"""
        Topics: {', '.join([t.name for t in topics])}
        Exam Type: {exam_type}
        Exam Date: {exam_date}
        Available study time: {hours_per_day} hours per day
        """

        response = await call_anthropic_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2000,
        )
        
        return json.loads(response)
