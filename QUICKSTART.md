# Quick Start Guide

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr poppler-utils

# For macOS
brew install tesseract poppler
```

## Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Minimum required: GEMINI_API_KEY
nano .env
```

## Initialize Database

```bash
# Create database tables
python -c "from python_backend.main import create_db_and_tables; create_db_and_tables()"
```

## Run the Server

```bash
# Development mode with auto-reload
uvicorn python_backend.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the provided script
./start_python_backend.sh
```

The server will be available at `http://localhost:8000`

## Validate Environment

```bash
# Check environment configuration
python -m python_backend.env_check
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

- `POST /ingest` - Upload documents for OCR and topic extraction
- `POST /topics/generate` - Generate new topics with AI
- `POST /flashcards/generate` - Create flashcards from topics
- `POST /quizzes/generate` - Generate quizzes
- `POST /agents/lesson` - Get AI-generated lessons
- `POST /agents/plan` - Create study plans
- `WS /ws/agent` - Real-time agent orchestration

See [PYTHON_BACKEND.md](PYTHON_BACKEND.md) for comprehensive documentation.
