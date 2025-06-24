# System Patterns: AI Research Agent

## Architecture Overview

The AI Research Agent follows a modular, single-agent architecture built around a finite state machine core. The system is designed with clean separation of concerns and SOLID principles.

```
📁 AI Research Agent
├── 🧠 Agent Core (agent.py)
│   └── Orchestrates workflow using FSM
├── 🎯 State Machine (state_machine.py) 
│   └── Manages predictable state transitions
├── 🧮 Reasoning Engines
│   ├── ReAct (reasoning/react.py)
│   └── Tree of Thoughts (reasoning/tree_of_thoughts.py)
├── 📋 Components
│   ├── Planner (components/planner.py)
│   ├── Executor (components/executor.py)
│   └── Synthesizer (components/synthesis.py)
├── 💾 Memory System
│   ├── Short-term (memory/short_term.py)
│   └── Long-term (memory/long_term.py)
└── 🛠️ Tools
    ├── Web Search (tools/web_search.py)
    ├── PDF Parser (tools/pdf_parser.py)
    └── Data Analyzer (tools/data_analyzer.py)
```

## Core Design Patterns

### 1. Finite State Machine Pattern
The agent uses a strict FSM to ensure predictable behavior:

**States:**
- `IDLE` → `PLANNING` → `EXECUTING` → `SYNTHESIZING` → `DONE`
- `ERROR` and `REPLANNING` as recovery states

**Key Benefits:**
- Prevents infinite loops and undefined states
- Observable state transitions with reasons
- Clear error recovery paths
- Pause/resume capabilities

**Implementation Location:** `ai_research_agent/state_machine.py`

### 2. Strategy Pattern for Reasoning
Multiple reasoning strategies are available via strategy pattern:

**ReAct Strategy:**
- Linear thought → action → observation loops
- Best for: Information gathering, tool-based tasks
- Use cases: Web searches, data extraction

**Tree of Thoughts Strategy:**
- Explores multiple reasoning paths simultaneously
- Best for: Complex analysis, creative problem solving
- Use cases: Strategic analysis, comparative studies

**Implementation Location:** `ai_research_agent/reasoning/`

### 3. Component-Based Architecture
Three core components handle distinct responsibilities:

**ResearchPlanner (`components/planner.py`):**
- Task decomposition and plan generation
- Dependency analysis and step ordering
- Replanning capabilities for error recovery

**PlanExecutor (`components/executor.py`):**
- Step-by-step execution with validation
- Tool integration and result collection
- Early termination logic for failure scenarios

**ResearchSynthesizer (`components/synthesis.py`):**
- Report generation from collected data
- Citation management and bibliography
- Multiple output formats (Markdown, text)

### 4. Hierarchical Memory System
Two-tier memory architecture for different temporal needs:

**Short-term Memory (`memory/short_term.py`):**
- Conversation history and working context
- Current plan progress and execution state
- Limited size with LRU eviction
- Cleared between sessions

**Long-term Memory (`memory/long_term.py`):**
- Persistent research findings and reports
- Citation database and knowledge base
- Vector database integration (Pinecone)
- Semantic search capabilities

### 5. Plugin-based Tool System
Tools are registered and accessed through a unified registry:

**Tool Interface:**
```python
class ToolSchema:
    name: str
    description: str
    parameters: Dict[str, Any]
    required_parameters: List[str]
```

**Tool Types:**
- **WebSearchTool**: Tavily API integration for web search
- **PDFParserTool**: Text extraction from PDF documents
- **DataAnalyzerTool**: Statistical analysis and data processing

**Tool Registry Location:** `ai_research_agent/tools/__init__.py`

## Critical Implementation Paths

