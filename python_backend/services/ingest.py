
import os
import json
from pathlib import Path
from typing import List
from sqlmodel import Session

# Optional imports - gracefully handle missing dependencies
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from ..models import Document, Topic

# Only import RAG if chromadb is available
try:
    from ..rag import RAGSystem
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)

async def process_document(
    file_path: str,
    user_id: str,
    session: Session,
) -> List[Topic]:
    """
    Process an uploaded document:
    1.  Detects file type (PDF, image, text).
    2.  Performs OCR using Tesseract if it's a PDF or image.
    3.  Uses Gemini to summarize the content and extract key topics.
    4.  Adds the full text to the RAG vector store.
    5.  Saves the extracted topics to the database.
    
    Note: This feature requires optional dependencies.
    Install with: pip install -r requirements-full.txt
    """
    if not MAGIC_AVAILABLE:
        raise RuntimeError("Document processing requires python-magic. Install with: pip install -r requirements-full.txt")
    
    if not OCR_AVAILABLE:
        raise RuntimeError("OCR processing requires pytesseract, PIL, and pdf2image. Install with: pip install -r requirements-full.txt")
    
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        print(f"Processing file: {file_path}, MIME type: {mime_type}")

        text_content = ""
        if "pdf" in mime_type:
            images = convert_from_path(file_path)
            for image in images:
                text_content += pytesseract.image_to_string(image) + "\n"
        elif "image" in mime_type:
            image = Image.open(file_path)
            text_content = pytesseract.image_to_string(image)
        elif "text" in mime_type:
            with open(file_path, "r") as f:
                text_content = f.read()
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")

        if not text_content.strip():
            print("Warning: No text could be extracted from the document.")
            return []

        # Summarize and extract topics with Gemini
        topics = await summarize_and_extract_topics_with_gemini(text_content)
        
        # Add full text to RAG system for context retrieval (if available)
        if RAG_AVAILABLE:
            rag = RAGSystem(user_id)
            source_filename = Path(file_path).name
            await rag.add_documents(texts=[text_content], source=source_filename)
        else:
            print("Warning: RAG system not available. Skipping document indexing.")

        # Save topics to the database
        saved_topics = []
        for topic_data in topics:
            topic = Topic(
                userId=user_id,
                name=topic_data["topic"],
                summary=topic_data["content"],
                # Default scores, can be updated by planner agent later
                importanceScore=5, 
                masteryScore=0,
            )
            session.add(topic)
            saved_topics.append(topic)
        
        session.commit()
        for t in saved_topics:
            session.refresh(t)

        print(f"Successfully processed and saved {len(saved_topics)} topics.")
        return saved_topics

    except Exception as e:
        print(f"Error processing document {file_path}: {e}")
        # Consider how to handle exceptions: re-raise, log, etc.
        raise

async def summarize_and_extract_topics_with_gemini(text: str) -> List[dict]:
    """
    Uses the Gemini API to summarize text and extract a list of topics.
    """
    if not GEMINI_AVAILABLE:
        print("Warning: google-generativeai not available. Returning fallback content.")
        return [{"topic": "General Content", "content": text[:4000]}]
    
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found. Skipping summarization.")
        # Fallback to simple text splitting if no API key
        return [{"topic": "General Content", "content": text[:4000]}]

    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Use a fast and capable model
        
        prompt = f"""
        As an expert study assistant, your task is to analyze the following document text and extract the main educational topics.
        For each topic, provide a concise summary. Your output must be a valid JSON object.

        The JSON object should be a list of dictionaries, where each dictionary has two keys: "topic" and "content".
        - "topic": A short, descriptive name for the topic (e.g., "Python Data Structures", "Quantum Mechanics Fundamentals").
        - "content": A clear and concise summary of the key points, concepts, and formulas related to that topic from the text.

        Here is the text to analyze:
        ---
        {text[:20000]} 
        ---

        Return ONLY the JSON object. Do not include any other text or markdown formatting.
        Example format:
        [
            {{"topic": "Topic Name 1", "content": "Summary of content for topic 1."}},
            {{"topic": "Topic Name 2", "content": "Summary of content for topic 2."}}
        ]
        """
        
        response = await model.generate_content_async(prompt)
        
        # Clean the response to get only the JSON part
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        
        parsed_json = json.loads(response_text)
        
        # Basic validation of the parsed structure
        if not isinstance(parsed_json, list):
             raise ValueError("LLM response is not a list.")
        for item in parsed_json:
            if "topic" not in item or "content" not in item:
                raise ValueError("LLM response is missing 'topic' or 'content' keys.")

        return parsed_json

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback in case of API error
        return [{"topic": "Extraction Failed", "content": f"Could not process content due to an API error: {e}"}]
