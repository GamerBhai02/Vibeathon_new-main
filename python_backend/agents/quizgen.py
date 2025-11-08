"""Agent for generating quizzes and mock exams"""

from ..services.anthropic import call_anthropic_api
from ..rag import RAGSystem
import json
from typing import List

class QuizGenAgent:
    """Generates practice questions, quizzes, and mock exams."""

    async def generate_questions(self, topic_name: str, difficulty: str, count: int, user_id: str) -> List[dict]:
        """Generates a list of practice questions on a given topic."""

        rag = RAGSystem(user_id)
        retrieved_docs = await rag.query(f"Content related to {topic_name} for a {difficulty} quiz")

        system_prompt = """
        You are a quiz generation AI. Your task is to create a set of practice questions on a given topic, at a specified difficulty level. The questions should be in a multiple-choice format.

        The output must be a valid JSON list of objects, where each object represents a question and has the following structure:
        - "question": The text of the question.
        - "options": A list of 4 strings representing the possible answers.
        - "correct_answer": The string that is the correct answer.
        - "explanation": A brief explanation of why the correct answer is right.

        Use the provided context from the user's documents to create relevant questions.
        """

        user_prompt = f"""
        Topic: {topic_name}
        Difficulty: {difficulty}
        Number of questions: {count}
        Context from user's documents:
        --- 
        {retrieved_docs}
        ---
        """

        response = await call_anthropic_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2000,
        )

        return json.loads(response)

    async def generate_mock_exam(self, exam_type: str, duration: int, total_marks: int, topics: List[str], user_id: str) -> dict:
        """Generates a comprehensive mock exam based on a set of topics."""
        
        rag = RAGSystem(user_id)
        context = ""
        for topic in topics:
            context += await rag.query(f"Content for a mock exam on {topic}") + "\n\n"

        system_prompt = """
        You are an expert exam creator. Your task is to generate a realistic mock exam based on a list of topics, duration, and total marks. The exam should have a mix of question types (e.g., multiple-choice, short answer) and cover the provided topics proportionally.

        The output must be a valid JSON object with the following structure:
        - "title": A suitable title for the mock exam.
        - "instructions": A list of instructions for the test-taker.
        - "questions": A list of question objects. Each question object should have:
            - "type": The type of question (e.g., "multiple-choice", "short-answer").
            - "question": The question text.
            - "options": A list of options (for multiple-choice questions).
            - "marks": The number of marks allocated to the question.
            - "topic": The topic the question relates to.

        Use the provided context from the user's documents to create relevant questions.
        """

        user_prompt = f"""
        Exam Type: {exam_type}
        Duration (minutes): {duration}
        Total Marks: {total_marks}
        Topics: {', '.join(topics)}
        Context from user's documents:
        ---
        {context}
        ---
        """

        response = await call_anthropic_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4000,
        )

        return json.loads(response)
