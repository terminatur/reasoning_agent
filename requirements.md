### `README.md` - Project Overview and Architectural Principles

# Project: Autonomous AI Research Agent

## 1\. Mandate and Core Objective

This project outlines the development of an autonomous AI Research Agent. The agent's primary goal is to perform deep, multi-step research on complex topics, moving beyond simple information retrieval to synthesize findings into a structured, comprehensive report.[1, 2] The agent will autonomously formulate plans, browse and analyze diverse online sources (text, PDFs), and generate reports with verifiable citations.[3, 4]

## 2\. Architectural Principles

The agent is built on a modular, single-agent architecture that leverages key design patterns for scalability, robustness, and observability.[5, 6]

  * **Modular Design**: The system is divided into three core modules: **Perception**, **Cognition**, and **Action**. This separation allows for independent development, testing, and maintenance of each component.[5, 7]
  * **State-Driven Operation**: The agent's lifecycle is managed by a Finite State Machine (FSM). This ensures predictable, robust, and observable behavior, preventing common issues like infinite loops and enabling features like pause/resume.[8, 9]
  * **Hierarchical Planning**: The agent uses a "divide and conquer" strategy, breaking down complex user queries into smaller, manageable sub-tasks. It can adapt its planning strategy from a full upfront plan to an interleaved, dynamic approach based on task complexity.[10, 11]
  * **Hybrid Reasoning**: The agent employs a hybrid reasoning model. For straightforward, tool-based tasks, it uses the **ReAct (Reason+Act)** framework to ground its conclusions in real-world data.[12] For complex, exploratory tasks, it switches to a **Tree of Thoughts (ToT)** framework to evaluate multiple reasoning paths simultaneously.[13, 14, 15]
  * **Hierarchical Memory**: The agent utilizes both short-term (working) memory for in-task context and a persistent long-term memory. Long-term memory is further divided into semantic (vector DB for facts), episodic (database for past experiences), and procedural (learned skills) components.[7, 16, 17, 18]
  * **Abstracted Tool Use**: Tools are integrated via a "Control Plane as a Tool" pattern. This decouples the agent's reasoning from the tool implementation, allowing for easy scaling and management of the toolset.[19]

## 3\. Project Goal

The end result will be a Python-based AI agent capable of taking a high-level research topic, conducting a thorough, multi-source investigation, and producing a well-structured, cited report.

### `requirements.txt` - Python Package Dependencies

```
# Core LLM and Agentic Frameworks
openai
langchain
langchain-openai
langgraph

# Web Search and Data Extraction
tavily-python
beautifulsoup4
requests
pypdf

# Data Analysis and Visualization
pandas
numpy
matplotlib

# Vector Database for Long-Term Memory
pinecone-client
# or weaviate-client, pymilvus, etc.

# State Management (optional, can be implemented manually)
python-statemachine

# UI (optional, for interactive demo)
streamlit
```

### Project Directory Structure

```
/ai-research-agent
|
├── main.py                 # Main entry point to run the agent
├── config.py               # API keys and configuration
├── requirements.txt        # Project dependencies
|
└───/src
|
    ├── agent.py                # Core ResearchAgent class and main loop
    ├── state_machine.py        # Finite State Machine definition
|
    ├── /components
| ├── __init__.py
| ├── planner.py            # Task decomposition and planning
| ├── executor.py           # Executes plan steps by calling tools
| └── synthesis.py          # Final report generation and analysis
|
    ├── /reasoning
| ├── __init__.py
| ├── react.py              # ReAct (Reason+Act) framework implementation
| └── tree_of_thoughts.py   # Tree of Thoughts (ToT) framework
|
    ├── /memory
| ├── __init__.py
| ├── short_term.py         # Manages working memory (context window)
| └── long_term.py          # Manages persistent memory (vector DB)
|
    └───/tools
        ├── __init__.py             # Tool registry and control plane
        ├── web_search.py         # Web search tool (e.g., Tavily)
        ├── pdf_parser.py         # PDF text extraction tool
        └── data_analyzer.py      # Code interpreter for data analysis
```

### Python Code Implementation Plan

#### `config.py`    
Of course. Here is a detailed architectural plan and a set of executable tasks, written in Python, that an AI model can use to construct a deep research agent. This plan is based on established design patterns for building robust, autonomous AI systems.

### `README.md` - Project Overview and Architectural Principles

