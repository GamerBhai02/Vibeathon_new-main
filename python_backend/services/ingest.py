
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
    from pdfminer.high_level import extract_text as pdf_extract_text
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

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


def is_heading(line):
    """
    Determine if a line is likely a heading based on formatting heuristics.
    """
    line_clean = line.strip()
    if not line_clean:
        return False

    # Mostly uppercase → heading
    if line_clean.isupper() and len(line_clean) > 3:
        return True

    # Short Title Case → heading
    words = line_clean.split()
    if len(words) <= 8 and all(w[0].isupper() for w in words if w.isalpha()):
        return True

    return False


def extract_topics_from_text(text: str) -> List[dict]:
    """
    Extract topics and content from text using heading detection.
    """
    lines = text.split("\n")
    results = []
    current_topic = None
    current_content = []

    for line in lines:
        if is_heading(line):
            if current_topic:
                results.append({
                    "topic": current_topic.strip(),
                    "content": "\n".join(current_content).strip(),
                })
                current_content = []
            current_topic = line.strip()
        else:
            current_content.append(line)

    # Add the last topic at the end
    if current_topic:
        results.append({
            "topic": current_topic.strip(),
            "content": "\n".join(current_content).strip(),
        })

    # If no topics were extracted, create a single topic with all content
    if not results:
        content_preview = text[:5000] if len(text) > 5000 else text
        results.append({
            "topic": "Document Content",
            "content": content_preview
        })

    return results


async def process_document(
    file_path: str,
    user_id: str,
    session: Session,
) -> List[Topic]:
    """
    Process an uploaded document:
    1.  Detects file type (PDF, image, text).
    2.  For PDFs: Uses pdfminer.six for text extraction (not OCR).
    3.  For text files: Directly reads the content.
    4.  For images: Returns educational placeholder content.
    5.  Uses Gemini to enhance and extract key topics.
    6.  Adds the full text to the RAG vector store.
    7.  Saves the extracted topics to the database.
    """
    if not MAGIC_AVAILABLE:
        raise RuntimeError("Document processing requires python-magic. Install with: pip install python-magic")
    
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        print(f"Processing file: {file_path}, MIME type: {mime_type}")

        text_content = ""
        topics = []
        
        if "pdf" in mime_type:
            # Use pdfminer.six for text-based PDF extraction
            if not PDFMINER_AVAILABLE:
                raise RuntimeError("PDF processing requires pdfminer.six. Install with: pip install pdfminer.six")
            
            text_content = pdf_extract_text(file_path)
            
            if not text_content or len(text_content.strip()) < 50:
                # Fallback if extraction yields minimal text
                text_content = "The document was processed but minimal text content was extracted. This may be an image-based PDF requiring OCR."
            
            # Extract topics using heading detection
            topics = extract_topics_from_text(text_content)
            
        elif "text" in mime_type:
            # Directly read text files
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()
            
            if not text_content.strip():
                print("Warning: Text file is empty.")
                return []
            
            # Extract topics using heading detection
            topics = extract_topics_from_text(text_content)
            
        elif "image" in mime_type:
            # For images, return educational placeholder instead of empty
            text_content = "This is an educational image that has been uploaded. For better content extraction from images, consider using OCR tools or converting the image content to text format."
            topics = [{
                "topic": "Educational Image Content",
                "content": text_content
            }]
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")

        if not text_content.strip():
            print("Warning: No text could be extracted from the document.")
            return []

        # Enhance topics with Gemini if available
        if GEMINI_AVAILABLE and GEMINI_API_KEY and topics:
            topics = await enhance_topics_with_gemini(topics, text_content)
        
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

async def enhance_topics_with_gemini(topics: List[dict], full_text: str) -> List[dict]:
    """
    Uses the Gemini API to enhance extracted topics and their content.
    Takes the initially extracted topics and improves their summaries.
    """
    if not GEMINI_AVAILABLE:
        print("Warning: google-generativeai not available. Returning original topics.")
        return topics
    
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found. Returning original topics.")
        return topics

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Combine extracted topics for context
        topics_summary = "\n\n".join([
            f"Topic: {t['topic']}\nContent: {t['content']}"
            for t in topics
        ])
        
        prompt = f"""
        As an expert study assistant, enhance the following extracted educational topics from a document.
        Improve the content summaries to be more clear, concise, and educational.
        Your output must be a valid JSON array.

        The JSON array should contain objects with two keys: "topic" and "content".
        - "topic": A short, descriptive name for the topic (keep similar to original if appropriate).
        - "content": An enhanced, clear and concise summary of the key points, concepts, and formulas.

        Here are the extracted topics:
        ---
        {topics_summary[:15000]}
        ---

        Full document text for context (first 5000 chars):
        ---
        {full_text[:5000]}
        ---

        Return ONLY the JSON array. Do not include any other text or markdown formatting.
        Example format:
        [
            {{"topic": "Topic Name 1", "content": "Enhanced summary of content for topic 1."}},
            {{"topic": "Topic Name 2", "content": "Enhanced summary of content for topic 2."}}
        ]
        """
        
        response = await model.generate_content_async(prompt)
        
        # Clean the response to get only the JSON part
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        parsed_json = json.loads(response_text)
        
        # Basic validation of the parsed structure
        if not isinstance(parsed_json, list):
             print("Warning: LLM response is not a list. Returning original topics.")
             return topics
        
        for item in parsed_json:
            if "topic" not in item or "content" not in item:
                print("Warning: LLM response is missing 'topic' or 'content' keys. Returning original topics.")
                return topics

        return parsed_json

    except Exception as e:
        print(f"Error calling Gemini API for enhancement: {e}")
        # Return original topics if enhancement fails
        return topics


async def summarize_and_extract_topics_with_gemini(text: str) -> List[dict]:
    """
    Legacy function - Uses the Gemini API to summarize text and extract a list of topics.
    Kept for backward compatibility but now primarily uses extract_topics_from_text.
    """
    if not GEMINI_AVAILABLE:
        print("Warning: google-generativeai not available. Using text-based extraction.")
        return extract_topics_from_text(text)
    
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found. Using text-based extraction.")
        return extract_topics_from_text(text)

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        # Fallback to text-based extraction
        return extract_topics_from_text(text)
