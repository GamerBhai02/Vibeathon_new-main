# Dependency Optimization Guide

## Overview
This project has been optimized to reduce disk space usage during deployment by making heavy dependencies optional.

## Changes Made

### 1. Python Dependencies Split
- **Core dependencies** (`requirements.txt`): ~100MB
  - Essential packages for API and basic functionality
  - No heavy ML/AI libraries
  
- **Full dependencies** (`requirements-full.txt`): ~3GB
  - Includes document processing features
  - OCR, PDF processing, and RAG capabilities
  - ChromaDB and sentence-transformers

### 2. Installation Options

#### Minimal Installation (Recommended for Deployment)
```bash
pip install -r requirements.txt
```
This installs only core dependencies (~100MB):
- FastAPI, Uvicorn
- SQLModel, SQLAlchemy
- Basic authentication and API features
- Google Generative AI (Gemini)

#### Full Installation (For Development or Advanced Features)
```bash
pip install -r requirements-full.txt
```
This installs all dependencies including:
- Document ingestion and OCR (pytesseract, pdf2image)
- RAG system (chromadb, sentence-transformers)
- Image processing (Pillow, python-magic)

### 3. Poetry Installation
```bash
# Core features only
poetry install

# With document processing features
poetry install --extras full
```

### 4. System Packages (Replit)
Heavy system packages in `.replit` and `replit.nix` have been commented out:
- tesseract-ocr
- poppler-utils
- Image processing libraries (libjpeg, libpng, etc.)

Uncomment these only if you need document processing features.

## Features Affected

### Available with Core Installation
✅ User authentication and authorization
✅ Learning path generation with Gemini AI
✅ Quiz generation and evaluation
✅ Flashcard system with spaced repetition
✅ YouTube search integration
✅ Mock tests and practice problems
✅ Agent orchestration system

### Requires Full Installation
❌ Document upload and ingestion (PDF, images)
❌ OCR text extraction from images/PDFs
❌ RAG-based context retrieval
❌ Vector database features

## Environment Variables
No changes to environment variables are required. The application will gracefully handle missing optional dependencies.

## Deployment Recommendations

### Production Deployment (Minimal)
For most deployments, use the minimal installation:
```bash
pip install -r requirements.txt
npm install
npm run build
```

### Development Environment (Full)
For local development with all features:
```bash
pip install -r requirements-full.txt
npm install
npm run dev
```

### Platform-Specific Notes

#### Replit
- Default: Uses minimal dependencies
- To enable document processing:
  1. Uncomment packages in `.replit` nix section
  2. Run: `pip install -r requirements-full.txt`

#### Vercel/Netlify
- Use minimal installation in build commands
- Deploy Python backend separately if document processing is needed

#### Railway/Render
- Start command: `pip install -r requirements.txt && uvicorn python_backend.main:app --host 0.0.0.0 --port $PORT`
- For full features: Change to `requirements-full.txt`

## Disk Space Savings
- **Before**: ~3.5GB total installation
- **After (minimal)**: ~150MB total installation
- **Savings**: ~95% reduction in disk usage

## Error Handling
The application will show clear error messages if optional features are accessed without required dependencies:
```
RuntimeError: Document processing requires python-magic. 
Install with: pip install -r requirements-full.txt
```

## Migrating Existing Installations
If you have an existing installation:
1. Create a fresh virtual environment
2. Install minimal dependencies: `pip install -r requirements.txt`
3. Test your deployment
4. Only install full dependencies if needed

## Questions?
- Check `DEPLOYMENT.md` for deployment guides
- See `PYTHON_BACKEND.md` for Python backend details
- Review code comments in `python_backend/rag.py` and `python_backend/services/ingest.py`
