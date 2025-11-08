"""EvaluatorAgent - Grades submissions with rubric alignment"""
from .base import BaseAgent
from typing import List, Dict, Any
import json


class EvaluatorAgent(BaseAgent):
    """Autonomous agent that grades answers and provides feedback"""
    
    def __init__(self):
        super().__init__("EvaluatorAgent")
    
    async def grade_submission(
        self,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Grade exam submission with detailed feedback"""
        
        total_marks = sum(q["marks"] for q in questions)
        graded_answers = []
        topic_breakdown = {}
        
        for i, answer in enumerate(answers):
            question = next((q for q in questions if q["id"] == answer["questionId"]), None)
            if not question:
                continue
            
            # Grade using LLM with rubric
            prompt = f"""
            Grade this answer against the rubric:
            
            Question: {question["question"]}
            Rubric: {question["rubric"]}
            Student Answer: {answer.get("answer", "")}
            Max Marks: {question["marks"]}
            
            Provide:
            1. Marks awarded (0 to {question["marks"]})
            2. Detailed feedback on strengths and improvements
            
            Format as JSON: {{"marksAwarded": X, "feedback": "..."}}
            """
            
            result = await self.act(prompt)
            
            try:
                if self.llm:
                    grading = json.loads(result["result"])
                else:
                    # Mock grading
                    answer_length = len(answer.get("answer", ""))
                    if answer_length > 100:
                        marks_awarded = int(question["marks"] * 0.8)
                        feedback = "Good comprehensive answer"
                    elif answer_length > 20:
                        marks_awarded = int(question["marks"] * 0.5)
                        feedback = "Adequate but could be more detailed"
                    else:
                        marks_awarded = int(question["marks"] * 0.2)
                        feedback = "Answer needs more depth and examples"
            except json.JSONDecodeError:
                grading = {
                    "marksAwarded": question["marks"] // 2,
                    "feedback": "Answer partially addresses the question",
                }
            
            graded_answers.append({
                "questionId": answer["questionId"],
                "answer": answer.get("answer", ""),
                "marksAwarded": grading["marksAwarded"],
                "feedback": grading["feedback"],
            })
            
            # Track topic performance
            topic_id = question.get("topicId", "unknown")
            if topic_id not in topic_breakdown:
                topic_breakdown[topic_id] = {"earned": 0, "possible": 0}
            topic_breakdown[topic_id]["earned"] += grading["marksAwarded"]
            topic_breakdown[topic_id]["possible"] += question["marks"]
        
        total_earned = sum(a["marksAwarded"] for a in graded_answers)
        score = int((total_earned / total_marks) * 100) if total_marks > 0 else 0
        
        await self.reflect(f"Graded submission: {score}% ({total_earned}/{total_marks})")
        
        return {
            "score": score,
            "answers": graded_answers,
            "topicBreakdown": topic_breakdown,
        }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run evaluator agent"""
        return await self.grade_submission(**kwargs)