# Project: Autonomous AI Research Agent

## 1\. Mandate and Core Objective

This project outlines the development of an autonomous AI Research Agent. The agent's primary goal is to perform deep, multi-step research on complex topics, moving beyond simple information retrieval to synthesize findings into a structured, comprehensive report.[1, 2] The agent will autonomously formulate plans, browse and analyze diverse online sources (text, PDFs), and generate reports with verifiable citations.[3, 4]

## 2\. Architectural Principles

The agent is built on a modular, single-agent architecture that leverages key design patterns for scalability, robustness, and observability.[5, 6]

  * **Modular Design**: The system is divided into three core modules: **Perception**, **Cognition**, and **Action**. This separation allows for independent development, testing, and maintenance of each component.[5, 7]
  * **State-Driven Operation**: The agent's lifecycle is managed by a Finite State Machine (FSM). This ensures predictable, robust, and observable behavior, preventing common issues like infinite loops and enabling features like pause/resume.[8, 9]
  * **Hierarchical Planning**: The agent uses a "divide and conquer" strategy, breaking down complex user queries into smaller, manageable sub-tasks. It can adapt its planning strategy from a full upfront plan to an interleaved, dynamic approach based on task complexity.[10, 11]
  * **Hybrid Reasoning**: The agent employs a hybrid reasoning model. For straightforward, tool-based tasks, it uses the **ReAct (Reason+Act)** framework to ground its conclusions in real-world data.[12] For complex, exploratory tasks, it switches to a **Tree of Thoughts (ToT)** framework to evaluate multiple reasoning paths simultaneously.[13, 14, 15]
  * **Hierarchical Memory**: The agent utilizes both short-term (working) memory for in-task context and a persistent long-term memory. Long-term memory is further divided into semantic (vector DB for facts), episodic (database for past experiences), and procedural (learned skills) components.[7, 16, 17, 18]
  * **Abstracted Tool Use**: Tools are integrated via a "Control Plane as a Tool" pattern. This decouples the agent's reasoning from the tool implementation, allowing for easy scaling and management of the toolset.[19]

## 3\. Project Goal

The end result will be a Python-based AI agent capable of taking a high-level research topic, conducting a thorough, multi-source investigation, and producing a well-structured, cited report.

### `requirements.txt` - Python Package Dependencies

```
# Core LLM and Agentic Frameworks
openai
langchain
langchain-openai
langgraph

# Web Search and Data Extraction
tavily-python
beautifulsoup4
requests
pypdf

# Data Analysis and Visualization
pandas
numpy
matplotlib

# Vector Database for Long-Term Memory
pinecone-client
# or weaviate-client, pymilvus, etc.

# State Management (optional, can be implemented manually)
python-statemachine

# UI (optional, for interactive demo)
streamlit
```

### Project Directory Structure

```
/ai-research-agent
|
├── main.py                 # Main entry point to run the agent
├── config.py               # API keys and configuration
├── requirements.txt        # Project dependencies
|
└───/src
|
    ├── agent.py                # Core ResearchAgent class and main loop
    ├── state_machine.py        # Finite State Machine definition
|
    ├── /components
| ├── __init__.py
| ├── planner.py            # Task decomposition and planning
| ├── executor.py           # Executes plan steps by calling tools
| └── synthesis.py          # Final report generation and analysis
|
    ├── /reasoning
| ├── __init__.py
| ├── react.py              # ReAct (Reason+Act) framework implementation
| └── tree_of_thoughts.py   # Tree of Thoughts (ToT) framework
|
    ├── /memory
| ├── __init__.py
| ├── short_term.py         # Manages working memory (context window)
| └── long_term.py          # Manages persistent memory (vector DB)
|
    └───/tools
        ├── __init__.py             # Tool registry and control plane
        ├── web_search.py         # Web search tool (e.g., Tavily)
        ├── pdf_parser.py         # PDF text extraction tool
        └── data_analyzer.py      # Code interpreter for data analysis
```

### Python Code Implementation Plan

#### `config.py`
Of course. Here is a detailed architectural plan and a set of executable tasks, written in Python, that an AI model can use to construct a deep research agent. This plan is based on established design patterns for building robust, autonomous AI systems.

### `README.md` - Project Overview and Architectural Principles

# Project: Autonomous AI Research Agent

## 1\. Mandate and Core Objective

