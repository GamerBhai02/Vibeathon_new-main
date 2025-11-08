"""Agent Orchestrator to coordinate all other agents"""

import asyncio
import json
from typing import AsyncGenerator

from pydantic import BaseModel

from ..services.anthropic import call_anthropic_api
from .evaluator import EvaluatorAgent
from .planner import PlannerAgent
from .quizgen import QuizGenAgent
from .teacher import TeacherAgent


class AgentEvent(BaseModel):
    type: str
    data: dict


class AgentOrchestrator:
    """Coordinates agents to achieve a user's goal"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.agents = {
            "planner": PlannerAgent(),
            "teacher": TeacherAgent(),
            "quizgen": QuizGenAgent(),
            "evaluator": EvaluatorAgent(),
        }

    async def run(self, goal: str) -> AsyncGenerator[AgentEvent, None]:
        """Decompose goal and execute tasks with agents"""
        yield AgentEvent(type="thought", data={"text": "Interpreting your goal..."})

        # Use a powerful model to interpret the goal into a plan
        system_prompt = """
        You are an AI orchestrator. Your job is to interpret a user's goal and break it down into a series of tasks for other AI agents.
        You have the following agents available:
        - planner: Creates a study plan.
        - teacher: Provides lessons on a topic.
        - quizgen: Generates quizzes and mock exams.
        - evaluator: Grades answers and provides feedback.

        Based on the user's goal, create a JSON array of tasks to be executed in sequence. Each task should have:
        - "agent": The name of the agent to use.
        - "action": The specific action for the agent to perform.
        - "params": A dictionary of parameters for that action.

        Example:
        Goal: "Help me prepare for my calculus final in 2 weeks. I can study 2 hours a day."
        [{"agent": "planner", "action": "generate_plan", "params": {"exam_type": "calculus final", "exam_date": "in 2 weeks", "hours_per_day": 2}}]
        Goal: "Teach me about photosynthesis"
        [{"agent": "teacher", "action": "generate_lesson", "params": {"topic": "photosynthesis"}}]
        Goal: "Quiz me on Python data structures, medium difficulty"
        [{"agent": "quizgen", "action": "generate_questions", "params": {"topic": "Python data structures", "difficulty": "medium", "count": 5}}]
        """

        try:
            llm_response = await call_anthropic_api(
                system_prompt=system_prompt,
                user_prompt=goal,
                max_tokens=500,
            )
            plan = json.loads(llm_response)
        except Exception as e:
            yield AgentEvent(
                type="error",
                data={"text": f"Sorry, I couldn't create a plan. Error: {e}"},
            )
            return

        yield AgentEvent(type="plan", data={"plan": plan})

        # Execute the plan
        for i, task in enumerate(plan):
            agent_name = task.get("agent")
            action = task.get("action")
            params = task.get("params", {})

            if agent_name not in self.agents:
                yield AgentEvent(
                    type="error", data={"text": f"Unknown agent: {agent_name}"}
                )
                continue

            agent = self.agents[agent_name]
            method = getattr(agent, action, None)

            if not method or not asyncio.iscoroutinefunction(method):
                yield AgentEvent(
                    type="error",
                    data={"text": f"Unknown or non-async action: {action}"},
                )
                continue

            yield AgentEvent(
                type="thought",
                data={
                    "text": f"Step {i+1}: Executing {agent_name}.{action} with params: {params}"
                },
            )

            try:
                # Add user_id to params if not present
                if "user_id" not in params:
                    params["user_id"] = self.user_id

                result = await method(**params)
                yield AgentEvent(type="result", data={"step": i + 1, "result": result})
            except Exception as e:
                yield AgentEvent(
                    type="error",
                    data={
                        "text": f"Error in step {i+1} ({agent_name}.{action}): {e}"
                    },
                )
                # Stop execution on error
                break

        yield AgentEvent(type="done", data={"text": "All tasks completed!"})
