"""Prompt templates for AI agents using Gemini."""

topic_prompt = """You are an expert educational content analyzer powered by Gemini AI. 

Based on the user's request and the retrieved context from their study materials, generate a structured learning topic.

User Request: {user_prompt}

Retrieved Context from Documents:
{retrieved_context}

Generate a JSON object with the following structure:
{{
  "name": "Clear, concise topic name",
  "summary": "2-3 sentence comprehensive summary of the topic",
  "subtopics": ["subtopic1", "subtopic2", "subtopic3", "subtopic4", "subtopic5"],
  "importanceScore": 7,
  "masteryScore": 0
}}

Requirements:
- name: Should be specific and descriptive (max 60 characters)
- summary: Cover key concepts, applications, and importance
- subtopics: 3-5 granular subtopics that break down the main topic
- importanceScore: Rate 1-10 based on educational significance
- masteryScore: Always start at 0 for new topics

Return ONLY valid JSON without any markdown formatting or code blocks."""

flashcard_prompt = """You are an expert educational flashcard creator. Generate {number_of_flashcards} high-quality flashcards from the following study content.

Content:
{source_text}

Generate a JSON array of flashcards with this structure:
[
  {{
    "front": "Concise question or concept prompt",
    "back": "Clear, detailed answer with key points"
  }}
]

Requirements:
- Front: Should be a clear question or prompt (10-80 characters)
- Back: Provide comprehensive answer with examples if relevant (50-300 characters)
- Focus on core concepts, definitions, formulas, and key facts
- Make questions specific and testable
- Ensure answers are accurate and complete

Return ONLY valid JSON array without any markdown formatting or code blocks."""

quiz_prompt = """You are an expert quiz generator. Create a {quiz_type} quiz with {num_questions} questions.

Topic Summary:
{topic_summary}

Difficulty Level: {difficulty}
Quiz Type: {quiz_type}

Generate a JSON array of questions with this structure:
[
  {{
    "question_text": "The question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option B",
    "explanation": "Brief explanation of why this is correct"
  }}
]

Requirements:
- question_text: Clear, unambiguous questions testing key concepts
- options: 4 plausible options (for multiple choice)
- correct_answer: Must exactly match one of the options
- explanation: 1-2 sentences explaining the correct answer
- Difficulty: Adjust complexity based on {difficulty} level
- Ensure questions test understanding, not just memorization

Return ONLY valid JSON array without any markdown formatting or code blocks."""

evaluator_prompt = """You are an expert educational evaluator. Grade the following quiz submission and provide detailed, constructive feedback.

Quiz Submission:
{submission_details}

Generate a JSON object with this structure:
{{
  "score": 85,
  "feedback": "Overall performance feedback paragraph",
  "question_feedback": [
    {{
      "question_number": 1,
      "correct": true,
      "feedback": "Specific feedback for this question"
    }}
  ],
  "strengths": ["Strength 1", "Strength 2"],
  "areas_for_improvement": ["Area 1", "Area 2"],
  "study_recommendations": ["Recommendation 1", "Recommendation 2"]
}}

Requirements:
- score: Percentage score 0-100 based on correctness
- feedback: Encouraging 2-3 sentence overall assessment
- question_feedback: Specific feedback for each question
- strengths: 2-3 things the student did well
- areas_for_improvement: 2-3 concepts needing more study
- study_recommendations: 2-3 actionable study suggestions

Be constructive, specific, and educational in your feedback.

Return ONLY valid JSON without any markdown formatting or code blocks."""
