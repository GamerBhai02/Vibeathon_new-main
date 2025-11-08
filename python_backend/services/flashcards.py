"""Service for generating flashcards from various sources."""

from sqlmodel import Session
from ..models import Topic, Flashcard
from .anthropic import call_anthropic_api
import json

async def generate_flashcards_from_source(
    source_type: str,
    source_id: str,
    count: int,
    user_id: str,
    session: Session,
) -> list:
    """Generates flashcards from a topic, lesson, or other source."""
    
    content = ""
    if source_type == "topic":
        topic = session.get(Topic, source_id)
        if not topic or topic.userId != user_id:
            raise ValueError("Topic not found")
        content = topic.summary
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    system_prompt = """
    You are a flashcard generation AI. Your task is to create a set of flashcards based on the provided text. Each flashcard should have a clear question on the front and a concise answer on the back.

    The output must be a valid JSON list of objects, where each object represents a flashcard and has the following structure:
    - "front": The question or term.
    - "back": The answer or definition.
    """

    user_prompt = f"""
    Content to turn into flashcards:
    ---
    {content}
    ---
    Number of flashcards to generate: {count}
    """

    response = await call_anthropic_api(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=1000,
    )

    flashcard_data = json.loads(response)

    saved_flashcards = []
    for fc_data in flashcard_data:
        flashcard = Flashcard(
            userId=user_id,
            topicId=source_id if source_type == "topic" else None,
            front=fc_data["front"],
            back=fc_data["back"],
        )
        session.add(flashcard)
        saved_flashcards.append(flashcard)
    
    session.commit()
    for fc in saved_flashcards:
        session.refresh(fc)

    return saved_flashcards
