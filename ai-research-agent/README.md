# 🔬 AI Research Agent

An autonomous AI-powered research agent that performs deep, multi-step research on complex topics and generates comprehensive reports with verifiable citations.

## 🌟 Features

- **Autonomous Research**: Conducts thorough research across multiple sources
- **Modular Architecture**: Built with clean separation of concerns and SOLID principles
- **State-Driven Operation**: Uses finite state machine for predictable behavior
- **Hybrid Reasoning**: Combines ReAct and Tree of Thoughts frameworks
- **Hierarchical Memory**: Short-term working memory + persistent long-term storage
- **Citation Management**: Automatic source tracking and bibliography generation
- **Multiple Tool Support**: Web search, PDF analysis, and data processing
- **Export Capabilities**: Generate reports in Markdown or text format

## 🏗️ Architecture

The agent follows a modular, single-agent architecture with these core components:

```
📁 AI Research Agent
├── 🧠 Reasoning Engines (ReAct + Tree of Thoughts)
├── 📋 Planning System (Task decomposition)
├── ⚙️ Execution Engine (Step coordination)
├── 📝 Synthesis Engine (Report generation)
├── 💾 Memory System (Short-term + Long-term)
└── 🛠️ Tool Registry (Web search, PDF parser, Data analyzer)
```

### Core Principles

- **Modular Design**: Independent, testable components
- **State-Driven**: Finite State Machine prevents infinite loops
- **Hierarchical Planning**: Divide and conquer approach
- **Hybrid Reasoning**: Strategy selection based on task complexity
- **Observable Behavior**: Clear state transitions and logging

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Required API keys (see Configuration section)

### Installation

1. **Clone and setup the project:**
```bash
cd ai-research-agent
```

2. **Install dependencies using uv:**
```bash
uv sync
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run your first research:**
```bash
uv run python main.py "What are the latest developments in quantum computing?"
```

## ⚙️ Configuration

Create a `.env` file with the following required variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
```

### Getting API Keys

- **OpenAI**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- **Tavily**: Sign up at [Tavily Search API](https://tavily.com/)
- **Pinecone** (optional): Create account at [Pinecone](https://www.pinecone.io/)

## 📖 Usage

### Command Line Interface

```bash
# Basic research query
uv run python main.py "Your research question"

# Interactive mode
uv run python main.py --interactive

# Run examples
uv run python main.py --examples

# Check agent status
uv run python main.py --status

# Use different planning strategy
uv run python main.py "Climate change impacts" --strategy interleaved
```

### Python API

```python
from src.agent import research_agent

# Conduct research
report = research_agent.research(
    query="How is AI being used in healthcare?",
    strategy="decomposition_first"
)

# Access results
print(report.executive_summary)
print(f"Found {len(report.citations)} sources")

# Get agent status
status = research_agent.get_status()
print(f"Agent state: {status['state']}")
```

### Example Research Queries

- "What are the environmental impacts of cryptocurrency mining?"
- "Analyze the current state of renewable energy adoption globally"
- "How is artificial intelligence transforming the finance industry?"
- "What are the latest breakthroughs in gene therapy?"

## 🛠️ Development

### Code Quality

The project follows strict coding standards:

```bash
# Lint code
uvx ruff check --fix

# Format code
uvx ruff format

# Run both
uvx ruff check --fix && uvx ruff format
```

### Project Structure

```
ai-research-agent/
├── src/
│   ├── agent.py              # Main agent orchestration
│   ├── config.py             # Configuration management
│   ├── models.py             # Pydantic data models
│   ├── state_machine.py      # FSM implementation
│   ├── components/           # Core components
│   │   ├── planner.py        # Task decomposition
│   │   ├── executor.py       # Plan execution
│   │   └── synthesis.py      # Report generation
│   ├── reasoning/            # Reasoning engines
│   │   ├── react.py          # ReAct framework
│   │   └── tree_of_thoughts.py # ToT framework
│   ├── memory/               # Memory systems
│   │   ├── short_term.py     # Working memory
│   │   └── long_term.py      # Persistent storage
│   └── tools/                # External tools
│       ├── web_search.py     # Web search via Tavily
│       ├── pdf_parser.py     # PDF text extraction
│       └── data_analyzer.py  # Data analysis
├── main.py                   # CLI entry point
├── pyproject.toml           # Project configuration
└── .env.example             # Environment template
```

### Adding New Tools

1. Create a new tool class in `src/tools/`
2. Implement required methods: `get_schema()`, `execute()`, `validate_input()`
3. Register in `src/tools/__init__.py`

Example:
```python
class MyTool:
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="my_tool",
            description="Description of what the tool does",
            parameters={...},
            required_parameters=[...]
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # Tool implementation
        pass
```

## 🎯 Reasoning Strategies

### ReAct (Reason + Act)
- **Best for**: Information gathering, tool-based tasks
- **Approach**: Linear thought → action → observation loops
- **Use cases**: Web searches, data extraction, straightforward analysis

### Tree of Thoughts
- **Best for**: Complex analysis, creative problem solving
- **Approach**: Explores multiple reasoning paths simultaneously
- **Use cases**: Strategic analysis, comparative studies, open-ended research

The agent automatically selects the appropriate strategy based on task complexity, or you can specify one explicitly.

## 📊 Memory System

### Short-term Memory
- Conversation history
- Current plan and progress
- Recent observations
- Working context (limited size)

### Long-term Memory
- Research reports
- Citation database
- Learned patterns
- Persistent knowledge (via Pinecone vector DB)

## 🔧 Troubleshooting

### Common Issues

1. **Missing API Keys**
   ```
   Error: Missing required environment variables
   ```
   **Solution**: Ensure all required API keys are set in `.env` file

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'src'
   ```
   **Solution**: Run commands with `uv run python` from project root

3. **Tool Failures**
   ```
   Tool execution failed: API request failed
   ```
   **Solution**: Check internet connection and API key validity

### Debug Mode

For detailed logging, set environment variable:
```bash
export PYTHONPATH=.
export DEBUG=1
uv run python main.py "your query"
```

## 🧪 Testing

Run the test suite:
```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio

# Run tests
uv run pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes following the coding standards
4. Run tests and linting: `uvx ruff check --fix && uvx ruff format`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📚 Documentation

- [Architecture Guide](docs/architecture.md) - Detailed system design
- [API Reference](docs/api.md) - Complete API documentation
- [Development Guide](docs/development.md) - Setup and contribution guide

## 🏆 Acknowledgments

- Built with [LangChain](https://github.com/hwchase17/langchain) for LLM integration
- Uses [Tavily](https://tavily.com/) for web search capabilities
- Vector storage powered by [Pinecone](https://www.pinecone.io/)
- Project management with [uv](https://github.com/astral-sh/uv)

---

**Built with ❤️ for autonomous research and knowledge discovery**
