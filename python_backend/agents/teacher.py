"""TeacherAgent - Generates RAG-powered micro-lessons"""
from .base import BaseAgent
from typing import Dict, Any
import json


class TeacherAgent(BaseAgent):
    """Autonomous agent that creates micro-lessons with citations"""
    
    def __init__(self):
        super().__init__("TeacherAgent")
    
    async def generate_lesson(
        self,
        topic_name: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Generate micro-lesson with RAG-backed content"""
        from ..rag import RAGSystem
        
        # Initialize RAG system
        rag = RAGSystem(user_id)
        
        # Search for relevant context
        relevant_docs = await rag.search(topic_name, k=5)
        
        # Build context from retrieved documents
        context = "\n\n".join([
            f"[Source: {doc['source']}]\n{doc['content']}"
            for doc in relevant_docs
        ])
        
        # Generate lesson with LLM
        prompt = f"""
        Create a comprehensive micro-lesson on: {topic_name}
        
        Use the following source materials as reference:
        {context}
        
        Structure the lesson as:
        1. Overview (2-3 sentences)
        2. Key Concepts (3-5 bullet points)
        3. Step-by-step explanation
        4. Common pitfalls to avoid
        5. Practice tip
        
        Include citations to the source materials.
        Format as JSON with fields: overview, concepts, steps, pitfalls, practiceTip, citations
        """
        
        thought = await self.think(f"Generating lesson for {topic_name}")
        result = await self.act(prompt)
        
        # Parse LLM response or use structured fallback
        try:
            if self.llm:
                lesson = json.loads(result["result"])
            else:
                # Mock lesson for development
                lesson = {
                    "overview": f"This lesson covers {topic_name} in detail.",
                    "concepts": [
                        f"Core concept 1 of {topic_name}",
                        f"Core concept 2 of {topic_name}",
                        f"Core concept 3 of {topic_name}",
                    ],
                    "steps": [
                        f"Step 1: Understand the basics of {topic_name}",
                        f"Step 2: Practice with examples",
                        f"Step 3: Apply to real problems",
                    ],
                    "pitfalls": [
                        "Common mistake 1",
                        "Common mistake 2",
                    ],
                    "practiceTip": f"Practice {topic_name} daily for best results",
                    "citations": [doc["source"] for doc in relevant_docs],
                }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            lesson = {
                "overview": f"Lesson on {topic_name}",
                "concepts": ["Concept 1", "Concept 2"],
                "steps": ["Step 1", "Step 2"],
                "pitfalls": ["Avoid this"],
                "practiceTip": "Practice regularly",
                "citations": [],
            }
        
        reflection = await self.reflect("Lesson generated successfully")
        
        return lesson
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the teacher agent"""
        return await self.generate_lesson(**kwargs)
