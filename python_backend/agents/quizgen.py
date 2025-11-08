"""QuizGenAgent - Generates practice questions and mock exams"""
from .base import BaseAgent
from typing import List, Dict, Any
import json


class QuizGenAgent(BaseAgent):
    """Autonomous agent that creates quizzes and exams"""
    
    def __init__(self):
        super().__init__("QuizGenAgent")
    
    async def generate_questions(
        self,
        topic_name: str,
        difficulty: str,
        count: int,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Generate practice questions"""
        
        prompt = f"""
        Generate {count} {difficulty} difficulty practice questions on: {topic_name}
        
        For each question provide:
        - question: The question text
        - hint: A subtle hint without giving away the answer
        - steps: Array of 3-5 progressive steps toward solution
        - fullSolution: Complete detailed solution
        - rubric: Grading criteria
        - difficulty: {difficulty}
        - confidence: Your confidence level (High/Medium/Low)
        
        Format as JSON array.
        """
        
        thought = await self.think(f"Generating {count} questions for {topic_name}")
        result = await self.act(prompt)
        
        # Parse or use mock
        try:
            if self.llm:
                questions = json.loads(result["result"])
            else:
                # Mock questions
                questions = [
                    {
                        "question": f"{difficulty.capitalize()} question {i+1} about {topic_name}",
                        "hint": f"Think about the key principles of {topic_name}",
                        "steps": [
                            "Identify the key concepts",
                            "Apply the formula or method",
                            "Verify your answer",
                        ],
                        "fullSolution": f"Detailed solution for question {i+1}",
                        "rubric": "5 points for approach, 3 for execution, 2 for explanation",
                        "difficulty": difficulty,
                        "citations": [f"Textbook Chapter {i+1}"],
                        "confidence": "High",
                    }
                    for i in range(count)
                ]
        except json.JSONDecodeError:
            # Fallback
            questions = []
        
        await self.reflect(f"Generated {len(questions)} questions")
        
        return questions
    
    async def generate_mock_exam(
        self,
        exam_type: str,
        duration: int,
        total_marks: int,
        topics: List[str],
        user_id: str,
    ) -> Dict[str, Any]:
        """Generate full mock exam"""
        
        # Distribute marks across topics
        marks_per_topic = total_marks // len(topics) if topics else total_marks
        
        questions = []
        question_id = 1
        
        for topic_id in topics:
            # Generate 2-3 questions per topic
            for i in range(2):
                marks = marks_per_topic // 2
                questions.append({
                    "id": f"q{question_id}",
                    "question": f"Question {question_id} on topic {topic_id}",
                    "marks": marks,
                    "rubric": f"{marks} marks for complete answer",
                    "topicId": topic_id,
                })
                question_id += 1
        
        return {
            "title": f"{exam_type} Mock Exam",
            "questions": questions,
            "instructions": f"Answer all questions. Time limit: {duration} minutes. Total marks: {total_marks}.",
        }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run quiz generation"""
        if "exam_type" in kwargs:
            return await self.generate_mock_exam(**kwargs)
        else:
            return await self.generate_questions(**kwargs)
