"""Agent for placement preparation and career guidance"""
import os
import json
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class PlacementAgent:
    """Provides placement preparation guidance and practice problems."""

    async def generate_interview_prep(self, topic: str, difficulty: str, company_type: str = "general") -> dict:
        """Generates interview preparation materials for a specific topic."""
        
        if not GEMINI_API_KEY:
            # Return mock data if no API key
            return {
                "topic": topic,
                "questions": [],
                "tips": [],
                "resources": []
            }
        
        prompt = f"""
        You are an expert career counselor and interview coach. Generate comprehensive interview preparation materials.

        Topic: {topic}
        Difficulty Level: {difficulty}
        Company Type: {company_type}

        Create a JSON object with the following structure:
        {{
          "topic": "{topic}",
          "keyConceptsToKnow": ["concept1", "concept2"],
          "commonQuestions": [
            {{
              "question": "Interview question text",
              "hints": ["hint1", "hint2"],
              "approach": "How to approach this question",
              "sampleAnswer": "A detailed sample answer"
            }}
          ],
          "codingProblems": [
            {{
              "title": "Problem title",
              "description": "Problem description",
              "difficulty": "Easy/Medium/Hard",
              "hints": ["hint1"],
              "solution": "Detailed solution explanation"
            }}
          ],
          "tipsAndTricks": ["tip1", "tip2"],
          "recommendedResources": ["resource1", "resource2"]
        }}

        Focus on practical, actionable advice for technical interviews.
        Respond with ONLY the JSON object, no additional text or markdown formatting.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(prompt)
        
        # Clean the response to extract JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        return json.loads(response_text)
    
    async def create_study_roadmap(self, target_role: str, current_skills: list, target_date: str) -> dict:
        """Creates a comprehensive study roadmap for placement preparation."""
        
        if not GEMINI_API_KEY:
            return {
                "roadmap": [],
                "estimatedTime": "N/A",
                "message": "Mock roadmap created"
            }
        
        prompt = f"""
        You are a career counselor specializing in tech placements. Create a detailed study roadmap.

        Target Role: {target_role}
        Current Skills: {', '.join(current_skills)}
        Target Date: {target_date}

        Create a JSON object with the following structure:
        {{
          "phases": [
            {{
              "phase": "Phase 1: Fundamentals",
              "duration_weeks": 4,
              "topics": ["topic1", "topic2"],
              "goals": ["goal1", "goal2"],
              "practiceProblems": 50,
              "milestones": ["milestone1"]
            }}
          ],
          "weeklySchedule": {{
            "dataStructures": 10,
            "algorithms": 10,
            "systemDesign": 5,
            "behavioralPrep": 3,
            "mockInterviews": 2
          }},
          "resources": [
            {{
              "type": "Book/Course/Platform",
              "name": "Resource name",
              "priority": "High/Medium/Low"
            }}
          ],
          "estimatedTotalHours": 200
        }}

        Respond with ONLY the JSON object, no additional text or markdown formatting.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(prompt)
        
        # Clean the response to extract JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        return json.loads(response_text)
