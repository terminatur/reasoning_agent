"""
File: src/components/__init__.py
Purpose: Components module initialization and unified interface for research agent components
Functionality: Exports core components and provides orchestration interface for the research workflow
Update Trigger: When new components are added or component interfaces change
Last Modified: 2024-06-24
"""
from .planner import ResearchPlanner
from .executor import PlanExecutor
from .synthesis import ResearchSynthesizer

__all__ = ["ResearchPlanner", "PlanExecutor", "ResearchSynthesizer", "ComponentOrchestrator"]

class ComponentOrchestrator:
    """
    Orchestrates the interaction between all research components.
    Provides a unified interface for the complete research workflow.
    """
    
    def __init__(self):
        self.planner = ResearchPlanner()
        self.executor = PlanExecutor()
        self.synthesizer = ResearchSynthesizer()
    
    def conduct_research(self, query: str, strategy: str = "decomposition_first", context: str = ""):
        """
        Conduct complete research workflow from query to final report.
        This is a high-level interface that coordinates all components.
        
        Args:
            query: Research question or topic
            strategy: Planning strategy to use
            context: Additional context for research
        
        Returns:
            Dictionary with plan, execution results, and final report
        """
        # This method would coordinate the full workflow
        # but is not implemented here as it requires the main agent
        # to handle state management and memory coordination
        raise NotImplementedError(
            "Full research workflow should be implemented in the main agent class"
        )
    
    def get_component_status(self):
        """Get status of all components."""
        return {
            "planner": {
                "available": True,
                "has_llm": self.planner.llm is not None,
                "max_steps": self.planner.max_steps
            },
            "executor": {
                "available": True,
                "max_retries": self.executor.max_retries,
                "reasoning_manager": True
            },
            "synthesizer": {
                "available": True,
                "has_llm": self.synthesizer.llm is not None
            }
        }
