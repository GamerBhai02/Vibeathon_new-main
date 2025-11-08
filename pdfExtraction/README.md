# PDF Extraction Module

This module provides lightweight PDF text extraction using `pdfminer.six`, with optional enhancement via Google's Gemini AI.

## Features

- **Lightweight**: Uses pdfminer.six for text extraction (no OCR dependencies)
- **Failsafe**: Returns sensible defaults if extraction fails
- **AI Enhancement**: Optional Gemini AI integration for better topic extraction
- **Standalone**: Can run with system Python (no virtual environment required)

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pdfminer.six google-generativeai
```

## Usage

### Basic Usage

```bash
python3 extract_pdf.py path/to/document.pdf
```

### With Gemini Enhancement

```bash
export GEMINI_API_KEY="your-api-key"
python3 extract_pdf.py path/to/document.pdf --enhance
```

### With MIME Type (for compatibility)

```bash
python3 extract_pdf.py path/to/document.pdf --mime_type application/pdf
```

## Output Format

The script outputs JSON with the following structure:

```json
[
  {
    "topic": "Topic Name",
    "content": "Content summary or full text"
  },
  {
    "topic": "Another Topic",
    "content": "More content..."
  }
]
```

## Failsafe Behavior

The script includes multiple failsafe mechanisms:

1. **Missing pdfminer.six**: Returns installation instructions
2. **File not found**: Returns file not found error message
3. **Empty PDF**: Returns minimal content warning
4. **Extraction error**: Returns error description
5. **Gemini unavailable**: Falls back to basic extraction

## Integration with Node.js

The script is designed to be called from Node.js via `child_process.spawn()`:

```javascript
const pythonProcess = spawn('python3', [
  'pdfExtraction/extract_pdf.py',
  filePath,
  '--enhance'
], {
  env: {
    ...process.env,
    GEMINI_API_KEY: process.env.GEMINI_API_KEY
  }
});
```

## Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key (optional, for AI enhancement)

## Requirements

- Python 3.7+
- pdfminer.six >= 20221105
- google-generativeai (optional, for Gemini enhancement)

## Error Handling

The script always returns valid JSON, even in error cases:

- Exit code 0: Successful extraction
- Exit code 1: File not found
- Exit code 0: Other errors (with error message in JSON)

This ensures the calling application can always parse the output safely.
