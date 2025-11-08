"""PlannerAgent - Builds personalized study plans"""
from .base import BaseAgent
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json


class PlannerAgent(BaseAgent):
    """Autonomous agent that creates personalized study schedules"""
    
    def __init__(self):
        super().__init__("PlannerAgent")
    
    async def generate_plan(
        self,
        topics: List[Any],
        exam_type: str,
        exam_date: str,
        hours_per_day: int,
    ) -> Dict[str, Any]:
        """Generate personalized study plan"""
        
        # Calculate days until exam
        exam_dt = datetime.fromisoformat(exam_date.replace("Z", "+00:00"))
        days_until_exam = (exam_dt - datetime.now()).days
        
        # Sort topics by importance and mastery (weak topics first)
        sorted_topics = sorted(
            topics,
            key=lambda t: (t.importanceScore * (100 - t.masteryScore)),
            reverse=True,
        )
        
        # Think about optimal allocation
        context = f"""
        Exam in {days_until_exam} days. Available: {hours_per_day} hours/day.
        Topics: {[f"{t.name} (importance:{t.importanceScore}, mastery:{t.masteryScore})" for t in sorted_topics]}
        
        Create an optimal study schedule.
        """
        
        thought = await self.think(context)
        print(f"[PlannerAgent] Thought: {thought[:200]}...")
        
        # Generate study blocks
        blocks = []
        current_date = datetime.now()
        block_id = 1
        
        for topic in sorted_topics:
            # Allocate time based on importance and mastery gap
            mastery_gap = 100 - topic.masteryScore
            sessions_needed = max(1, int(mastery_gap / 20))  # Rough estimate
            
            for i in range(sessions_needed):
                # Alternate between learn and practice
                activity = "learn" if i % 2 == 0 else "practice"
                duration = 60 if activity == "learn" else 45
                
                blocks.append({
                    "id": f"block-{block_id}",
                    "topicId": topic.id,
                    "topicName": topic.name,
                    "activity": activity,
                    "duration": duration,
                    "scheduledFor": current_date.isoformat(),
                    "completed": False,
                })
                
                block_id += 1
                current_date += timedelta(hours=2)  # Space out sessions
        
        # Reflect on the plan
        reflection = await self.reflect(f"Created {len(blocks)} study blocks")
        print(f"[PlannerAgent] Reflection: {reflection[:200]}...")
        
        return {
            "startDate": datetime.now().isoformat(),
            "endDate": exam_date,
            "blocks": blocks[:50],  # Limit to 50 blocks for now
            "weeklyGoal": f"Complete {min(14, len(blocks))} study sessions per week",
        }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the planner agent"""
        return await self.generate_plan(**kwargs)
