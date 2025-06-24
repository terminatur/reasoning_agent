# 🔬 AI Research Agent

An autonomous AI-powered research agent that performs deep, multi-step research on complex topics and generates comprehensive reports with verifiable citations.

This is a personal project in an attempt to understand how deep research agents work.

Different AI systems were used in the planning and building of this agent.

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
# Change working directory
cd ai-research-agent

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
   ModuleNotFoundError: No module named 'ai_research_agent'
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

## Current status:

This agent does infact work. However, there are some existing issues. Results from first query `Research Query: How is Ai being used in healthcare?`

```markdown
📄 **Executive Summary:**
This research report investigates how artificial intelligence (AI) is currently being utilized in healthcare, with the objective of providing a comprehensive overview of AI applications, adoption trends, benefits, challenges, and future directions based on recent (2023–2024) academic and industry sources. The study synthesizes data from structured datasets, market reports, case studies, and expert analyses to capture the evolving landscape of AI integration across clinical and operational domains.

Key findings reveal that AI is rapidly transforming healthcare through diverse applications such as predictive analytics, diagnostic enhancement, personalized treatment, and automation of routine tasks. AI-powered predictive models analyze patient data to forecast disease progression and optimize treatment plans, while diagnostic tools leveraging image recognition improve accuracy and speed in radiology, pathology, and other specialties. Additionally, AI automates administrative workflows, enabling clinicians to focus more on patient care. Adoption rates are highest in medical imaging, with approximately 90% of healthcare organizations employing AI tools, though patient and clinician acceptance varies.

The most important insights highlight AI’s dual impact on improving clinical outcomes and operational efficiency. AI-driven diagnostics and precision medicine contribute to earlier disease detection and tailored therapies, enhancing patient care quality. Meanwhile, automation reduces clinician workload and healthcare costs. However, challenges remain, including cautious patient attitudes toward AI-driven diagnoses and the need for regulatory frameworks to ensure ethical and safe AI deployment.

Implications of these findings suggest that AI will continue to play a pivotal role in shaping the future of healthcare by enabling more proactive, personalized, and efficient care delivery. Healthcare providers and policymakers must address adoption barriers, foster trust through transparency, and invest in AI literacy and infrastructure to fully realize AI’s transformative potential. Continued research and collaboration across stakeholders will be essential to navigate ethical considerations and optimize AI integration for improved health outcomes.

🔍 **Key Findings:**
## Findings

This section presents a comprehensive synthesis of current research and data on the use of artificial intelligence (AI) in healthcare, organized by key thematic areas: applications, adoption and impact, benefits, challenges, and future directions. The findings draw primarily from recent (2023–2024) market reports, academic whitepapers, industry analyses, and case studies, including insights from Grand View Research, Medwave, Statista, and TempDev.

---

### 1. Key Applications of AI...

💡 **Conclusions:**
**Conclusions**

This research has demonstrated that artificial intelligence (AI) is playing an increasingly transformative role in healthcare as of 2024, with widespread adoption across clinical, operational, and administrative domains. The key findings reveal that AI applications are diverse and impactful, primarily encompassing predictive analytics, diagnostic enhancement, personalized treatment, and workflow automation. These technologies leverage vast datasets—including electronic health records, medical imaging, and genomics—to improve accuracy, efficiency, and patient outcomes.

In addressing the original research question, it is clear that AI is being used not only to augment clinical decision-making through improved diagnostics and risk prediction but also to streamline healthcare delivery by automating routine tasks such as scheduling and documentation. The integration of AI into precision medicine enables tailored therapies based on individual patient profiles, marking a significant advancement toward personalized care.

Several patterns and trends emerge from the analysis. Imaging and radiology remain the leading sectors for AI adoption, with a high percentage of healthcare organizations implementing AI tools. While clinicians generally recognize the benefits of AI in reducing administrative burdens, patient acceptance of AI-driven diagnostics is more cautious, highlighting a gap between technological capability and user trust. Additionally, AI’s role in predictive analytics is expanding, facilitating proactive interventions and resource optimization.

The implications of these findings are multifaceted. AI has the potential to enhance healthcare quality and accessibility, reduce costs, and alleviate clinician workload. However, challenges such as ethical considerations, data privacy, algorithmic transparency, and patient trust must be addressed to ensure responsible and equitable AI deployment. Furthermore, the mixed attitudes among healthcare providers and patients underscore the need for education and transparent communication about AI’s capabilities and limitations.

Future research should focus on longitudinal studies to assess the long-term clinical and economic impacts of AI integration, strategies to improve patient and provider acceptance, and the development of robust frameworks for ethical AI governance. Investigating AI’s role in underserved populations and low-resource settings could also provide valuable insights into reducing healthcare disparities. Lastly, continuous evaluation of AI algorithms for bias and accuracy will be essential to maintain safety and efficacy as these technologies evolve.

In summary, AI is rapidly reshaping healthcare by enhancing diagnostics, personalizing treatment, and optimizing operations. While promising, its full potential will be realized only through careful management of technical, ethical, and social challenges, supported by ongoing research and stakeholder engagement.

📚 **Citations:** 0 sources

📈 **Report Statistics:**
  - Word Count: 1602
  - Generated: 2025-06-24 17:29:13
  - Methodology: This research employed the following methodology:

1. Multi-source information gathering and analysi...
  - Steps Executed: 4
  - Success Rate: 100.0%
  - Total Time: 183.1s
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
