"""SM-2 Spaced Repetition Algorithm"""
from datetime import datetime, timedelta
from ..models import Flashcard


def update_flashcard_sm2(flashcard: Flashcard, quality: int) -> Flashcard:
    """
    Update flashcard using SM-2 algorithm
    
    Args:
        flashcard: The flashcard to update
        quality: User's recall quality (0-5)
            5: Perfect recall
            4: Correct with hesitation
            3: Correct with difficulty
            2: Incorrect but familiar
            1: Incorrect, answer seemed familiar
            0: Complete blackout
    
    Returns:
        Updated flashcard
    """
    
    # SM-2 algorithm implementation
    if quality >= 3:
        # Correct recall
        if flashcard.repetitions == 0:
            flashcard.interval = 1
        elif flashcard.repetitions == 1:
            flashcard.interval = 6
        else:
            flashcard.interval = int(flashcard.interval * flashcard.easinessFactor)
        
        flashcard.repetitions += 1
    else:
        # Incorrect recall - reset
        flashcard.repetitions = 0
        flashcard.interval = 1
    
    # Update easiness factor
    flashcard.easinessFactor = max(
        1.3,
        flashcard.easinessFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    )
    
    # Calculate next review date
    next_review = datetime.utcnow() + timedelta(days=flashcard.interval)
    flashcard.nextReviewAt = next_review.isoformat()
    
    return flashcard
