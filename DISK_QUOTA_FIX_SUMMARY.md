# Disk Quota Fix - Implementation Summary

## Problem
The project was experiencing "disk quota exceeded" errors during deployment due to installing heavy dependencies totaling ~3.5GB.

## Solution
Made heavy dependencies optional and implemented graceful degradation throughout the codebase.

## Changes Implemented

### 1. Python Dependencies Optimization

#### Before
All dependencies installed by default:
- chromadb (~500MB)
- sentence-transformers (~2GB with ML models)
- pytesseract, pdf2image, python-magic (~1GB)
- google-api-python-client
- Total: ~3.5GB

#### After
Split into two installation options:

**requirements.txt (Minimal - ~100MB)**
- fastapi, uvicorn
- sqlmodel, sqlalchemy
- google-generativeai (Gemini)
- Basic authentication and API packages
- No ML/AI model downloads

**requirements-full.txt (Full Features - ~3GB)**
- Includes all from requirements.txt
- Plus: chromadb, sentence-transformers
- Plus: pytesseract, pdf2image, python-magic, pillow
- Plus: google-api-python-client

### 2. Node.js Dependencies Optimization

#### Before
All Replit plugins in devDependencies (installed in production)

#### After
- Moved @replit/* plugins to optionalDependencies
- Updated vite.config.ts to gracefully handle missing plugins
- Plugins only loaded in Replit environment

Result: ~385MB for node_modules (no change, but won't fail in non-Replit environments)

### 3. System Packages Optimization

#### Before (.replit)
```
packages = ["freetype", "lcms2", "libimagequant", "libjpeg", "libtiff", 
            "libwebp", "libxcrypt", "openjpeg", "poppler_utils", "tcl", 
            "tesseract", "tk", "zlib"]
```

#### After
All packages commented out by default. Only install if needed for document processing.

### 4. Code Changes for Graceful Degradation

Updated the following files to handle missing dependencies:

1. **python_backend/rag.py**
   - Checks if chromadb is available
   - Exports RAG_AVAILABLE constant
   - Shows clear error messages when RAG features are used without dependencies

2. **python_backend/services/ingest.py**
   - Optional imports for magic, pytesseract, pdf2image
   - Clear error messages for document processing without dependencies
   - Falls back gracefully to text-only processing

3. **python_backend/core_agents.py**
   - Optional RAG import
   - TopicGenerator works without RAG, uses empty context

4. **python_backend/agents/teacher.py**
   - Optional RAG import
   - TeacherAgent generates lessons without document context

5. **python_backend/agents/quizgen.py**
   - Optional RAG import
   - QuizGenAgent generates quizzes without document context

6. **vite.config.ts**
   - Try/catch for Replit plugin imports
   - Stub functions when plugins unavailable

### 5. Documentation

Created comprehensive documentation:
- **OPTIMIZATION_GUIDE.md**: Complete guide to dependency optimization
- **DEPLOYMENT.md**: Updated with optimization notes
- **README.md**: Updated installation instructions

## Installation Commands

### Minimal (Recommended for Deployment)
```bash
npm install
pip install -r requirements.txt
npm run build
npm start
```

### Full (Development with All Features)
```bash
npm install
pip install -r requirements-full.txt
npm run build
npm run dev
```

## Features Matrix

### Available with Minimal Installation
- ✅ User authentication and authorization
- ✅ AI-powered learning with Gemini
- ✅ Quiz generation and evaluation
- ✅ Flashcard system with spaced repetition
- ✅ Mock tests and practice
- ✅ Placement preparation
- ✅ All agent orchestration

### Requires Full Installation
- ❌ Document upload (PDF/images)
- ❌ OCR text extraction
- ❌ RAG-based context retrieval
- ❌ Vector database features

When optional features are accessed without dependencies, users see:
```
RuntimeError: Document processing requires python-magic. 
Install with: pip install -r requirements-full.txt
```

## Results

### Disk Space Savings
- **Before**: ~3.5GB
- **After**: ~500MB (385MB node + 100MB Python)
- **Reduction**: 85% smaller

### Build Status
- ✅ npm run build: Success
- ✅ Python imports: Success
- ✅ All agents instantiate: Success
- ✅ No security vulnerabilities: Confirmed

### Deployment Compatibility
- ✅ Replit (with or without full features)
- ✅ Vercel (Node.js backend)
- ✅ Netlify (static + functions)
- ✅ Railway/Render (Python backend)
- ✅ Any platform with Node 20+ and Python 3.11+

## Migration Path

For existing deployments:
1. Remove old virtual environment
2. Install minimal dependencies: `pip install -r requirements.txt`
3. Test deployment
4. Only install full dependencies if document features needed

## Testing Performed

1. ✅ Build process completes
2. ✅ Minimal dependencies install correctly
3. ✅ All Python modules import without errors
4. ✅ All agents can be instantiated
5. ✅ Proper warning messages displayed
6. ✅ No security vulnerabilities
7. ✅ Graceful degradation verified

## Recommendations

1. **For most deployments**: Use minimal installation
2. **For document processing**: Use full installation
3. **For development**: Use full installation
4. **Monitor**: Check if document features are actually used
5. **Consider**: Deploying Python backend separately if needed

## Files Modified

1. requirements.txt (new minimal)
2. requirements-full.txt (new full)
3. pyproject.toml (optional extras)
4. package.json (optional dependencies)
5. .replit (commented packages)
6. replit.nix (minimal deps)
7. vite.config.ts (graceful plugin loading)
8. python_backend/rag.py (optional imports)
9. python_backend/services/ingest.py (optional imports)
10. python_backend/core_agents.py (optional imports)
11. python_backend/agents/teacher.py (optional imports)
12. python_backend/agents/quizgen.py (optional imports)
13. OPTIMIZATION_GUIDE.md (new)
14. DEPLOYMENT.md (updated)
15. README.md (updated)

## Maintenance Notes

- All optional imports use try/except blocks
- Clear error messages guide users to requirements-full.txt
- RAG_AVAILABLE flag allows conditional feature access
- No breaking changes to existing code paths
- Backward compatible with full installation

## Support

For questions or issues:
1. See OPTIMIZATION_GUIDE.md for detailed instructions
2. See DEPLOYMENT.md for deployment guides
3. Check error messages for dependency requirements
4. Install full dependencies if needed: `pip install -r requirements-full.txt`
