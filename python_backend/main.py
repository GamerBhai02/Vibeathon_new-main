"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, SQLModel
from typing import List
import os
import shutil
from pathlib import Path

# ✅ Import engine at the top
from .database import get_session, engine
from .models import User, Topic, Flashcard, Quiz, QuizQuestion, Document
from .enums import TopicStatus, QuizDifficulty, QuizType
from .agents import TopicGenerator, FlashcardAgent, QuizGen, EvaluatorAgent
from .services import (
    update_flashcard_sm2, 
    search_youtube,
    execute_code_judge0,
    process_document,  # ✅ Add this import
)

app = FastAPI(title="Agentverse Study Buddy API", version="1.0.0")

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # ✅ Add Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Create upload directory ---
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# --- Dependency for getting current user (dev mode) ---
def get_current_user(session: Session = Depends(get_session)) -> User:
    """Get or create a dummy user for development."""
    user = session.exec(select(User).where(User.email == "dummy@example.com")).first()
    if not user:
        user = User(email="dummy@example.com", name="Demo User")
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

# --- API Endpoints ---

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Agentverse Study Buddy API is running",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
    }

# ✅ ADD INGEST ENDPOINT
@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and process a document (PDF, image, or text file).
    Performs OCR using Tesseract and extracts topics using Gemini API.
    """
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document with OCR + Gemini topic extraction
        topics = await process_document(
            file_path=str(file_path),
            user_id=current_user.id,
            session=session
        )
        
        # Clean up uploaded file
        file_path.unlink()
        
        return {
            "message": f"Document processed successfully",
            "filename": file.filename,
            "topics_extracted": len(topics),
            "topics": [
                {
                    "id": t.id,
                    "name": t.name,
                    "summary": t.summary,
                    "importanceScore": t.importanceScore,
                }
                for t in topics
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/topics/generate")
async def generate_new_topic(
    prompt: str = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generates a new learning topic using an AI agent."""
    agent = TopicGenerator()
    topic_data = await agent.generate_topic(prompt, current_user.id)

    topic = Topic(
        **topic_data,
        userId=current_user.id,
    )
    session.add(topic)
    session.commit()
    session.refresh(topic)
    return topic

@app.get("/topics", response_model=List[Topic])
def get_user_topics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Gets all topics for the current user."""
    return session.exec(select(Topic).where(Topic.userId == current_user.id)).all()

@app.post("/flashcards/generate")
async def generate_flashcards(
    source_type: str = Body(..., embed=True),
    source_id: str = Body(..., embed=True),
    count: int = Body(5, embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generates flashcards from a specified source."""
    agent = FlashcardAgent()
    flashcards = await agent.generate_flashcards(
        source_type, source_id, count, current_user.id, session
    )
    return flashcards

@app.post("/flashcards/{flashcard_id}/review")
def review_flashcard(
    flashcard_id: str,
    quality: int = Body(..., embed=True, ge=0, le=5),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Updates a flashcard's SM-2 data based on a review."""
    return update_flashcard_sm2(session, flashcard_id, quality, current_user.id)

@app.post("/quizzes/generate")
async def generate_quiz(
    topic_id: str = Body(..., embed=True),
    difficulty: QuizDifficulty = Body(QuizDifficulty.MEDIUM, embed=True),
    quiz_type: QuizType = Body(QuizType.MULTIPLE_CHOICE, embed=True),
    num_questions: int = Body(5, embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generates a quiz for a given topic."""
    topic = session.get(Topic, topic_id)
    if not topic or topic.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found")

    agent = QuizGen()
    quiz_data = await agent.generate_quiz(
        topic.summary, difficulty.value, quiz_type.value, num_questions
    )

    quiz = Quiz(
        title=f"Quiz for {topic.name}",
        difficulty=difficulty,
        quizType=quiz_type,
        userId=current_user.id,
        topicId=topic_id,
    )
    session.add(quiz)
    session.commit()
    session.refresh(quiz)

    for q_data in quiz_data: 
        question = QuizQuestion(
            question_text=q_data['question_text'],
            quizId=quiz.id
        )
        session.add(question)
    
    session.commit()
    session.refresh(quiz)
    
    return quiz

@app.post("/quizzes/submit")
async def submit_quiz(
    quiz_id: str = Body(..., embed=True),
    answers: List[dict] = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Submits answers to a quiz and gets an evaluation."""
    quiz = session.get(Quiz, quiz_id)
    if not quiz or quiz.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = session.exec(
        select(QuizQuestion).where(QuizQuestion.quizId == quiz_id)
    ).all()

    agent = EvaluatorAgent()
    evaluation = await agent.grade_submission(questions, answers)

    return evaluation

@app.post("/code/execute")
async def execute_code(
    language: str = Body(..., embed=True),
    code: str = Body(..., embed=True),
    stdin: str = Body(None, embed=True),
):
    """Executes a code snippet using Judge0."""
    try:
        return await execute_code_judge0(language, code, stdin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing code: {e}")

@app.get("/youtube/search")
async def youtube_search(query: str):
    """Searches YouTube for educational videos."""
    try:
        return await search_youtube(query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {e}")

# --- Database initialization ---
def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    """Initialize database on application startup."""
    print("🚀 Starting Agentverse Study Buddy API...")
    print(f"✅ Gemini API: {'Configured' if os.getenv('GEMINI_API_KEY') else '⚠️  Not configured (using mock mode)'}")
    print(f"✅ Database: {os.getenv('DATABASE_URL', 'sqlite:///./test.db')}")
    create_db_and_tables()
    print("✅ Database tables created")
    print("🎓 API is ready!")
