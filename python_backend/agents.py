"""This file contains the AI agents that power the application."""

import os
import re
import json
from sqlmodel import Session, select
import google.generativeai as genai
from .rag import RAGSystem
from .models import Flashcard, Topic

# --- Configuration ---
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    MODEL_NAME = "gemini-1.5-flash"
except KeyError:
    print("Warning: GEMINI_API_KEY not found. Using mock LLM.")
    MODEL_NAME = "mock"
except Exception as e:
    print(f"An error occurred during Gemini configuration: {e}")
    MODEL_NAME = "mock"


# --- Mock LLM ---
class MockLLM:
    """A mock LLM for testing purposes."""
    async def generate_content(self, contents):
        print(f"--- MOCK LLM INPUT ---\n{contents}\n--- END MOCK LLM INPUT ---")
        # Simulate a delay
        import asyncio
        await asyncio.sleep(1)
        
        if "GENERATE QUIZ" in contents:
            return '[{"question_text": "What is 2+2?", "answer": "4"}, {"question_text": "Capital of France?", "answer": "Paris"}]'
        elif "GENERATE FLASHCARDS" in contents:
            return '[{"front": "Hello", "back": "World"}, {"front": "Key", "back": "Value"}]'
        elif "GENERATE TOPIC" in contents:
            return '{"name": "Mock Topic", "summary": "This is a mock summary.", "subtopics": ["sub1", "sub2"]}'
        elif "EVALUATE SUBMISSION" in contents:
            return '{"feedback": "Mock feedback", "score": 85}'
        return "This is a mock response."

# --- Gemini LLM ---
class GeminiLLM:
    """Interface for the Gemini large language model."""
    def __init__(self, model_name: str = MODEL_NAME):
        """Initializes the Gemini LLM."""
        self.model = genai.GenerativeModel(model_name)

    async def generate_content(self, contents: str) -> str:
        """Generates content using the Gemini model."""
        print(f"--- GEMINI PROMPT ---\n{contents}\n--- END GEMINI PROMPT ---")
        response = await self.model.generate_content_async(contents)
        return response.text

# --- LLM Factory ---
def get_llm():
    """Returns the appropriate LLM based on the configuration."""
    if MODEL_NAME == "mock":
        return MockLLM()
    return GeminiLLM()

# --- Prompt Templates ---
topic_prompt = """
You are an expert educational AI assistant. Based on the user's prompt and the retrieved context, generate a learning topic.

User Prompt: {user_prompt}

Retrieved Context:
{retrieved_context}

Generate a JSON object with the following structure:
{{
  "name": "Topic Name",
  "summary": "A concise summary of the topic (2-3 sentences)",
  "subtopics": ["subtopic1", "subtopic2", "subtopic3"]
}}

Respond with ONLY the JSON object, no additional text.
"""

flashcard_prompt = """
You are an expert flashcard creator. Generate {number_of_flashcards} flashcards from the following content:

{source_text}

Create flashcards that test key concepts, definitions, and important facts.
Generate a JSON array of flashcard objects with the following structure:
[
  {{"front": "Question or prompt", "back": "Answer or explanation"}},
  {{"front": "Question or prompt", "back": "Answer or explanation"}}
]

Respond with ONLY the JSON array, no additional text.
"""

quiz_prompt = """
You are an expert quiz creator. Generate a quiz with the following specifications:

Topic Summary: {topic_summary}
Difficulty: {difficulty}
Quiz Type: {quiz_type}
Number of Questions: {num_questions}

Generate a JSON array of question objects with the following structure:
[
  {{"question_text": "Question text here", "answer": "Correct answer"}},
  {{"question_text": "Question text here", "answer": "Correct answer"}}
]

For multiple choice questions, include the correct answer in the "answer" field.
Respond with ONLY the JSON array, no additional text.
"""

evaluator_prompt = """
You are an expert evaluator. Grade the following quiz submission and provide detailed feedback:

{submission_details}

Generate a JSON object with the following structure:
{{
  "feedback": "Detailed feedback on the answers",
  "score": 85
}}

The score should be out of 100. Provide constructive feedback.
Respond with ONLY the JSON object, no additional text.
"""

# --- Helper for parsing LLM output ---
def parse_llm_output(text: str) -> list | dict:
    """Parses the LLM's JSON output, cleaning it if necessary."""
    try:
        # First, try to parse the text directly
        return json.loads(text)
    except json.JSONDecodeError:
        # If it fails, try to find the JSON block within the text
        match = re.search(r"```json
(.*)
```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse cleaned JSON: {e}")
        else:
            raise ValueError("No valid JSON found in the LLM output.")


# --- AGENT CLASSES ---

class TopicGenerator:
    """Agent for generating new learning topics."""
    def __init__(self):
        self.llm = get_llm()

    async def generate_topic(self, prompt: str, user_id: int) -> dict:
        """Generates a topic, summary, and subtopics."""
        rag_system = RAGSystem(str(user_id))
        context = await rag_system.query(prompt, n_results=3)
        
        formatted_prompt = topic_prompt.format(
            user_prompt=prompt, retrieved_context=context
        )
        
        response = await self.llm.generate_content(formatted_prompt)
        return parse_llm_output(response)

class FlashcardAgent:
    """Agent for generating flashcards."""
    def __init__(self):
        self.llm = get_llm()

    async def generate_flashcards(
        self, source_type: str, source_id: str, count: int, user_id: int, db_session: Session
    ) -> list[Flashcard]:
        """Generates flashcards from a source (e.g., a Topic)."""
        if source_type == "topic":
            topic = db_session.get(Topic, int(source_id))
            if not topic:
                raise ValueError("Topic not found")
            source_text = topic.summary
        else:
            # Placeholder for other source types like documents or YouTube videos
            raise NotImplementedError(f"Source type '{source_type}' not supported.")
            
        formatted_prompt = flashcard_prompt.format(
            source_text=source_text, number_of_flashcards=count
        )
        response = await self.llm.generate_content(formatted_prompt)
        flashcard_data = parse_llm_output(response)

        flashcards = []
        for data in flashcard_data:
            flashcard = Flashcard(
                front=data["front"],
                back=data["back"],
                topicId=int(source_id),
                userId=user_id,
            )
            db_session.add(flashcard)
            flashcards.append(flashcard)
        
        db_session.commit()
        for fc in flashcards:
            db_session.refresh(fc)
            
        return flashcards

class QuizGen:
    """Agent for generating quizzes."""
    def __init__(self):
        self.llm = get_llm()

    async def generate_quiz(
        self, topic_summary: str, difficulty: str, quiz_type: str, num_questions: int
    ) -> list[dict]:
        """Generates a quiz based on a topic."""
        formatted_prompt = quiz_prompt.format(
            topic_summary=topic_summary,
            difficulty=difficulty,
            quiz_type=quiz_type,
            num_questions=num_questions,
        )
        response = await self.llm.generate_content(formatted_prompt)
        return parse_llm_output(response)

class EvaluatorAgent:
    """Agent for evaluating quiz submissions."""
    def __init__(self):
        self.llm = get_llm()

    async def grade_submission(self, questions: list, answers: list) -> dict:
        """Grades a user's quiz submission."""
        submission_str = ""
        for q, a in zip(questions, answers):
            submission_str += f"Question: {q.question_text}\nUser Answer: {a['answer']}\n\n"
            
        formatted_prompt = evaluator_prompt.format(submission_details=submission_str)
        response = await self.llm.generate_content(formatted_prompt)
        return parse_llm_output(response)