This project outlines the development of an autonomous AI Research Agent. The agent's primary goal is to perform deep, multi-step research on complex topics, moving beyond simple information retrieval to synthesize findings into a structured, comprehensive report.[1, 2] The agent will autonomously formulate plans, browse and analyze diverse online sources (text, PDFs), and generate reports with verifiable citations.[3, 4]

## 2\. Architectural Principles

The agent is built on a modular, single-agent architecture that leverages key design patterns for scalability, robustness, and observability.[5, 6]

  * **Modular Design**: The system is divided into three core modules: **Perception**, **Cognition**, and **Action**. This separation allows for independent development, testing, and maintenance of each component.[5, 7]
  * **State-Driven Operation**: The agent's lifecycle is managed by a Finite State Machine (FSM). This ensures predictable, robust, and observable behavior, preventing common issues like infinite loops and enabling features like pause/resume.[8, 9]
  * **Hierarchical Planning**: The agent uses a "divide and conquer" strategy, breaking down complex user queries into smaller, manageable sub-tasks. It can adapt its planning strategy from a full upfront plan to an interleaved, dynamic approach based on task complexity.[10, 11]
  * **Hybrid Reasoning**: The agent employs a hybrid reasoning model. For straightforward, tool-based tasks, it uses the **ReAct (Reason+Act)** framework to ground its conclusions in real-world data.[12] For complex, exploratory tasks, it switches to a **Tree of Thoughts (ToT)** framework to evaluate multiple reasoning paths simultaneously.[13, 14, 15]
  * **Hierarchical Memory**: The agent utilizes both short-term (working) memory for in-task context and a persistent long-term memory. Long-term memory is further divided into semantic (vector DB for facts), episodic (database for past experiences), and procedural (learned skills) components.[7, 16, 17, 18]
  * **Abstracted Tool Use**: Tools are integrated via a "Control Plane as a Tool" pattern. This decouples the agent's reasoning from the tool implementation, allowing for easy scaling and management of the toolset.[19]

## 3\. Project Goal

The end result will be a Python-based AI agent capable of taking a high-level research topic, conducting a thorough, multi-source investigation, and producing a well-structured, cited report.

### `requirements.txt` - Python Package Dependencies

```
# Core LLM and Agentic Frameworks
openai
langchain
langchain-openai
langgraph

# Web Search and Data Extraction
tavily-python
beautifulsoup4
requests
pypdf

# Data Analysis and Visualization
pandas
numpy
matplotlib

# Vector Database for Long-Term Memory
pinecone-client
# or weaviate-client, pymilvus, etc.

# State Management (optional, can be implemented manually)
python-statemachine

# UI (optional, for interactive demo)
streamlit
```

### Project Directory Structure

```
/ai-research-agent
|
├── main.py                 # Main entry point to run the agent
├── config.py               # API keys and configuration
├── requirements.txt        # Project dependencies
|
└───/src
|
    ├── agent.py                # Core ResearchAgent class and main loop
    ├── state_machine.py        # Finite State Machine definition
|
    ├── /components
| ├── __init__.py
| ├── planner.py            # Task decomposition and planning
| ├── executor.py           # Executes plan steps by calling tools
| └── synthesis.py          # Final report generation and analysis
|
    ├── /reasoning
| ├── __init__.py
| ├── react.py              # ReAct (Reason+Act) framework implementation
| └── tree_of_thoughts.py   # Tree of Thoughts (ToT) framework
|
    ├── /memory
| ├── __init__.py
| ├── short_term.py         # Manages working memory (context window)
| └── long_term.py          # Manages persistent memory (vector DB)
|
    └───/tools
        ├── __init__.py             # Tool registry and control plane
        ├── web_search.py         # Web search tool (e.g., Tavily)
        ├── pdf_parser.py         # PDF text extraction tool
        └── data_analyzer.py      # Code interpreter for data analysis
```

### Python Code Implementation Plan

#### `config.py`
# src/config.py
```python
"""
Configuration file for API keys and other constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Model configurations
PLANNER_MODEL = "gpt-4.1-mini-2025-04-14"
EXECUTOR_MODEL = "gpt-4.1-mini-2025-04-14"
SYNTHESIS_MODEL = "gpt-4.1-mini-2025-04-14"

# Vector DB configuration
PINECONE_INDEX_NAME = "research-agent-ltm"
```