### 1. Research Workflow Execution
```python
# Main execution path in agent.py
def _execute_research_workflow(self, strategy: str):
    # PLANNING: Generate research plan
    plan = self.planner.generate_plan(query, strategy, context, tools)
    
    # EXECUTING: Execute steps with dependency validation
    while has_executable_steps(plan):
        next_step = self.planner.get_next_executable_step(plan)
        result = self.executor.execute_step(step, context, tools)
        
        # Handle replanning on failure
        if not result.success and should_replan():
            new_plan = self.planner.replan_from_step(plan, step, context)
    
    # SYNTHESIZING: Generate final report
    report = self.synthesizer.generate_report(query, results, context)
```

### 2. State Management Flow
```python
# State transitions in state_machine.py
VALID_TRANSITIONS = {
    AgentState.IDLE: {PLANNING},
    AgentState.PLANNING: {EXECUTING, ERROR},
    AgentState.EXECUTING: {SYNTHESIZING, REPLANNING, ERROR},
    AgentState.REPLANNING: {EXECUTING, ERROR},
    AgentState.SYNTHESIZING: {DONE, ERROR},
    AgentState.ERROR: {PLANNING, IDLE},
    AgentState.DONE: {IDLE}
}
```

### 3. Memory Integration Points
```python
# Memory integration throughout workflow
self.memory.add_conversation_message("user", query)
self.memory.update_plan(plan)
self.memory.add_observation(f"Completed step {step.number}", result)
self.memory.store_research_report(report)
```

## Key Technical Decisions

### 1. Pydantic for Data Models
- **Decision**: Use Pydantic BaseModel for all data structures
- **Rationale**: Type safety, validation, JSON serialization
- **Implementation**: All models in `ai_research_agent/models.py`

### 2. Single LLM Provider Strategy
- **Decision**: Standardize on OpenAI for consistency
- **Rationale**: Consistent behavior across components
- **Configuration**: `ai_research_agent/config.py`

### 3. Optional Vector Database
- **Decision**: Pinecone integration with local fallback
- **Rationale**: Enhanced semantic search when available
- **Implementation**: Graceful degradation in `memory/long_term.py`

### 4. File Header Documentation
- **Decision**: Mandatory file headers with update triggers
- **Rationale**: Clear responsibility and maintenance guidance
- **Format**: Purpose, Functionality, Update Trigger, Last Modified

### 5. Tool Execution Safety
- **Decision**: Isolated tool execution with timeouts
- **Rationale**: Prevent system hangs and resource exhaustion
- **Implementation**: Error handling in `components/executor.py`

## Component Relationships

### Agent Core Dependencies
```python
# ResearchAgent initializes and coordinates all components
class ResearchAgent:
    def __init__(self):
        self.planner = ResearchPlanner()
        self.executor = PlanExecutor()
        self.synthesizer = ResearchSynthesizer()
        self.memory = MemoryManager()
```

### Memory System Integration
```python
# MemoryManager coordinates both memory tiers
class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
```

### Tool Registry Pattern
```python
# Tools register themselves for discovery
tool_registry.register_tool("web_search", WebSearchTool())
tool_registry.register_tool("pdf_parser", PDFParserTool())
tool_registry.register_tool("data_analyzer", DataAnalyzerTool())
```

## Error Handling Patterns

### 1. Graceful Degradation
- API failures fall back to alternative approaches
- Missing dependencies use simplified implementations
- Network issues trigger retry mechanisms

### 2. Error Recovery States
- `ERROR` state allows transition back to `PLANNING` or `IDLE`
- `REPLANNING` state handles step failures with plan modification
- Context preservation during error recovery

### 3. Resource Management
- Tool execution timeouts prevent hangs
- Memory limits prevent excessive resource usage
- Connection pooling for external APIs

## Performance Considerations

### 1. Lazy Loading
- Tools initialize only when needed
- Vector database connections on first use
- LLM clients created on demand

### 2. Caching Strategies
- Plan results cached to avoid redundant API calls
- Tool outputs cached for duplicate operations
- Memory retrieval uses efficient indexing

### 3. Async Operations
- Non-blocking tool execution where possible
- Parallel reasoning for Tree of Thoughts
- Background memory persistence

This architecture enables a robust, maintainable research agent that can handle complex workflows while providing transparent, observable behavior through its state-driven design.
