"""Base agent class with LangChain integration"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import os

# Optional LangChain imports with fallback
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain not fully available, agents will use mock mode")


class BaseAgent(ABC):
    """Base class for all autonomous agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM based on available API keys"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        # Check for OpenRouter (supports many models)
        if os.getenv("OPENROUTER_API_KEY"):
            try:
                return ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    model="anthropic/claude-3-sonnet",
                    temperature=0.7,
                )
            except Exception as e:
                print(f"⚠️  OpenRouter init failed: {e}")
                return None
        
        # Check for Gemini
        elif os.getenv("GEMINI_API_KEY"):
            try:
                # Use Gemini via OpenAI-compatible API
                return ChatOpenAI(
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    api_key=os.getenv("GEMINI_API_KEY"),
                    model="gemini-1.5-flash",
                    temperature=0.7,
                )
            except Exception as e:
                print(f"⚠️  Gemini init failed: {e}")
                return None
        
        # Fallback to mock for development
        else:
            print(f"⚠️  No API key found for {self.agent_name}, using mock mode")
            return None
    
    async def think(self, context: str) -> str:
        """Agent thinks about the problem"""
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return f"[Analyzing: {context[:100]}...]"
        
        try:
            messages = [
                SystemMessage(content=f"You are {self.agent_name}, an autonomous AI agent."),
                HumanMessage(content=f"Think step-by-step about: {context}"),
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"⚠️  {self.agent_name} think error: {e}")
            return f"[Error in thought process]"
    
    async def act(self, action_prompt: str) -> Dict[str, Any]:
        """Agent takes action based on plan"""
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return {"action": "mock", "result": f"Mock action from {self.agent_name}"}
        
        try:
            messages = [
                SystemMessage(content=f"You are {self.agent_name}."),
                HumanMessage(content=action_prompt),
            ]
            response = await self.llm.ainvoke(messages)
            return {"action": "completed", "result": response.content}
        except Exception as e:
            print(f"⚠️  {self.agent_name} act error: {e}")
            return {"action": "error", "result": str(e)}
    
    async def reflect(self, result: str) -> str:
        """Agent reflects on the result"""
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return f"[Reflection: {result[:100]}...]"
        
        try:
            messages = [
                SystemMessage(content=f"You are {self.agent_name}."),
                HumanMessage(content=f"Reflect on this result: {result}"),
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"⚠️  {self.agent_name} reflect error: {e}")
            return f"[Error in reflection]"
    
    @abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Main execution method - must be implemented by subclasses"""
        pass
