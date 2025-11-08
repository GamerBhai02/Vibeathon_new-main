"""
Agentverse Study Buddy - Python FastAPI Backend
Multi-agent autonomous exam preparation system
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

# Request/Response models
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from python_backend.agents import AgentOrchestrator
from python_backend.auth import create_access_token, get_current_user
from python_backend.database import create_db_and_tables, get_session
from python_backend.models import (
    Flashcard,
    MockExam,
    PracticeQuestion,
    StudyPlan,
    Topic,
    User,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and services on startup"""
    create_db_and_tables()
    print("✓ Database initialized")
    print("✓ Python FastAPI backend ready on port 5000")
    yield


app = FastAPI(
    title="Agentverse Study Buddy API",
    description="Autonomous AI agents for exam preparation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "backend": "python-fastapi"}


class LoginRequest(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    token: str
    user: dict


# Auth endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(payload: LoginRequest, session: Session = Depends(get_session)):
    """Email-based login (magic link simulation)"""
    # Find or create user
    statement = select(User).where(User.email == payload.email)
    user = session.exec(statement).first()

    if not user:
        user = User(email=payload.email, name=payload.email.split("@")[0])
        session.add(user)
        session.commit()
        session.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
    }


@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "createdAt": current_user.createdAt.isoformat()
        if current_user.createdAt
        else None,
    }


# Topic extraction from documents
@app.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Upload and process study materials"""
    from python_backend.services.ingest import process_document

    # Save uploaded file temporarily
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Process with OCR and topic extraction
    topics = await process_document(file_path, current_user.id, session)

    # Clean up
    os.remove(file_path)

    return {"success": True, "topicsExtracted": len(topics)}


# Topics
@app.get("/api/topics", response_model=List[Topic])
async def get_topics(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all topics for current user"""
    statement = select(Topic).where(Topic.userId == current_user.id)
    topics = session.exec(statement).all()
    return topics


