"""SM-2 Spaced Repetition Algorithm"""

from datetime import datetime, timedelta
from sqlmodel import Session
from ..models import Flashcard

def update_flashcard_sm2(session: Session, flashcard_id: int, quality: int, user_id: str):
    """Updates a flashcard's review data using the SM-2 algorithm."""
    if not (0 <= quality <= 5):
        raise ValueError("Quality must be between 0 and 5.")

    flashcard = session.get(Flashcard, flashcard_id)
    if not flashcard or flashcard.userId != user_id:
        raise ValueError("Flashcard not found")

    if quality < 3:
        # Incorrect response, reset repetition number
        flashcard.repetition = 0
        flashcard.interval = 1
    else:
        # Correct response, update SM-2 parameters
        if flashcard.repetition == 0:
            flashcard.interval = 1
        elif flashcard.repetition == 1:
            flashcard.interval = 6
        else:
            flashcard.interval = round(flashcard.interval * flashcard.easinessFactor)

        flashcard.repetition += 1

        # Update easiness factor
        easiness_factor = flashcard.easinessFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if easiness_factor < 1.3:
            easiness_factor = 1.3
        flashcard.easinessFactor = easiness_factor

    # Set next review date
    flashcard.nextReviewDate = datetime.utcnow().date() + timedelta(days=flashcard.interval)

    session.add(flashcard)
    session.commit()
    session.refresh(flashcard)

    return flashcard
