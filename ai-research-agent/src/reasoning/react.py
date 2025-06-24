"""
File: src/reasoning/react.py
Purpose: ReAct (Reason+Act) framework implementation for grounded reasoning with external tool usage
Functionality: Implements thought-action-observation loops, handles tool execution, and maintains reasoning transparency
Update Trigger: When ReAct patterns change, tool integration is updated, or reasoning prompts are modified
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional, Tuple
import json
import re
from datetime import datetime

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ..config import config
from ..models import ToolResult, ReasoningStrategy
from ..tools import tool_registry

class ReActEngine:
    """
    ReAct (Reason + Act) reasoning engine.
    Implements the thought-action-observation loop for grounded reasoning.
    """
    
    def __init__(self):
        self.model_name = config.get_model_config("reasoning")
        self.max_iterations = config.MAX_REASONING_ITERATIONS
        self.llm = None
        
        if LANGCHAIN_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=config.OPENAI_API_KEY,
                    temperature=0.1  # Low temperature for more focused reasoning
                )
            except Exception as e:
                print(f"Warning: Could not initialize LLM: {e}")
        else:
            print("Warning: LangChain not available. ReAct engine will use mock responses.")
    
    def execute_step(self, task: str, context: str, available_tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a single ReAct step: Thought -> Action -> Observation.
        """
        if available_tools is None:
            available_tools = tool_registry.get_tool_names()
        
        # Start reasoning loop
        iteration = 0
        reasoning_history = []
        final_answer = None
        
        while iteration < self.max_iterations and not final_answer:
            iteration += 1
            
            # Step 1: Generate Thought
            thought = self._generate_thought(task, context, reasoning_history, available_tools)
            
            # Step 2: Generate Action or Final Answer
            action_result = self._generate_action(thought, task, context, available_tools)
            
            if action_result.get("is_final_answer"):
                final_answer = action_result.get("answer")
                reasoning_history.append({
                    "iteration": iteration,
                    "thought": thought,
                    "action": "Final Answer",
                    "result": final_answer
                })
                break
            
            # Step 3: Execute Action
            tool_name = action_result.get("tool_name")
            tool_params = action_result.get("parameters", {})
            
            if tool_name:
                observation = self._execute_tool(tool_name, tool_params)
            else:
                observation = "No valid action specified."
            
            # Record this reasoning step
            reasoning_history.append({
                "iteration": iteration,
                "thought": thought,
                "action": f"Used {tool_name} with params: {tool_params}",
                "observation": observation.result if isinstance(observation, ToolResult) else str(observation)
            })
            
            # Update context with new observation
            context += f"\nObservation {iteration}: {observation.result if isinstance(observation, ToolResult) else str(observation)}"
        
        # If we didn't get a final answer, generate one
        if not final_answer:
            final_answer = self._generate_final_answer(task, context, reasoning_history)
        
        return {
            "task": task,
            "final_answer": final_answer,
            "reasoning_steps": reasoning_history,
            "iterations_used": iteration,
            "success": final_answer is not None,
            "reasoning_strategy": ReasoningStrategy.REACT
        }
    
    def _generate_thought(self, task: str, context: str, history: List[Dict], available_tools: List[str]) -> str:
        """Generate a thought about what to do next."""
        if not self.llm:
            return f"I need to work on: {task}. Let me think about what information I need."
        
        try:
            prompt = self._create_thought_prompt(task, context, history, available_tools)
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating thought: {e}")
            return f"I need to approach this task: {task}"
    
    def _generate_action(self, thought: str, task: str, context: str, available_tools: List[str]) -> Dict[str, Any]:
        """Generate an action based on the current thought."""
        if not self.llm:
            # Simple mock action selection
            if "search" in task.lower():
                return {
                    "is_final_answer": False,
                    "tool_name": "web_search",
                    "parameters": {"query": task}
                }
            else:
                return {
                    "is_final_answer": True,
                    "answer": f"Mock answer for: {task}"
                }
        
        try:
            prompt = self._create_action_prompt(thought, task, context, available_tools)
            response = self.llm.invoke(prompt)
            return self._parse_action_response(response.content)
        except Exception as e:
            print(f"Error generating action: {e}")
            return {
                "is_final_answer": True,
                "answer": f"Unable to complete task due to error: {e}"
            }
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool with the given parameters."""
        try:
            return tool_registry.execute_tool(tool_name, **parameters)
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result="",
                error_message=str(e),
                execution_time=0.0
            )
    
    def _generate_final_answer(self, task: str, context: str, history: List[Dict]) -> str:
        """Generate a final answer based on all reasoning and observations."""
        if not self.llm:
            return f"Based on the available information, here's what I found about: {task}"
        
        try:
            prompt = self._create_final_answer_prompt(task, context, history)
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating final answer: {e}")
            return f"Unable to generate final answer due to error: {e}"
    
    def _create_thought_prompt(self, task: str, context: str, history: List[Dict], available_tools: List[str]) -> str:
        """Create prompt for thought generation."""
        tools_list = ", ".join(available_tools)
        
        history_text = ""
        if history:
            history_text = "\nPrevious reasoning steps:\n"
            for step in history[-3:]:  # Last 3 steps
                history_text += f"Thought: {step['thought']}\nAction: {step['action']}\nObservation: {step['observation']}\n\n"
        
        prompt = f"""You are a research agent using the ReAct (Reason+Act) framework. 

