# Project Brief: AI Research Agent

## Project Overview
This is an autonomous AI-powered research agent that performs deep, multi-step research on complex topics and generates comprehensive reports with verifiable citations. It serves as a personal project to understand how deep research agents work, utilizing different AI systems for planning and building.

## Core Purpose
Build a sophisticated research agent that can:
- Conduct thorough, autonomous research across multiple sources
- Generate comprehensive reports with proper citations
- Handle complex, multi-step research workflows
- Provide verifiable and reliable research outputs

## Key Requirements

### Functional Requirements
1. **Autonomous Research Capability**
   - Perform deep research on complex topics
   - Multi-step research workflows
   - Cross-reference multiple sources
   - Handle both web sources and PDF documents

2. **Report Generation**
   - Comprehensive research reports
   - Proper citation management
   - Executive summaries and detailed findings
   - Multiple export formats (Markdown, text)

3. **Reliability & Verifiability**
   - All claims must be backed by citations
   - Source tracking and bibliography generation
   - Transparent research methodology
   - Error handling and graceful degradation

### Technical Requirements
1. **Modular Architecture**
   - Clean separation of concerns
   - SOLID principles compliance
   - Independent, testable components
   - Pluggable tool system

2. **State Management**
   - Finite state machine for predictable behavior
   - Observable state transitions
   - Error recovery mechanisms
   - Pause/resume capabilities

3. **Memory Systems**
   - Short-term working memory for current tasks
   - Long-term persistent storage for knowledge
   - Semantic search capabilities
   - Memory statistics and management

4. **Reasoning Frameworks**
   - ReAct (Reason + Act) for linear tasks
   - Tree of Thoughts for complex analysis
   - Automatic strategy selection
   - Hybrid reasoning approaches

## Success Criteria
- Agent successfully completes research queries end-to-end
- Generated reports meet academic standards for citations
- System maintains state consistency across workflows
- All tools integrate seamlessly with the agent
- Memory systems provide useful context for future research
- Code follows established quality standards and patterns

## Project Constraints
- Python 3.11+ using modern tooling (uv, ruff)
- API-dependent (OpenAI, Tavily, optional Pinecone)
- Single-agent architecture (no multi-agent coordination)
- Command-line interface primary (no web UI)

## Target Users
- Researchers needing comprehensive topic analysis
- Students conducting literature reviews
- Analysts requiring multi-source synthesis
- Anyone needing thorough, cited research reports

This project demonstrates advanced agent design patterns including state machines, hybrid reasoning, hierarchical memory, and tool orchestration in a real-world research application.
