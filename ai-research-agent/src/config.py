"""
File: src/config.py
Purpose: Configuration management for API keys, model settings, and application constants
Functionality: Loads environment variables, defines model configurations, and provides centralized settings management
Update Trigger: When new API services are added, model configurations change, or environment setup requirements are modified
Last Modified: 2024-06-24
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for the AI Research Agent."""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    
    # Model configurations
    PLANNER_MODEL: str = "gpt-4-turbo"
    EXECUTOR_MODEL: str = "gpt-4-turbo"
    SYNTHESIS_MODEL: str = "gpt-4-turbo"
    REASONING_MODEL: str = "gpt-4-turbo"
    
    # Vector DB configuration
    PINECONE_INDEX_NAME: str = "research-agent-ltm"
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    
    # Memory settings
    MAX_SHORT_TERM_MEMORY: int = 10
    MAX_CONTEXT_WINDOW: int = 8000
    
    # Agent behavior settings
    MAX_PLAN_STEPS: int = 10
    MAX_REASONING_ITERATIONS: int = 5
    REPLANNING_THRESHOLD: float = 0.3
    
    # Tool settings
    WEB_SEARCH_MAX_RESULTS: int = 5
    PDF_MAX_PAGES: int = 50
    
    @classmethod
    def validate_required_keys(cls) -> bool:
        """Validate that all required API keys are present."""
        required_keys = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("TAVILY_API_KEY", cls.TAVILY_API_KEY),
        ]
        
        missing_keys = [key for key, value in required_keys if not value]
        
        if missing_keys:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_keys)}"
            )
        
        return True
    
    @classmethod
    def get_model_config(cls, component: str) -> str:
        """Get the model configuration for a specific component."""
        model_map = {
            "planner": cls.PLANNER_MODEL,
            "executor": cls.EXECUTOR_MODEL,
            "synthesis": cls.SYNTHESIS_MODEL,
            "reasoning": cls.REASONING_MODEL,
        }
        return model_map.get(component, cls.EXECUTOR_MODEL)


# Global config instance
config = Config()
