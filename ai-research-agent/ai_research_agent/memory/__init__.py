"""
File: src/memory/__init__.py
Purpose: Memory module initialization and unified memory management interface
Functionality: Exports memory classes and provides unified memory management for the research agent
Update Trigger: When memory system architecture changes or new memory types are added
Last Modified: 2024-06-24
"""
from .short_term import ShortTermMemory
from .long_term import LongTermMemory

__all__ = ["ShortTermMemory", "LongTermMemory", "MemoryManager"]

class MemoryManager:
    """
    Unified memory management interface that coordinates short-term and long-term memory.
    Provides a single entry point for all memory operations.
    """
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        
    def add_conversation_message(self, role: str, message: str) -> str:
        """Add a conversation message to short-term memory."""
        return self.short_term.add_conversation_message(role, message)
    
    def add_observation(self, observation: str, tool_result=None) -> str:
        """Add an observation to short-term memory."""
        return self.short_term.add_observation(observation, tool_result)
    
    def add_reasoning_step(self, thought: str, action: str, reasoning_type: str = "react") -> str:
        """Add a reasoning step to short-term memory."""
        return self.short_term.add_reasoning_step(thought, action, reasoning_type)
    
    def update_plan(self, plan) -> None:
        """Update the current research plan in short-term memory."""
        self.short_term.update_plan(plan)
    
    def get_context_window(self) -> str:
        """Get the current context window for the agent."""
        return self.short_term.get_context_window()
    
    def store_research_finding(self, content: str, metadata: dict, embedding=None) -> str:
        """Store a research finding in long-term memory."""
        return self.long_term.store_research_finding(content, metadata, embedding)
    
    def store_citation(self, citation) -> str:
        """Store a citation in long-term memory."""
        return self.long_term.store_citation(citation)
    
    def store_research_report(self, report) -> str:
        """Store a complete research report in long-term memory."""
        return self.long_term.store_research_report(report)
    
    def search_long_term_memory(self, query: str, memory_type=None, limit: int = 5):
        """Search long-term memory for relevant content."""
        return self.long_term.search_memories(query, memory_type, limit)
    
    def get_memory_stats(self):
        """Get statistics about both memory systems."""
        return {
            "short_term": self.short_term.get_memory_stats(),
            "long_term": self.long_term.get_memory_stats()
        }
    
    def clear_short_term_memory(self, preserve_plan: bool = True) -> None:
        """Clear short-term memory."""
        self.short_term.clear_memory(preserve_plan)
    
    def export_memory(self, file_path: str) -> bool:
        """Export memory to a file."""
        return self.long_term.export_memory(file_path)
