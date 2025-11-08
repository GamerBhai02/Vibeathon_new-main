"""Agent for generating lessons and explanations"""

import os
import json
import re
import google.generativeai as genai
from ..rag import RAGSystem

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class TeacherAgent:
    """Generates micro-lessons and explanations with RAG integration."""

    async def generate_lesson(self, topic_name: str, user_id: str) -> dict:
        """Creates a concise, engaging micro-lesson on a specific topic."""

        rag = RAGSystem(user_id)
        retrieved_docs = await rag.query(f"Content related to {topic_name}")

        if not GEMINI_API_KEY:
            # Return a mock lesson if no API key
            return {
                "title": f"Introduction to {topic_name}",
                "key_concepts": ["Concept 1", "Concept 2"],
                "explanation": "This is a mock lesson.",
                "example": "This is a mock example.",
                "summary": "This is a mock summary."
            }

        prompt = f"""
        You are an expert teacher AI. Your goal is to create a high-quality, engaging micro-lesson on a specific topic. The lesson should be clear, concise, and easy to understand for a student who is learning this for the first time.

        Structure the lesson as a JSON object with the following keys:
        - "title": The title of the lesson (e.g., "Introduction to Photosynthesis").
        - "key_concepts": A list of the most important concepts or terms covered in the lesson.
        - "explanation": A detailed but clear explanation of the topic. Use analogies and simple examples where possible.
        - "example": A practical example or a worked-through problem to illustrate the concept.
        - "summary": A brief summary of the main points of the lesson.

        Use the provided context from the user's documents to make the lesson more relevant.
        
        Topic: {topic_name}
        Context from user's documents:
        --- 
        {retrieved_docs}
        ---
        
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
