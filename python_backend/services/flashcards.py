"""Flashcard generation service"""
from typing import List
from sqlmodel import Session
from datetime import datetime, timedelta
from ..models import Flashcard


async def generate_flashcards_from_source(
    source_type: str,
    source_id: str,
    count: int,
    user_id: str,
    session: Session,
) -> List[Flashcard]:
    """Generate flashcards from lesson or topic"""
    
    # In production: use LLM to generate flashcards from content
    # For now: create mock flashcards
    
    flashcards = []
    next_review = datetime.utcnow() + timedelta(days=1)
    
    for i in range(count):
        flashcard = Flashcard(
            userId=user_id,
            topicId=source_id,
            front=f"Question {i+1} about {source_type}",
            back=f"Answer {i+1} with explanation",
            nextReviewAt=next_review.isoformat(),
            easinessFactor=2.5,
            interval=1,
            repetitions=0,
        )
        session.add(flashcard)
        flashcards.append(flashcard)
    
    session.commit()
    return flashcards
