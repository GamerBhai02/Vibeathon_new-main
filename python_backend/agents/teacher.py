"""Agent for generating lessons and explanations"""

from ..services.anthropic import call_anthropic_api
from ..rag import RAGSystem
import json

class TeacherAgent:
    """Generates micro-lessons and explanations with RAG integration."""

    async def generate_lesson(self, topic_name: str, user_id: str) -> dict:
        """Creates a concise, engaging micro-lesson on a specific topic."""

        rag = RAGSystem(user_id)
        retrieved_docs = await rag.query(f"Content related to {topic_name}")

        system_prompt = """
        You are an expert teacher AI. Your goal is to create a high-quality, engaging micro-lesson on a specific topic. The lesson should be clear, concise, and easy to understand for a student who is learning this for the first time.

        Structure the lesson as a JSON object with the following keys:
        - "title": The title of the lesson (e.g., "Introduction to Photosynthesis").
        - "key_concepts": A list of the most important concepts or terms covered in the lesson.
        - "explanation": A detailed but clear explanation of the topic. Use analogies and simple examples where possible.
        - "example": A practical example or a worked-through problem to illustrate the concept.
        - "summary": A brief summary of the main points of the lesson.

        Use the provided context from the user's documents to make the lesson more relevant.
        """

        user_prompt = f"""
        Topic: {topic_name}
        Context from user's documents:
        --- 
        {retrieved_docs}
        ---        
        """

        response = await call_anthropic_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=1500,
        )

        return json.loads(response)
