#!/usr/bin/env python3
"""
Lightweight PDF extraction using pdfminer.six
Extracts topics and content from PDF files without requiring OCR or heavy dependencies.
"""
import json
import argparse
import sys
import os

# Try to import pdfminer, provide helpful error if not available
try:
    from pdfminer.high_level import extract_text
except ImportError:
    print(json.dumps([{
        "topic": "Installation Required",
        "content": "Please install pdfminer.six: pip install pdfminer.six"
    }]), file=sys.stdout)
    sys.exit(0)

# Try to import google generativeai for enhanced topic extraction
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


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


def extract_topics_and_content(pdf_path):
    """
    Extract topics and content from a PDF file using text-based extraction.
    Falls back to simple extraction if advanced processing fails.
    """
    try:
        text = extract_text(pdf_path)
        
        if not text or len(text.strip()) < 50:
            # Fallback if extraction yields minimal text
            return [{
                "topic": "Document Content",
                "content": "The document was processed but minimal text content was extracted. This may be an image-based PDF requiring OCR."
            }]
        
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
            # Split content into chunks for better processing
            content_preview = text[:5000] if len(text) > 5000 else text
            results.append({
                "topic": "Document Content",
                "content": content_preview
            })
        
        return results
    
    except Exception as e:
        # Failsafe: return a minimal result with error information
        return [{
            "topic": "Extraction Error",
            "content": f"An error occurred during PDF extraction: {str(e)}. Please check if the file is a valid PDF."
        }]


def enhance_with_gemini(topics_list, api_key):
    """
    Use Gemini AI to enhance and restructure extracted topics.
    Returns enhanced topics or original if enhancement fails.
    """
    if not GEMINI_AVAILABLE or not api_key:
        return topics_list
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Combine all extracted content
        combined_text = "\n\n".join([
            f"Topic: {t['topic']}\nContent: {t['content']}"
            for t in topics_list
        ])
        
        prompt = f"""
        As an expert study assistant, analyze this extracted document content and organize it into clear educational topics.
        For each topic, provide a concise summary. Return a JSON array of objects.

        Each object should have:
        - "topic": A short, descriptive name
        - "content": A clear summary of key points and concepts

        Here is the extracted text:
        ---
        {combined_text[:15000]}
        ---

        Return ONLY a valid JSON array, no markdown formatting.
        Example: [{{"topic": "Topic 1", "content": "Summary 1"}}, {{"topic": "Topic 2", "content": "Summary 2"}}]
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        enhanced = json.loads(response_text)
        
        # Validate structure
        if isinstance(enhanced, list) and len(enhanced) > 0:
            if all("topic" in item and "content" in item for item in enhanced):
                return enhanced
        
        # If validation fails, return original
        return topics_list
    
    except Exception as e:
        print(f"Warning: Gemini enhancement failed: {e}", file=sys.stderr)
        return topics_list


def main():
    parser = argparse.ArgumentParser(
        description="Extract topics and content from a PDF file."
    )
    parser.add_argument("pdf_file", help="The path to the PDF file to process")
    parser.add_argument("--mime_type", help="MIME type (optional, for compatibility)")
    parser.add_argument("--enhance", action="store_true", help="Use Gemini AI to enhance extraction")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.pdf_file):
        result = [{
            "topic": "File Not Found",
            "content": f"The specified file '{args.pdf_file}' could not be found."
        }]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # Extract topics
    extracted_data = extract_topics_and_content(args.pdf_file)
    
    # Optionally enhance with Gemini
    if args.enhance:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            extracted_data = enhance_with_gemini(extracted_data, api_key)
    
    # Output as JSON
    print(json.dumps(extracted_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