### `src/tools/__init__.py`
```python
# src/tools/__init__.py
"""
Implements the "Control Plane as a Tool" pattern.[19]
This module serves as a single entry point for the agent to access all available tools.
It decouples the agent's reasoning from the specific tool implementations,
allowing for easier scaling, maintenance, and governance.
"""
from.web_search import WebSearchTool
from.pdf_parser import PDFParserTool
from.data_analyzer import DataAnalyzerTool

class ToolRegistry:
    """A central registry to manage and dispatch tool calls."""
    def __init__(self):
        self.tools = {
            "web_search": WebSearchTool(),
            "pdf_parser": PDFParserTool(),
            "data_analyzer": DataAnalyzerTool(),
        }
        print("ToolRegistry initialized with tools:", list(self.tools.keys()))

    def get_tool_definitions(self):
        """Returns a list of tool schemas for the LLM to understand."""
        return [tool.schema for tool in self.tools.values()]

    def execute_tool(self, tool_name: str, **kwargs):
        """
        Executes a specified tool with the given arguments.
        This acts as the control plane, routing the agent's intent to the correct tool.
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        try:
            tool = self.tools[tool_name]
            # In a production system, add input validation, logging, and policy checks here.[19]
            return tool.run(**kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"

# Instantiate a single registry for the agent to use
tool_registry = ToolRegistry()
``` 

# src/components/planner.py
```python
# src/components/planner.py
"""
The Planner component is responsible for Task Decomposition.
It breaks down a high-level user query into a structured plan of sub-tasks.
This embodies the "divide and conquer" strategy.[20, 11]
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import PLANNER_MODEL, OPENAI_API_KEY

class Planner:
    """
    Generates a multi-step research plan based on the user's query.
    It can choose between a decomposition-first or interleaved approach.[11]
    """
    def __init__(self, tool_definitions):
        self.llm = ChatOpenAI(model=PLANNER_MODEL, api_key=OPENAI_API_KEY, temperature=0.0)
        self.tool_definitions = tool_definitions

    def generate_plan(self, query: str, strategy: str = "decomposition_first") -> list:
        """
        Generates a research plan.
        For complex, unpredictable tasks, an "interleaved" strategy would be used,
        where planning and execution happen in cycles.[11]
        """
        if strategy == "decomposition_first":
            return self._decomposition_first_plan(query)
        else:
            # Interleaved planning would generate one step, execute, then replan.
            # This is managed by the main agent loop.
            raise NotImplementedError("Interleaved planning strategy not yet implemented.")

    def _decomposition_first_plan(self, query: str) -> list:
        """
        Creates a complete, sequential plan before execution begins.
        Effective for well-defined tasks in stable environments.[11]
        """
        prompt_template = ChatPromptTemplate.from_messages()

        chain = prompt_template | self.llm
        response = chain.invoke({
            "query": query,
            "tools": str(self.tool_definitions)
        })

        # In a real implementation, you would parse the string response into a list of dicts.
        # For this plan, we'll assume the LLM returns a clean, parsable list.
        print(f"--- Generated Plan ---\n{response.content}\n--------------------")
        # This is a placeholder for actual parsing logic
        plan =
        return plan

    def should_replan(self, observation: str) -> bool:
        """
        Determines if the plan needs to be updated based on new information.
        This is crucial for dynamic replanning.[21, 22, 23, 24]
        """
        # Logic to analyze the observation and decide if the current plan is still valid.
        # For example, if a search returns no results or unexpected information.
        if "Error:" in observation or "No relevant results found" in observation:
            return True
        return False
```

