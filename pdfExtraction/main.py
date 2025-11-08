import argparse
import json
import sys
import asyncio
import os
from pathlib import Path

# Add the project root to sys.path for absolute imports if not already there
# This handles cases where pdfExtraction/main.py is run directly or as a subprocess
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from kreuzberg import extract_file, ExtractionConfig, TesseractConfig
from pdfExtraction.summarizer import summarize_content

async def extract_topics_and_content(file_path, mime_type):
    
    result = await extract_file(
        file_path,
        mime_type=mime_type,
        config=ExtractionConfig(
            force_ocr=True,
            ocr_config=TesseractConfig()
        )
    )
    full_extracted_text = result.content

    # Call the summarizer once with the entire extracted text
    # The summarizer is expected to return a list of topic-content dictionaries
    summarized_topics_data = summarize_content("Document Analysis", full_extracted_text)
    
    try:
        # Ensure the output is a list of dictionaries
        if isinstance(summarized_topics_data, str):
            # Attempt to parse if it's a string (expected from LLM)
            parsed_data = json.loads(summarized_topics_data)
        else:
            parsed_data = summarized_topics_data # Assume it's already parsed if not a string

        if not isinstance(parsed_data, list) or not all(isinstance(item, dict) and "topic" in item and "content" in item for item in parsed_data):
            raise ValueError("Summarizer did not return a valid list of topic-content dictionaries.")
        
        return parsed_data
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error processing summarizer output: {e}. Returning fallback.", file=sys.stderr)
        # Fallback if summarizer output is not as expected
        return [{"topic": "Full Document Summary", "content": full_extracted_text[:500] + "..."}]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract topics and content from a document file."
    )
    parser.add_argument("file", help="The path to the document file to process.")
    parser.add_argument("--mime_type", help="The mime type of the file.")
    args = parser.parse_args()

    extracted_data = asyncio.run(extract_topics_and_content(args.file, args.mime_type))
    json.dump(extracted_data, sys.stdout, ensure_ascii=False, indent=4)