Task: {task}

Context: {context}

Available tools: {tools_list}

{history_text}

Generate your next thought about what you should do to complete this task. Be specific about what information you need or what action would be most helpful. Your thought should be focused and actionable.

Thought:"""
        
        return prompt
    
    def _create_action_prompt(self, thought: str, task: str, context: str, available_tools: List[str]) -> str:
        """Create prompt for action generation."""
        # Get tool schemas for better action generation
        tool_schemas = tool_registry.get_tool_schemas()
        schemas_text = "\n".join([f"- {schema.name}: {schema.description}" for schema in tool_schemas])
        
        prompt = f"""Based on your thought, decide on the next action. You can either:
1. Use a tool to gather more information
2. Provide a final answer if you have enough information

Task: {task}
Your thought: {thought}
Context: {context}

Available tools and their descriptions:
{schemas_text}

Respond in this exact format:
If using a tool:
ACTION: tool_name
PARAMETERS: {{"param1": "value1", "param2": "value2"}}

If providing final answer:
FINAL_ANSWER: Your complete answer here

Your response:"""
        
        return prompt
    
    def _create_final_answer_prompt(self, task: str, context: str, history: List[Dict]) -> str:
        """Create prompt for final answer generation."""
        history_summary = ""
        for step in history:
            history_summary += f"Step {step['iteration']}: {step['thought']} -> {step['action']} -> {step.get('observation', 'No observation')}\n"
        
        prompt = f"""Based on all your reasoning and observations, provide a comprehensive final answer.

Original task: {task}
Context: {context}

Your reasoning process:
{history_summary}

Provide a clear, complete answer that addresses the original task. Include any relevant information you discovered and cite sources where appropriate.

Final Answer:"""
        
        return prompt
    
    def _parse_action_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's action response."""
        response = response.strip()
        
        # Check for final answer
        if "FINAL_ANSWER:" in response:
            answer = response.split("FINAL_ANSWER:", 1)[1].strip()
            return {
                "is_final_answer": True,
                "answer": answer
            }
        
        # Parse tool action
        if "ACTION:" in response:
            try:
                lines = response.split("\n")
                action_line = next(line for line in lines if line.startswith("ACTION:"))
                tool_name = action_line.split("ACTION:", 1)[1].strip()
                
                # Find parameters
                params = {}
                param_line = next((line for line in lines if line.startswith("PARAMETERS:")), None)
                if param_line:
                    param_text = param_line.split("PARAMETERS:", 1)[1].strip()
                    try:
                        params = json.loads(param_text)
                    except json.JSONDecodeError:
                        # Try to parse simple key=value format
                        params = self._parse_simple_params(param_text)
                
                return {
                    "is_final_answer": False,
                    "tool_name": tool_name,
                    "parameters": params
                }
            except Exception as e:
                print(f"Error parsing action response: {e}")
        
        # Fallback: treat as final answer
        return {
            "is_final_answer": True,
            "answer": response
        }
    
    def _parse_simple_params(self, param_text: str) -> Dict[str, Any]:
        """Parse simple parameter format like query="search term"."""
        params = {}
        # Simple regex to extract key="value" pairs
        pattern = r'(\w+)=["\'](.*?)["\']'
        matches = re.findall(pattern, param_text)
        for key, value in matches:
            params[key] = value
        return params
    
    def get_reasoning_summary(self, reasoning_result: Dict[str, Any]) -> str:
        """Generate a summary of the reasoning process."""
        steps = reasoning_result.get("reasoning_steps", [])
        summary = f"ReAct reasoning completed in {reasoning_result.get('iterations_used', 0)} iterations:\n"
        
        for step in steps:
            summary += f"- Step {step['iteration']}: {step['thought'][:100]}...\n"
        
        summary += f"\nFinal Answer: {reasoning_result.get('final_answer', 'No answer generated')[:200]}..."
        return summary