# src/reasoning/react.py
```python
# src/reasoning/react.py
"""
Implements the ReAct (Reason + Act) framework.[12, 25]
This pattern forces the agent to interleave thought, action, and observation,
grounding its reasoning in externally retrieved information and making its process transparent.
"""
from langchain_openai import ChatOpenAI
from config import EXECUTOR_MODEL, OPENAI_API_KEY

class ReActEngine:
    """
    Executes a single task step using the Thought -> Action -> Observation loop.
    """
    def __init__(self, tool_registry):
        self.llm = ChatOpenAI(model=EXECUTOR_MODEL, api_key=OPENAI_API_KEY, temperature=0.0)
        self.tool_registry = tool_registry

    def execute_step(self, task_description: str, context: str):
        """
        Runs one cycle of the ReAct loop.
        """
        # 1. Thought: The LLM reasons about what to do next.
        thought = self._generate_thought(task_description, context)
        print(f"Thought: {thought}")

        # 2. Action: The LLM decides which tool to use and with what parameters.
        action_request = self._generate_action(thought)
        print(f"Action: {action_request}")
        # Placeholder for parsing action_request into tool_name and args
        tool_name = "web_search"
        args = {"query": task_description}

        # The agent's "hands" execute the action.
        observation = self.tool_registry.execute_tool(tool_name, **args)
        print(f"Observation: {observation}")

        return observation

    def _generate_thought(self, task, context):
        # Prompt the LLM to generate a thought based on the task and context.
        # This is the "Reason" part of ReAct.[12]
        return f"Given the task '{task}' and the context '{context}', I need to find relevant information."

    def _generate_action(self, thought):
        # Prompt the LLM to generate a tool call based on its thought.
        # This is the "Act" part of ReAct.[12]
        return f"tool_name: 'web_search', query: '...' "
```

# rc/agent.py
```python
# src/agent.py
"""
The core ResearchAgent class that orchestrates the entire process.
It manages the state, invokes the planner, executor, and synthesizer,
and handles the main operational loop.
"""
from components.planner import Planner
from reasoning.react import ReActEngine # In a full implementation, you'd also import ToTEngine
from tools import tool_registry
from memory.short_term import ShortTermMemory
from components.synthesis import Synthesizer

class ResearchAgent:
    """
    An autonomous agent that performs deep research.
    Its behavior is guided by a state machine.[8]
    """
    def __init__(self):
        self.state = "IDLE" # Initial state
        self.planner = Planner(tool_registry.get_tool_definitions())
        self.reasoning_engine = ReActEngine(tool_registry) # Could dynamically switch to ToT
        self.memory = ShortTermMemory()
        self.synthesizer = Synthesizer()
        self.plan =
        self.results =

    def run(self, query: str):
        """
        The main execution loop of the agent, modeled as a Finite State Machine (FSM).
        This provides a robust and observable structure for the agent's lifecycle.[9, 26]
        """
        print(f"Agent starting research for query: '{query}'")
        self.memory.add_message("user", query)

        # State: PLANNING
        self.state = "PLANNING"
        print(f"Agent state -> {self.state}")
        self.plan = self.planner.generate_plan(query)
        self.memory.update_plan(self.plan)

        # State: EXECUTING
        self.state = "EXECUTING"
        print(f"Agent state -> {self.state}")
        for step in self.plan:
            print(f"\nExecuting Step {step['step_number']}: {step['task']}")
            # The reasoning engine executes the task step by step.
            # For simplicity, we directly call the engine here.
            # A more complex agent would have an inner loop for multi-step reasoning per task.
            context = self.memory.get_context()
            result = self.reasoning_engine.execute_step(step['task'], context)
            self.results.append(result)
            self.memory.add_message("assistant", f"Result for step {step['step_number']}: {result}")

            # Dynamic Replanning Check [21, 22]
            if self.planner.should_replan(result):
                print("Replanning triggered by new observation...")
                self.state = "REPLANNING"
                # In a full implementation, this would regenerate the plan from the current step.
                # For now, we'll just log it.
                print("Replanning logic would execute here.")
                self.state = "EXECUTING"


        # State: SYNTHESIZING
        self.state = "SYNTHESIZING"
        print(f"\nAgent state -> {self.state}")
        final_report = self.synthesizer.generate_report(query, self.results)
        print("\n--- FINAL REPORT ---")
        print(final_report)
        print("--------------------")

        # State: DONE
        self.state = "DONE"
        print(f"\nAgent state -> {self.state}")
        return final_report
```

# main.py
```python
# main.py
"""
Main entry point for the AI Research Agent.
"""
from ai_research_agent.agent import ResearchAgent

def main():
    """
    Initializes and runs the research agent.
    """
    # Example user query
    user_query = "Analyze the impact of generative AI on the software development lifecycle, focusing on recent trends and challenges."

    # Create an instance of the agent
    agent = ResearchAgent()

    # Run the research process
    final_report = agent.run(user_query)

    # The final report is returned
    # In a real application, this could be saved to a file or displayed in a UI.

if __name__ == "__main__":
    main()
```