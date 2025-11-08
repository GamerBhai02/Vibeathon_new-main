"""Document ingestion with OCR and topic extraction"""
import asyncio
import json
import os
from pathlib import Path
from typing import List

from sqlmodel import Session

from ..models import Document, Topic
from ..rag import RAGSystem


async def process_document(
    file_path: str,
    user_id: str,
    session: Session,
) -> List[any]:
    """Process uploaded document and extract topics"""
    
    # Determine mime type for pdfExtraction script
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == ".pdf":
        mime_type = "application/pdf"
    elif file_ext in [".png", ".jpg", ".jpeg"]:
        mime_type = "image/jpeg" # Assuming jpeg for simplicity, could be more robust
    elif file_ext == ".txt":
        mime_type = "text/plain"
    else:
        raise ValueError("Unsupported file format for ingestion")

    # Execute pdfExtraction/main.py as a subprocess
    pdf_extraction_script_path = Path(__file__).parent.parent.parent / "pdfExtraction" / "main.py"
    
    process = await asyncio.create_subprocess_exec(
        "python",
        str(pdf_extraction_script_path),
        file_path,
        "--mime_type",
        mime_type,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"Error during PDF extraction: {stderr.decode()}", flush=True)
        raise RuntimeError(f"PDF extraction failed: {stderr.decode()}")

    extracted_data = json.loads(stdout.decode())

    # Add to RAG system (using the full extracted text before summarization for RAG)
    # For RAG, we might want the original content, not the summarized one.
    # This part needs clarification based on exact RAG requirements.
    # For now, let's assume we add the raw content to RAG.
    # The `extracted_data` now contains summarized content per topic.
    
    # Reconstruct full text for RAG if needed, or pass summarized content
    full_extracted_text_for_rag = "\n\n".join([item["content"] for item in extracted_data])
    
    rag = RAGSystem(user_id)
    vector_ids = await rag.add_documents(
        texts=[full_extracted_text_for_rag], # Using summarized content for RAG
        source=os.path.basename(file_path),
    )
    
    # Save document record
    document = Document(
        userId=user_id,
        filename=os.path.basename(file_path),
        contentType=file_ext,
        extractedText=full_extracted_text_for_rag[:5000],  # Store first 5000 chars of summarized content
        vectorIds=vector_ids,
    )
    session.add(document)
    session.commit()
    
    topics = []
    for topic_data in extracted_data:
        topic = Topic(
            userId=user_id,
            name=topic_data["topic"],
            # Assuming importance and mastery are not directly from summarizer,
            # or need a default/calculation here.
            # For now, using dummy values or you can enhance summarizer to provide these.
            importanceScore=8,  
            masteryScore=50,  
            summary=topic_data["content"] # Store the summarized content
        )
        session.add(topic)
        topics.append(topic)
    
    session.commit()
    return topics
