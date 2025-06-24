"""
File: src/memory/short_term.py
Purpose: Short-term working memory management for maintaining context during research sessions
Functionality: Stores conversation history, current plan, and working context with size limits and retrieval
Update Trigger: When memory management strategies change, context window limits are updated, or retrieval logic is modified
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from ..models import MemoryEntry, ResearchPlan, ToolResult
from ..config import config

class ShortTermMemory:
    """
    Manages short-term working memory for the research agent.
    Handles conversation history, current context, and temporary storage.
    """
    
    def __init__(self):
        self.max_entries = config.MAX_SHORT_TERM_MEMORY
        self.max_context_window = config.MAX_CONTEXT_WINDOW
        self.entries: List[MemoryEntry] = []
        self.current_plan: Optional[ResearchPlan] = None
        self.context_summary: str = ""
        
    def add_entry(self, content: str, entry_type: str, importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new memory entry."""
        entry_id = str(uuid.uuid4())
        
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            entry_type=entry_type,
            importance=importance,
            metadata=metadata or {}
        )
        
        self.entries.append(entry)
        
        # Maintain size limits
        self._manage_memory_size()
        
        return entry_id
    
    def add_conversation_message(self, role: str, message: str) -> str:
        """Add a conversation message to memory."""
        return self.add_entry(
            content=message,
            entry_type="conversation",
            importance=0.7,
            metadata={"role": role}
        )
    
    def add_observation(self, observation: str, tool_result: Optional[ToolResult] = None) -> str:
        """Add an observation from tool execution."""
        metadata = {}
        if tool_result:
            metadata = {
                "tool_name": tool_result.tool_name,
                "success": tool_result.success,
                "execution_time": tool_result.execution_time
            }
        
        return self.add_entry(
            content=observation,
            entry_type="observation",
            importance=0.8,
            metadata=metadata
        )
    
    def add_reasoning_step(self, thought: str, action: str, reasoning_type: str = "react") -> str:
        """Add a reasoning step to memory."""
        content = f"Thought: {thought}\nAction: {action}"
        return self.add_entry(
            content=content,
            entry_type="reasoning",
            importance=0.6,
            metadata={"reasoning_type": reasoning_type}
        )
    
    def update_plan(self, plan: ResearchPlan) -> None:
        """Update the current research plan."""
        self.current_plan = plan
        
        # Add plan summary to memory
        plan_summary = f"Research plan created with {len(plan.steps)} steps for query: '{plan.query}'"
        self.add_entry(
            content=plan_summary,
            entry_type="plan_update",
            importance=0.9,
            metadata={"plan_id": str(plan.created_at)}
        )
    
    def get_recent_entries(self, count: int = 5, entry_type: Optional[str] = None) -> List[MemoryEntry]:
        """Get the most recent memory entries."""
        filtered_entries = self.entries
        
        if entry_type:
            filtered_entries = [entry for entry in self.entries if entry.entry_type == entry_type]
        
        # Sort by timestamp (most recent first)
        filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_entries[:count]
    
    def get_context_window(self) -> str:
        """Generate a context window string for the agent."""
        context_parts = []
        
        # Add current plan if available
        if self.current_plan:
            context_parts.append(f"Current Research Plan: {self.current_plan.query}")
            context_parts.append(f"Plan has {len(self.current_plan.steps)} steps")
        
        # Add recent conversation
        recent_conversations = self.get_recent_entries(count=3, entry_type="conversation")
        if recent_conversations:
            context_parts.append("Recent Conversation:")
            for entry in reversed(recent_conversations):  # Chronological order
                role = entry.metadata.get("role", "unknown")
                context_parts.append(f"{role}: {entry.content}")
        
        # Add recent observations
        recent_observations = self.get_recent_entries(count=2, entry_type="observation")
        if recent_observations:
            context_parts.append("Recent Observations:")
            for entry in reversed(recent_observations):
                context_parts.append(f"- {entry.content}")
        
        # Add recent reasoning
        recent_reasoning = self.get_recent_entries(count=2, entry_type="reasoning")
        if recent_reasoning:
            context_parts.append("Recent Reasoning:")
            for entry in reversed(recent_reasoning):
                context_parts.append(f"- {entry.content}")
        
        context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > self.max_context_window:
            context = context[:self.max_context_window] + "... [truncated]"
        
        return context
    
    def get_plan_progress(self) -> Dict[str, Any]:
        """Get current plan progress information."""
        if not self.current_plan:
            return {"has_plan": False}
        
        completed_steps = sum(1 for step in self.current_plan.steps if step.completed)
        total_steps = len(self.current_plan.steps)
        
        return {
            "has_plan": True,
            "query": self.current_plan.query,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": (completed_steps / total_steps) * 100 if total_steps > 0 else 0,
            "current_step": next((step for step in self.current_plan.steps if not step.completed), None)
        }
    
    def search_entries(self, query: str, entry_type: Optional[str] = None) -> List[MemoryEntry]:
        """Search memory entries by content."""
        query_lower = query.lower()
        results = []
        
        for entry in self.entries:
            if entry_type and entry.entry_type != entry_type:
                continue
            
            if query_lower in entry.content.lower():
                results.append(entry)
        
        # Sort by relevance (exact matches first, then by importance)
        results.sort(key=lambda x: (query_lower not in x.content.lower(), -x.importance))
        
        return results
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about current memory usage."""
        entry_types = {}
        for entry in self.entries:
            entry_types[entry.entry_type] = entry_types.get(entry.entry_type, 0) + 1
        
        total_content_length = sum(len(entry.content) for entry in self.entries)
        
        return {
            "total_entries": len(self.entries),
            "entry_types": entry_types,
            "total_content_length": total_content_length,
            "memory_utilization": len(self.entries) / self.max_entries if self.max_entries > 0 else 0,
            "has_current_plan": self.current_plan is not None,
            "oldest_entry": min(self.entries, key=lambda x: x.timestamp).timestamp if self.entries else None,
            "newest_entry": max(self.entries, key=lambda x: x.timestamp).timestamp if self.entries else None
        }
    
    def clear_memory(self, preserve_plan: bool = True) -> None:
        """Clear all memory entries, optionally preserving the current plan."""
        self.entries.clear()
        
        if not preserve_plan:
            self.current_plan = None
        
        self.context_summary = ""
    
    def _manage_memory_size(self) -> None:
        """Manage memory size by removing old or low-importance entries."""
        if len(self.entries) <= self.max_entries:
            return
        
        # Sort by importance and timestamp (keep important and recent entries)
        sorted_entries = sorted(
            self.entries,
            key=lambda x: (x.importance, x.timestamp.timestamp()),
            reverse=True
        )
        
        # Keep only the most important/recent entries
        self.entries = sorted_entries[:self.max_entries]
        
        # Re-sort by timestamp for chronological order
        self.entries.sort(key=lambda x: x.timestamp)
    
    def _generate_summary(self) -> str:
        """Generate a summary of current memory state."""
        if not self.entries:
            return "No memory entries"
        
        recent_entries = self.get_recent_entries(count=5)
        summary_parts = []
        
        for entry in recent_entries:
            summary_parts.append(f"{entry.entry_type}: {entry.content[:100]}...")
        
        return "; ".join(summary_parts)
