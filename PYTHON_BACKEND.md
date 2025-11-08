# Python FastAPI Backend - Vibeathon

## ✅ Complete Implementation

The Python FastAPI backend has been fully implemented with all required components for the AI-powered study platform.

### 🏗️ Architecture

**Tech Stack:**
- ✅ FastAPI for REST API and WebSocket support
- ✅ SQLModel + SQLite for persistence  
- ✅ Google Gemini AI for all LLM operations
- ✅ ChromaDB for vector search and RAG
- ✅ Tesseract OCR for document processing
- ✅ Judge0 integration for code execution
- ✅ YouTube API integration for video search
- ✅ SM-2 spaced repetition algorithm

### 🤖 Autonomous AI Agents

All agents implemented with Gemini AI integration:

1. **PlannerAgent** (`python_backend/agents/planner.py`)
   - Analyzes exam timeline and creates optimized study schedules
   - Prioritizes topics based on importance and mastery scores
   - Provides weekly goals and daily study blocks

2. **TeacherAgent** (`python_backend/agents/teacher.py`)
   - Generates RAG-powered micro-lessons with context from uploaded documents
   - Provides clear explanations with examples
   - Structured learning content with key concepts and summaries

3. **SchedulerAgent** (`python_backend/agents/scheduler.py`)
   - Creates detailed time-based study schedules
   - Distributes topics across available time
   - Includes breaks and varied activities

4. **PlacementAgent** (`python_backend/agents/placement.py`)
   - Generates interview preparation materials
   - Company-specific preparation guidance
   - Creates study roadmaps for target roles

5. **QuizGenAgent** (in `python_backend/agents.py`)
   - Creates practice questions with various difficulty levels
   - Generates mock exams (CIE/SEE/LAB)
   - Multiple quiz types supported

6. **EvaluatorAgent** (in `python_backend/agents.py`)
   - Grades quiz submissions with detailed feedback
   - Provides scores and constructive criticism
   - Helps identify areas for improvement

7. **AgentOrchestrator** (`python_backend/agents/orchestrator.py`)
   - Coordinates multiple agents to achieve complex goals
   - Decomposes user goals into agent tasks
   - Real-time streaming via WebSocket

### 📁 Project Structure

```
python_backend/
├── main.py                 # FastAPI app with all routes
├── database.py             # SQLModel database setup
├── models/                 # Database models
│   ├── user.py
│   ├── topic.py
│   ├── flashcard.py
│   ├── quiz.py
│   └── document.py
├── enums.py                # Enumerations for status, difficulty, etc.
├── agents.py               # Core agents (Topic, Flashcard, Quiz, Evaluator)
├── rag.py                  # ChromaDB vector store with lazy loading
├── env_check.py            # Environment validation script
├── agents/
│   ├── orchestrator.py     # Multi-agent coordination
│   ├── planner.py          # Study plan generation
│   ├── teacher.py          # Lesson generation
│   ├── scheduler.py        # Study scheduling
│   └── placement.py        # Placement preparation
└── services/
    ├── ingest.py           # OCR + topic extraction
    ├── sm2.py              # Spaced repetition algorithm
    ├── flashcards.py       # Flashcard generation
    ├── judge0.py           # Code execution
    ├── youtube.py          # YouTube video search
    └── anthropic.py        # Legacy (not used)
```

### 🔌 API Endpoints

#### Document Ingestion
- `POST /ingest` - Upload and process documents (PDF, images, text) with OCR and topic extraction

#### Topics
- `POST /topics/generate` - Generate new learning topic with AI
- `GET /topics` - Get all topics for current user

#### Flashcards
- `POST /flashcards/generate` - Generate flashcards from a source (topic)
- `POST /flashcards/{id}/review` - Review flashcard with SM-2 update

#### Quizzes
- `POST /quizzes/generate` - Generate quiz for a topic
- `POST /quizzes/submit` - Submit quiz answers for evaluation

#### AI Agents
- `POST /agents/lesson` - Generate micro-lesson with TeacherAgent
- `POST /agents/plan` - Generate study plan with PlannerAgent
- `POST /agents/schedule` - Create detailed schedule with SchedulerAgent
- `POST /agents/placement/interview-prep` - Get interview prep materials
- `POST /agents/placement/roadmap` - Create placement preparation roadmap
- `WS /ws/agent` - Real-time agent orchestration via WebSocket

