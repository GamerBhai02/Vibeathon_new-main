"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
import tempfile
import os
from pathlib import Path

from .database import get_session, engine
from .models import User, Topic, Flashcard, Quiz, QuizQuestion, Document
from .enums import TopicStatus, QuizDifficulty, QuizType
from .agents import TopicGenerator, FlashcardAgent, QuizGen, EvaluatorAgent
from .services import (
    update_flashcard_sm2, 
    search_youtube,
    execute_code_judge0,
    process_document,
)

app = FastAPI()

# --- Middleware ---
# Get allowed origins from environment variable or use defaults
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Configurable for different environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency for getting current user (dummy implementation) ---
def get_current_user():
    # In a real app, this would involve token validation
    # For now, we'll just use a dummy user
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == 1)).first()
        if not user:
            user = User(id=1, username="dummyuser", email="dummy@example.com", hashed_password="")
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification."""
    return {
        "status": "healthy",
        "service": "vibeathon-python-backend",
        "version": "1.0.0"
    }

@app.post("/topics/generate")
async def generate_new_topic(
    prompt: str = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generates a new learning topic using an AI agent."""
    agent = TopicGenerator()
    topic_data = await agent.generate_topic(prompt, current_user.id)

    topic = Topic(**topic_data, userId=current_user.id, status=TopicStatus.IN_PROGRESS)
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
    source_id: int = Body(..., embed=True),
    count: int = Body(5, embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generates flashcards from a specified source."""
    agent = FlashcardAgent()
    flashcards = await agent.generate_flashcards(source_type, str(source_id), count, current_user.id, session)
    return flashcards

@app.post("/flashcards/{flashcard_id}/review")
def review_flashcard(
    flashcard_id: int,
    quality: int = Body(..., embed=True, ge=0, le=5),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Updates a flashcard's SM-2 data based on a review."""
    return update_flashcard_sm2(session, flashcard_id, quality, current_user.id)

@app.post("/quizzes/generate")
async def generate_quiz(
    topic_id: int = Body(..., embed=True),
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
    quiz_data = await agent.generate_quiz(topic.summary, difficulty, quiz_type, num_questions)

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
        question = QuizQuestion(question_text=q_data['question_text'], quizId=quiz.id)
        session.add(question)
    
    session.commit()
    session.refresh(quiz)
    
    return quiz

@app.post("/quizzes/submit")
async def submit_quiz(
    quiz_id: int = Body(..., embed=True),
    answers: List[dict] = Body(..., embed=True), # {question_id: int, answer: str}
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Submits answers to a quiz and gets an evaluation."""
    quiz = session.get(Quiz, quiz_id)
    if not quiz or quiz.userId != current_user.id:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = session.exec(select(QuizQuestion).where(QuizQuestion.quizId == quiz_id)).all()

    agent = EvaluatorAgent()
    evaluation = await agent.grade_submission(questions, answers)

    return evaluation


@app.post("/code/execute")
async def execute_code(
    language: str = Body(..., embed=True),
    code: str = Body(..., embed=True),
    stdin: str = Body(None, embed=True),
):
    """Executes a code snippet."""
    try:
        return await execute_code_judge0(language, code, stdin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing code: {e}")

@app.get("/youtube/search")
async def youtube_search(query: str):
    """Searches YouTube for videos."""
    try:
        return await search_youtube(query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {e}")

@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Uploads and processes a document (PDF, image, or text file) for OCR and topic extraction."""
    try:
        # Create a temporary file to store the upload
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            # Write uploaded file to temporary file
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process the document (OCR, topic extraction, RAG indexing)
            topics = await process_document(
                file_path=tmp_file_path,
                user_id=str(current_user.id),
                session=session,
            )
            
            # Create a Document record
            document = Document(
                userId=current_user.id,
                filename=file.filename,
                contentType=file.content_type or "application/octet-stream",
                extractedText="",  # Could be populated with full text if needed
                vectorIds=[],  # Could be populated with ChromaDB IDs
            )
            session.add(document)
            session.commit()
            session.refresh(document)
            
            return {
                "message": "Document processed successfully",
                "document_id": document.id,
                "topics_extracted": len(topics),
                "topics": [{"id": t.id, "name": t.name} for t in topics]
            }
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@app.post("/agents/lesson")
async def generate_lesson(
    topic_name: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Generates a micro-lesson on a specific topic using TeacherAgent."""
    from .agents.teacher import TeacherAgent
    agent = TeacherAgent()
    try:
        lesson = await agent.generate_lesson(topic_name, str(current_user.id))
        return lesson
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lesson: {e}")

@app.post("/agents/plan")
async def generate_study_plan(
    exam_type: str = Body(..., embed=True),
    exam_date: str = Body(..., embed=True),
    hours_per_day: int = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generates a study plan using PlannerAgent."""
    from .agents.planner import PlannerAgent
    agent = PlannerAgent()
    try:
        topics = session.exec(select(Topic).where(Topic.userId == current_user.id)).all()
        plan = await agent.generate_plan(topics, exam_type, exam_date, hours_per_day)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {e}")

@app.post("/agents/schedule")
async def create_schedule(
    start_date: str = Body(..., embed=True),
    end_date: str = Body(..., embed=True),
    hours_per_day: int = Body(..., embed=True),
    preferences: dict = Body(None, embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Creates a detailed study schedule using SchedulerAgent."""
    from .agents.scheduler import SchedulerAgent
    agent = SchedulerAgent()
    try:
        topics = session.exec(select(Topic).where(Topic.userId == current_user.id)).all()
        schedule = await agent.create_schedule(topics, start_date, end_date, hours_per_day, preferences)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating schedule: {e}")

@app.post("/agents/placement/interview-prep")
async def generate_interview_prep(
    topic: str = Body(..., embed=True),
    difficulty: str = Body("medium", embed=True),
    company_type: str = Body("general", embed=True),
):
    """Generates interview preparation materials using PlacementAgent."""
    from .agents.placement import PlacementAgent
    agent = PlacementAgent()
    try:
        prep_materials = await agent.generate_interview_prep(topic, difficulty, company_type)
        return prep_materials
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating interview prep: {e}")

@app.post("/agents/placement/roadmap")
async def create_placement_roadmap(
    target_role: str = Body(..., embed=True),
    current_skills: List[str] = Body(..., embed=True),
    target_date: str = Body(..., embed=True),
):
    """Creates a placement preparation roadmap using PlacementAgent."""
    from .agents.placement import PlacementAgent
    agent = PlacementAgent()
    try:
        roadmap = await agent.create_study_roadmap(target_role, current_skills, target_date)
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating roadmap: {e}")

@app.websocket("/ws/agent")
async def websocket_agent_console(websocket: WebSocket):
    """WebSocket endpoint for real-time agent interaction using AgentOrchestrator."""
    await websocket.accept()
    
    # Note: In production, you'd want to authenticate the WebSocket connection
    # For now, we'll use a dummy user ID
    user_id = "1"
    
    try:
        from .agents.orchestrator import AgentOrchestrator
        
        # Receive the user's goal
        data = await websocket.receive_json()
        goal = data.get("goal", "")
        
        if not goal:
            await websocket.send_json({"type": "error", "data": {"text": "No goal provided"}})
            return
        
        # Create orchestrator and run
        orchestrator = AgentOrchestrator(user_id)
        
        # Stream agent events back to client
        async for event in orchestrator.run(goal):
            await websocket.send_json(event.dict())
        
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"text": f"An error occurred: {str(e)}"}
            })
        except:
            pass

# --- Database Initialization ---

def create_db_and_tables():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
