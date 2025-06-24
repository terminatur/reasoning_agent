# Technical Context: AI Research Agent

## Technology Stack

### Core Technologies
- **Python 3.11+**: Primary language with modern features
- **Pydantic**: Type-safe data models and validation
- **OpenAI API**: LLM integration for reasoning and synthesis
- **Tavily API**: Web search and information retrieval
- **Pinecone** (optional): Vector database for semantic search

### Development Tooling
- **uv**: Modern Python package manager and environment tool
- **ruff**: Fast Python linter and formatter
- **pytest**: Testing framework (development dependency)

### Architecture Dependencies
- **Finite State Machine**: Custom implementation for agent state management
- **Strategy Pattern**: Pluggable reasoning strategies (ReAct, Tree of Thoughts)
- **Component Architecture**: Modular design with clear separation of concerns

## Development Setup

### Environment Requirements
```bash
# Python version
Python 3.11+

# Package management
uv (replaces pip, poetry, pipenv)

# Code quality
ruff (linting and formatting)
```

### Installation Process
```bash
# Clone and navigate
cd ai-research-agent

# Install dependencies
uv sync

# Setup environment variables
cp .env.example .env
# Edit .env with API keys
```

### Required Environment Variables
```env
# Essential
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Optional (enables vector search)
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
```

## Technical Constraints

### API Dependencies
- **OpenAI API**: Required for all LLM operations
  - Planning, reasoning, synthesis
  - Rate limits and cost considerations
  - Fallback strategies not implemented

- **Tavily Search API**: Required for web research
  - Real-time information gathering
  - Search result quality dependent on service
  - No local search fallback

- **Pinecone Vector DB**: Optional but recommended
  - Semantic memory search capabilities
  - Falls back to local storage when unavailable
  - Requires separate service subscription

### Performance Constraints
- **Single-threaded execution**: No parallel tool execution
- **Memory limitations**: Short-term memory has size limits
- **API rate limits**: External services impose request limits
- **Network dependency**: Requires stable internet connection

### Architectural Constraints
- **Single-agent design**: No multi-agent coordination
- **Synchronous workflow**: Sequential step execution
- **State machine constraints**: Strict state transition rules
- **Tool isolation**: Tools cannot communicate directly

## Critical Configuration

### Core Configuration (`config.py`)
```python
class Config:
    # API Keys
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str
    PINECONE_API_KEY: Optional[str]
    
    # Model Configuration
    DEFAULT_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Memory Configuration
    PINECONE_INDEX_NAME: str = "research-agent-memory"
    SHORT_TERM_MEMORY_LIMIT: int = 100
    
    # Tool Configuration
    WEB_SEARCH_MAX_RESULTS: int = 10
    PDF_PARSER_MAX_PAGES: int = 50
```

### Project Configuration (`pyproject.toml`)
```toml
[project]
name = "ai-research-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "openai>=1.0.0",
    "tavily-python>=0.3.0",
    "pinecone-client>=3.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0"
]

[tool.ruff]
line-length = 88
target-version = "py311"
```

## Tool Integration Patterns

### Tool Registry System
```python
# Tool registration pattern
from .tools import tool_registry

# Register tools on import
tool_registry.register_tool("web_search", WebSearchTool())
tool_registry.register_tool("pdf_parser", PDFParserTool())
tool_registry.register_tool("data_analyzer", DataAnalyzerTool())

# Access tools
available_tools = tool_registry.get_tool_names()
tool_info = tool_registry.get_tool_info("web_search")
```

### Tool Interface Standard
```python
class ToolInterface:
    def get_schema(self) -> ToolSchema:
        """Return tool schema for LLM planning"""
        pass
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute tool with parameters"""
        pass
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        pass
```

### Error Handling Standards
```python
# Standard error handling pattern
try:
    result = tool.execute(**params)
    if not result.success:
        # Handle tool failure
        self.handle_tool_failure(result)
except Exception as e:
    # Handle system errors
    self.handle_system_error(e)
```

## Memory Architecture

### Short-term Memory (`memory/short_term.py`)
- **Storage**: In-memory Python data structures
- **Capacity**: Limited by configuration (default: 100 entries)
- **Persistence**: Session-only, cleared on restart
- **Access Pattern**: LIFO with importance scoring

### Long-term Memory (`memory/long_term.py`)
- **Primary**: Pinecone vector database (when available)
- **Fallback**: Local JSON storage
- **Capacity**: Unlimited (subject to external service limits)
- **Persistence**: Permanent across sessions
- **Access Pattern**: Semantic search with metadata filtering

### Memory Integration Points
```python
# Memory operations throughout agent lifecycle
self.memory.add_conversation_message("user", query)
self.memory.update_plan(research_plan)
self.memory.add_observation("step_result", tool_result)
self.memory.store_research_report(final_report)

# Memory retrieval
context = self.memory.get_context_window()
related_findings = self.memory.search_related_research(topic)
```

## Development Workflow

### Code Quality Standards
```bash
# Pre-commit checks (required)
uvx ruff check --fix
uvx ruff format

# Testing (when available)
uv run pytest tests/

# Type checking (implicit via Pydantic)
# Static analysis via ruff
```

### File Organization Standards
- **Single responsibility**: One class per file
- **File size limit**: 500 lines maximum
- **Header documentation**: Required for all files
- **Type hints**: Required for all functions
- **Pydantic models**: Required for all data structures

### Import Patterns
```python
# Standard import organization
from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from ..models import AgentState, ResearchPlan
from ..config import config
```

## Deployment Considerations

### Runtime Dependencies
- **Python 3.11+**: Core runtime requirement
- **API connectivity**: Required for OpenAI and Tavily
- **Memory allocation**: Varies by research complexity
- **Storage space**: Local fallback storage needs

### Security Considerations
- **API key management**: Environment variables only
- **Data privacy**: External API data sharing
- **Input validation**: Pydantic model validation
- **Error exposure**: Careful error message handling

### Monitoring and Debugging
```python
# Built-in status monitoring
agent_status = research_agent.get_status()
execution_summary = research_agent.get_execution_summary()
memory_stats = research_agent.memory.get_memory_stats()

# State machine observation
state_history = state_machine.get_transition_history()
valid_transitions = state_machine.get_valid_transitions(current_state)
```

## Testing Strategy

### Component Testing
- **Unit tests**: Individual component functionality
- **Integration tests**: Component interaction
- **Tool tests**: External API integration
- **State machine tests**: Transition validation

### Test Configuration
```python
# Test environment configuration
OPENAI_API_KEY="test_key"  # Mock in tests
TAVILY_API_KEY="test_key"  # Mock in tests
# No Pinecone in tests (local fallback)
```

## Future Technical Considerations

### Scalability Improvements
- **Async tool execution**: Parallel operation support
- **Caching layer**: Reduce API calls
- **Connection pooling**: Optimize external connections
- **Background processing**: Long-running research tasks

### Architecture Evolution
- **Multi-agent support**: Coordinated agent workflows
- **Plugin system**: External tool integration
- **Web interface**: GUI for research management
- **API server**: Expose agent as service

### Monitoring and Analytics
- **Performance metrics**: Execution time tracking
- **Quality metrics**: Research accuracy measurement
- **Usage analytics**: Tool utilization patterns
- **Error tracking**: Failure analysis and prevention

This technical foundation provides a robust, maintainable platform for autonomous research while maintaining clear separation of concerns and following modern Python development practices.
