"""Agent for evaluating user submissions and providing feedback"""

from ..services.anthropic import call_anthropic_api
import json
from typing import List

class EvaluatorAgent:
    """Grades student answers and provides constructive feedback."""

    async def grade_submission(self, questions: List[dict], answers: List[dict]) -> dict:
        """Grades a set of answers against the original questions."""

        system_prompt = """
        You are an AI evaluator. Your task is to grade a student's submission for a test. You will be given the original questions and the student's answers. You need to assess each answer, calculate a total score, and provide feedback.

        The output must be a valid JSON object with the following structure:
        - "score": The total score achieved by the student.
        - "topicBreakdown": A dictionary where keys are topics and values are the scores for that topic.
        - "answers": A list of objects, each corresponding to an answer. Each object should have:
            - "question": The original question text.
            - "submitted_answer": The answer submitted by the student.
            - "is_correct": A boolean indicating if the answer is correct.
            - "feedback": Constructive feedback on the answer, explaining why it is right or wrong.
            - "marks_awarded": The marks awarded for the answer.

        For multiple-choice questions, the answer is either right or wrong. For short-answer questions, you may need to assess the content and award partial marks if appropriate.
        """
        
        user_prompt = f"""
        Questions:
        {json.dumps(questions)}

        Student's Answers:
        {json.dumps(answers)}
        """

        response = await call_anthropic_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=3000,
        )

        return json.loads(response)