# Study plan generation
@app.post("/api/plan/generate")
async def generate_study_plan(
    exam_type: str,
    exam_date: str,
    hours_per_day: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate personalized study plan using PlannerAgent"""
    from python_backend.agents.planner import PlannerAgent

    # Get user's topics
    topics_stmt = select(Topic).where(Topic.userId == current_user.id)
    topics = session.exec(topics_stmt).all()

    # Run PlannerAgent
    planner = PlannerAgent()
    plan = await planner.generate_plan(
        topics=topics,
        exam_type=exam_type,
        exam_date=exam_date,
        hours_per_day=hours_per_day,
    )

    # Save to database
    study_plan = StudyPlan(
        userId=current_user.id,
        startDate=plan["startDate"],
        endDate=plan["endDate"],
        examType=exam_type,
        blocks=plan["blocks"],
        weeklyGoal=plan["weeklyGoal"],
    )
    session.add(study_plan)
    session.commit()
    session.refresh(study_plan)

    return study_plan


@app.get("/api/plan")
async def get_study_plan(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get current study plan"""
    statement = (
        select(StudyPlan)
        .where(StudyPlan.userId == current_user.id)
        .order_by(StudyPlan.id.desc())
    )
    plan = session.exec(statement).first()
    return plan


# RAG-powered micro-lessons
@app.post("/api/learn/lesson")
async def generate_lesson(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate micro-lesson using TeacherAgent with RAG"""
    from python_backend.agents.teacher import TeacherAgent

    # Get topic
    topic = session.get(Topic, topic_id)
    if not topic or topic.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Generate lesson with RAG
    teacher = TeacherAgent()
    lesson = await teacher.generate_lesson(topic.name, current_user.id)

    return lesson


# Practice question generation
@app.post("/api/practice/generate")
async def generate_practice_questions(
    topic_id: str,
    difficulty: str,
    count: int = 5,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate practice questions using QuizGenAgent"""
    from python_backend.agents.quizgen import QuizGenAgent

    topic = session.get(Topic, topic_id)
    if not topic or topic.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Generate questions
    quizgen = QuizGenAgent()
    questions = await quizgen.generate_questions(
        topic_name=topic.name,
        difficulty=difficulty,
        count=count,
        user_id=current_user.id,
    )

    # Save to database
    for q_data in questions:
        question = PracticeQuestion(
            userId=current_user.id,
            topicId=topic_id,
            **q_data,
        )
        session.add(question)

    session.commit()
    return questions


# Mock exam generation and grading
@app.post("/api/mock/generate")
async def generate_mock_exam(
    exam_type: str,
    duration: int,
    total_marks: int,
    topics: List[str],
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate mock exam using QuizGenAgent"""
    from python_backend.agents.quizgen import QuizGenAgent

    quizgen = QuizGenAgent()
    exam = await quizgen.generate_mock_exam(
        exam_type=exam_type,
        duration=duration,
        total_marks=total_marks,
        topics=topics,
        user_id=current_user.id,
    )

    # Save to database
    mock_exam = MockExam(
        userId=current_user.id,
        type=exam_type,
        title=exam["title"],
        duration=duration,
        totalMarks=total_marks,
        questions=exam["questions"],
        instructions=exam["instructions"],
    )
    session.add(mock_exam)
    session.commit()
    session.refresh(mock_exam)

    return mock_exam


@app.get("/api/mock/list")
async def list_mock_exams(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all mock exams for current user"""
    statement = select(MockExam).where(MockExam.userId == current_user.id)
    mocks = session.exec(statement).all()
    return mocks


@app.post("/api/mock/attempt/start")
async def start_mock_attempt(
    mockId: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Start a new mock exam attempt"""
    mock = session.get(MockExam, mockId)
    if not mock or mock.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Mock exam not found")

    return {"attemptId": f"attempt-{mockId}", "mockExam": mock, "startTime": "now"}


@app.post("/api/mock/attempt/submit")
async def submit_mock_attempt(
    mock_id: str,
    answers: List[dict],
    time_taken_sec: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Grade mock exam using EvaluatorAgent"""
    from python_backend.agents.evaluator import EvaluatorAgent
    from python_backend.models import Attempt

    mock_exam = session.get(MockExam, mock_id)
    if not mock_exam or mock_exam.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Mock exam not found")

    # Grade using EvaluatorAgent
    evaluator = EvaluatorAgent()
    grading_result = await evaluator.grade_submission(
        questions=mock_exam.questions,
        answers=answers,
    )

    # Save attempt
    attempt = Attempt(
        userId=current_user.id,
        mockId=mock_id,
        score=grading_result["score"],
        timeTakenSec=time_taken_sec,
        answers=grading_result["answers"],
        topicBreakdown=grading_result["topicBreakdown"],
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    return attempt


# Flashcard generation with SM-2 algorithm
@app.post("/api/flashcards/generate")
async def generate_flashcards(
    source_type: str,
    source_id: str,
    count: int = 10,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate flashcards from lessons or topics"""
    from python_backend.services.flashcards import generate_flashcards_from_source

    flashcards = await generate_flashcards_from_source(
        source_type=source_type,
        source_id=source_id,
        count=count,
        user_id=current_user.id,
        session=session,
    )

    return flashcards


@app.post("/api/flashcards/review")
async def review_flashcard(
    flashcard_id: str,
    quality: int,  # 0-5 for SM-2 algorithm
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update flashcard using SM-2 spaced repetition algorithm"""
    from python_backend.services.sm2 import update_flashcard_sm2

    flashcard = session.get(Flashcard, flashcard_id)
    if not flashcard or flashcard.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    updated = update_flashcard_sm2(flashcard, quality)
    session.add(updated)
    session.commit()
    session.refresh(updated)

    return updated


@app.get("/api/flashcards/due")
async def get_due_flashcards(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get flashcards due for review today"""
    from datetime import datetime

    statement = select(Flashcard).where(
        Flashcard.userId == current_user.id, Flashcard.nextReview <= datetime.utcnow()
    )
    cards = session.exec(statement).all()
    return cards


# Placement preparation with code execution
@app.post("/api/placement/execute")
async def execute_code(
    language: str,
    code: str,
    stdin: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Execute code using Judge0 API"""
    from python_backend.services.judge0 import execute_code_judge0

    result = await execute_code_judge0(language, code, stdin)
    return result


@app.post("/api/code/execute")
async def execute_code_alias(
    language: str,
    code: str,
    stdin: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Execute code using Judge0 API (alias for placement execute)"""
    from python_backend.services.judge0 import execute_code_judge0

    result = await execute_code_judge0(language, code, stdin)
    return result


@app.post("/api/placement/profile")
async def create_placement_profile(
    targetCompanies: List[str],
    targetRole: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create placement preparation profile"""
    return {
        "id": f"profile-{current_user.id}",
        "targetCompanies": targetCompanies,
        "targetRole": targetRole,
        "created": True,
    }


@app.get("/api/placement/list")
async def list_placement_profiles(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List placement profiles"""
    return []


@app.get("/api/youtube/suggest")
async def suggest_youtube_videos(
    topic: str,
    current_user: User = Depends(get_current_user),
):
    """Suggest YouTube videos for a topic"""
    from python_backend.services.youtube import search_youtube

    try:
        videos = await search_youtube(topic)
        return {"videos": videos}
    except Exception as e:
        return {"videos": [], "error": str(e)}


# Agent orchestration with SSE streaming
@app.get("/api/agent/run")
async def run_agent_orchestrator(
    goal: str,
    current_user: User = Depends(get_current_user),
):
    """Run autonomous agent orchestrator with streaming thoughts"""

    async def event_generator():
        orchestrator = AgentOrchestrator(user_id=current_user.id)

        async for event in orchestrator.run(goal):
            yield f"data: {event.json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


# Mount static files and serve SPA (must be AFTER all API routes)
static_path = Path(__file__).parent.parent / "dist" / "public"
if static_path.exists():
    app.mount(
        "/assets", StaticFiles(directory=str(static_path / "assets")), name="assets"
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        from fastapi.responses import FileResponse

        if full_path.startswith("api/") or full_path.startswith("health"):
            raise HTTPException(status_code=404)
        return FileResponse(str(static_path / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "python_backend.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
    )
