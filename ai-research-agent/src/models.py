"""
File: src/models.py
Purpose: Core data models and schemas for the AI Research Agent using Pydantic
Functionality: Defines type-safe data structures for plans, research steps, memory, and agent state
Update Trigger: When new data structures are needed, existing models require new fields, or validation rules change
Last Modified: 2024-06-24
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class AgentState(str, Enum):
    """Finite state machine states for the research agent."""
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    REPLANNING = "REPLANNING"
    SYNTHESIZING = "SYNTHESIZING"
    DONE = "DONE"
    ERROR = "ERROR"


class ReasoningStrategy(str, Enum):
    """Available reasoning strategies for task execution."""
    REACT = "REACT"
    TREE_OF_THOUGHTS = "TREE_OF_THOUGHTS"


class ToolResult(BaseModel):
    """Result from a tool execution."""
    tool_name: str = Field(..., description="Name of the executed tool")
    success: bool = Field(..., description="Whether the tool execution was successful")
    result: Union[str, Dict[str, Any]] = Field(..., description="Tool execution result")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: float = Field(..., ge=0, description="Time taken to execute in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional tool metadata")


class ResearchStep(BaseModel):
    """Individual step in a research plan."""
    step_number: int = Field(..., ge=1, description="Sequential step number")
    task: str = Field(..., min_length=1, description="Description of the task to perform")
    reasoning_strategy: ReasoningStrategy = Field(
        ReasoningStrategy.REACT, description="Reasoning strategy to use for this step"
    )
    tool_name: Optional[str] = Field(None, description="Preferred tool for this step")
    expected_output: str = Field(..., description="Expected type or format of output")
    dependencies: List[int] = Field(
        default_factory=list, description="Step numbers this step depends on"
    )
    completed: bool = Field(False, description="Whether this step has been completed")
    result: Optional[ToolResult] = Field(None, description="Result of step execution")


class ResearchPlan(BaseModel):
    """Complete research plan with multiple steps."""
    query: str = Field(..., min_length=1, description="Original research query")
    steps: List[ResearchStep] = Field(..., min_items=1, description="List of research steps")
    strategy: str = Field("decomposition_first", description="Planning strategy used")
    created_at: datetime = Field(default_factory=datetime.now)
    estimated_duration: Optional[int] = Field(None, ge=0, description="Estimated completion time in minutes")
    
    @validator("steps")
    def validate_step_numbers(cls, v):
        """Ensure step numbers are sequential and unique."""
        step_numbers = [step.step_number for step in v]
        if len(set(step_numbers)) != len(step_numbers):
            raise ValueError("Step numbers must be unique")
        if step_numbers != list(range(1, len(step_numbers) + 1)):
            raise ValueError("Step numbers must be sequential starting from 1")
        return v


class MemoryEntry(BaseModel):
    """Entry in the agent's memory system."""
    id: str = Field(..., description="Unique identifier for the memory entry")
    content: str = Field(..., min_length=1, description="Memory content")
    entry_type: str = Field(..., description="Type of memory entry (conversation, observation, etc.)")
    timestamp: datetime = Field(default_factory=datetime.now)
    importance: float = Field(0.5, ge=0, le=1, description="Importance score for memory retrieval")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentContext(BaseModel):
    """Current context and state of the research agent."""
    state: AgentState = Field(AgentState.IDLE, description="Current agent state")
    query: Optional[str] = Field(None, description="Current research query")
    plan: Optional[ResearchPlan] = Field(None, description="Current research plan")
    current_step: Optional[int] = Field(None, ge=1, description="Currently executing step number")
    working_memory: List[MemoryEntry] = Field(
        default_factory=list, description="Short-term working memory"
    )
    results: List[ToolResult] = Field(
        default_factory=list, description="Accumulated research results"
    )
    reasoning_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="History of reasoning steps"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def update_timestamp(self) -> None:
        """Update the last_updated timestamp."""
        self.last_updated = datetime.now()


class Citation(BaseModel):
    """Citation information for research sources."""
    source_url: Optional[str] = Field(None, description="URL of the source")
    title: str = Field(..., min_length=1, description="Title of the source")
    author: Optional[str] = Field(None, description="Author of the source")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    accessed_date: datetime = Field(default_factory=datetime.now, description="Date accessed")
    snippet: Optional[str] = Field(None, description="Relevant snippet or quote")
    relevance_score: float = Field(0.5, ge=0, le=1, description="Relevance to research query")


class ResearchReport(BaseModel):
    """Final research report with findings and citations."""
    query: str = Field(..., min_length=1, description="Original research query")
    executive_summary: str = Field(..., min_length=1, description="High-level summary of findings")
    detailed_findings: str = Field(..., min_length=1, description="Detailed research findings")
    conclusions: str = Field(..., min_length=1, description="Research conclusions")
    citations: List[Citation] = Field(default_factory=list, description="List of sources cited")
    methodology: str = Field(..., description="Research methodology used")
    limitations: Optional[str] = Field(None, description="Research limitations and caveats")
    generated_at: datetime = Field(default_factory=datetime.now)
    word_count: int = Field(0, ge=0, description="Total word count of the report")
    
    @validator("word_count", always=True)
    def calculate_word_count(cls, v, values):
        """Calculate word count from report sections."""
        text_fields = ["executive_summary", "detailed_findings", "conclusions"]
        total_words = sum(
            len(values.get(field, "").split()) for field in text_fields
        )
        return total_words


class ToolSchema(BaseModel):
    """Schema definition for a tool."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")
    required_parameters: List[str] = Field(default_factory=list, description="Required parameters")
