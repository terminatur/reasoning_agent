"""
File: src/__init__.py
Purpose: Main package initialization for the AI Research Agent
Functionality: Exports core classes and provides package-level configuration
Update Trigger: When package structure changes or new core exports are needed
Last Modified: 2024-06-24
"""
from .agent import ResearchAgent, research_agent
from .config import config
from .models import (
    AgentState, ResearchPlan, ResearchStep, ResearchReport, 
    Citation, ToolResult, MemoryEntry, AgentContext
)

__version__ = "0.1.0"
__author__ = "AI Research Agent Team"
__description__ = "Autonomous AI Research Agent with modular architecture"

__all__ = [
    "ResearchAgent",
    "research_agent", 
    "config",
    "AgentState",
    "ResearchPlan",
    "ResearchStep", 
    "ResearchReport",
    "Citation",
    "ToolResult",
    "MemoryEntry",
    "AgentContext"
]