#### Integrations
- `POST /code/execute` - Execute code via Judge0
- `GET /youtube/search` - Search YouTube for educational videos

### 🚀 Getting Started

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required system packages for OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
```

#### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required:
- `GEMINI_API_KEY` - Google Gemini API key

Optional:
- `YOUTUBE_API_KEY` - For YouTube video search
- `JUDGE0_API_URL` and `JUDGE0_API_KEY` - For code execution
- `DATABASE_URL` - Database connection (defaults to SQLite)
- `CHROMA_DB_PATH` - Vector DB path (defaults to ./chroma_db)
- `CORS_ORIGINS` - Allowed CORS origins

#### 3. Validate Environment

```bash
python -m python_backend.env_check
```

#### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn python_backend.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn python_backend.main:app --host 0.0.0.0 --port 8000
```

Or use the provided script:
```bash
./start_python_backend.sh
```

### 📝 Environment Variables

See `.env.example` for a complete list of environment variables.

Key variables:
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - Features work with graceful degradation
YOUTUBE_API_KEY=your_youtube_api_key_here
JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=your_judge0_api_key_here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./test.db
CHROMA_DB_PATH=./chroma_db

# CORS (optional, defaults provided)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### ✨ Key Features

1. **Document Ingest Pipeline**
   - Upload PDFs, images, or text files
   - OCR with Tesseract
   - Automatic topic extraction using Gemini
   - Vector indexing in ChromaDB for RAG

2. **RAG-Powered Learning**
   - Semantic search over uploaded materials
   - Context-aware lesson generation
   - Document-based flashcard creation

3. **Autonomous AI Agents**
   - Multi-agent orchestration
   - Real-time streaming via WebSocket
   - Goal-based task decomposition

4. **Spaced Repetition**
   - SM-2 algorithm implementation
   - Automatic flashcard scheduling
   - Adaptive review intervals

5. **Placement Preparation**
   - Interview preparation materials
   - Company-specific guidance
   - Study roadmaps for target roles

6. **Code Execution**
   - Judge0 integration
   - Support for multiple languages
   - Safe sandboxed execution

### 🔧 No API Keys? No Problem!

The system includes graceful degradation:

| Feature | With API Keys | Without GEMINI_API_KEY |
|---------|--------------|------------------------|
| **AI Agents** | Full Gemini responses | Mock responses |
| **Document Processing** | Full OCR + extraction | Text reading only |
| **RAG** | Full vector search | Keyword search fallback |
| **Code Execution** | Judge0 API | Returns without keys error |
| **YouTube** | Full search | Returns without keys error |

### 🧪 Testing

```bash
# Health check
curl http://localhost:8000/

# Generate a topic
curl -X POST http://localhost:8000/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Python data structures"}'

# Upload a document
curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf"
```

### 📊 What's Been Fixed

✅ Fixed Issues:
- Missing `json` import in agents.py
- Database `engine` initialization order in main.py
- Removed Anthropic API dependency (replaced with Gemini)
- Created prompt templates in agents.py
- Added Document model
- Created `/ingest` endpoint for document upload/OCR
- Updated RAG system with lazy loading for better resilience
- Added SchedulerAgent and PlacementAgent
- Added WebSocket endpoint for real-time agent console
- Updated CORS configuration with environment variable support
- Created environment validation script
- Updated .gitignore to exclude build artifacts and secrets

✅ Enhanced Features:
- All agents now use Gemini API (single LLM provider)
- Comprehensive agent endpoints in main.py
- WebSocket support for real-time agent orchestration
- Environment variable validation
- Comprehensive documentation and setup instructions

### 🎯 Architecture Decisions

- **Single LLM Provider**: Using only Google Gemini for consistency and simplicity
- **Lazy Loading**: RAG and embeddings are initialized on-demand to avoid blocking imports
- **WebSocket for Agents**: Real-time streaming of agent thoughts and results
- **Graceful Degradation**: System works without API keys in mock mode
- **Environment First**: Configuration through environment variables

---

**Built with FastAPI, Google Gemini, ChromaDB, SQLModel, and ❤️**
