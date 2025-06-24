"""
File: src/components/planner.py
Purpose: Task decomposition and research planning component for breaking down complex queries
Functionality: Generates hierarchical research plans, estimates task complexity, and supports dynamic replanning
Update Trigger: When planning strategies change, decomposition algorithms are updated, or plan formats are modified
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ..config import config
from ..models import ResearchPlan, ResearchStep, ReasoningStrategy
from ..tools import tool_registry

class ResearchPlanner:
    """
    Generates research plans by decomposing complex queries into manageable steps.
    Implements hierarchical planning with dynamic replanning capabilities.
    """
    
    def __init__(self):
        self.model_name = config.get_model_config("planner")
        self.max_steps = config.MAX_PLAN_STEPS
        self.llm = None
        
        if LANGCHAIN_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=config.OPENAI_API_KEY,
                    temperature=0.2  # Low temperature for consistent planning
                )
            except Exception as e:
                print(f"Warning: Could not initialize LLM for planner: {e}")
        else:
            print("Warning: LangChain not available. Planner will use template-based planning.")
    
    def generate_plan(
        self, 
        query: str, 
        strategy: str = "decomposition_first",
        context: str = "",
        available_tools: Optional[List[str]] = None
    ) -> ResearchPlan:
        """
        Generate a comprehensive research plan for the given query.
        
        Args:
            query: The research question or topic
            strategy: Planning strategy ("decomposition_first" or "interleaved")
            context: Additional context for planning
            available_tools: List of available tools for the plan
        """
        if available_tools is None:
            available_tools = tool_registry.get_tool_names()
        
        if strategy == "decomposition_first":
            return self._decomposition_first_plan(query, context, available_tools)
        elif strategy == "interleaved":
            return self._interleaved_plan(query, context, available_tools)
        else:
            # Default to decomposition first
            return self._decomposition_first_plan(query, context, available_tools)
    
    def _decomposition_first_plan(
        self, 
        query: str, 
        context: str, 
        available_tools: List[str]
    ) -> ResearchPlan:
        """
        Create a complete plan upfront using decomposition strategy.
        Best for well-defined research topics.
        """
        if self.llm:
            steps = self._generate_steps_with_llm(query, context, available_tools)
        else:
            steps = self._generate_template_steps(query, available_tools)
        
        # Validate and limit steps
        steps = steps[:self.max_steps]
        
        # Estimate duration
        estimated_duration = self._estimate_duration(steps)
        
        return ResearchPlan(
            query=query,
            steps=steps,
            strategy="decomposition_first",
            estimated_duration=estimated_duration
        )
    
    def _interleaved_plan(
        self, 
        query: str, 
        context: str, 
        available_tools: List[str]
    ) -> ResearchPlan:
        """
        Create an initial plan with planned replanning points.
        Best for exploratory or uncertain research domains.
        """
        # Start with a basic exploration step
        initial_steps = [
            ResearchStep(
                step_number=1,
                task=f"Conduct initial web search to understand the scope of: {query}",
                reasoning_strategy=ReasoningStrategy.REACT,
                tool_name="web_search",
                expected_output="Overview of topic and key subtopics to explore",
                dependencies=[]
            ),
            ResearchStep(
                step_number=2,
                task="Analyze initial findings and determine specific research directions",
                reasoning_strategy=ReasoningStrategy.TREE_OF_THOUGHTS,
                tool_name=None,
                expected_output="Refined research plan with specific focus areas",
                dependencies=[1]
            )
        ]
        
        return ResearchPlan(
            query=query,
            steps=initial_steps,
            strategy="interleaved",
            estimated_duration=15  # Initial estimate, will be refined
        )
    
    def _generate_steps_with_llm(
        self, 
        query: str, 
        context: str, 
        available_tools: List[str]
    ) -> List[ResearchStep]:
        """Generate research steps using LLM-based planning."""
        try:
            prompt = self._create_planning_prompt(query, context, available_tools)
            response = self.llm.invoke(prompt)
            return self._parse_plan_response(response.content)
        except Exception as e:
            print(f"Error generating plan with LLM: {e}")
            return self._generate_template_steps(query, available_tools)
    
    def _generate_template_steps(self, query: str, available_tools: List[str]) -> List[ResearchStep]:
        """Generate basic research steps using templates."""
        steps = []
        
        # Step 1: Initial web search
        steps.append(ResearchStep(
            step_number=1,
            task=f"Search for current information about: {query}",
            reasoning_strategy=ReasoningStrategy.REACT,
            tool_name="web_search" if "web_search" in available_tools else None,
            expected_output="Current information and key sources on the topic",
            dependencies=[]
        ))
        
        # Step 2: Analyze findings
        steps.append(ResearchStep(
            step_number=2,
            task="Analyze initial search results and identify key themes",
            reasoning_strategy=ReasoningStrategy.REACT,
            tool_name=None,
            expected_output="Key themes and areas requiring deeper investigation",
            dependencies=[1]
        ))
        
        # Step 3: Deep dive search
        steps.append(ResearchStep(
            step_number=3,
            task="Conduct focused search on identified key themes",
            reasoning_strategy=ReasoningStrategy.REACT,
            tool_name="web_search" if "web_search" in available_tools else None,
            expected_output="Detailed information on specific aspects of the topic",
            dependencies=[2]
        ))
        
        # Step 4: Synthesis
        steps.append(ResearchStep(
            step_number=4,
            task="Synthesize all findings into comprehensive analysis",
            reasoning_strategy=ReasoningStrategy.TREE_OF_THOUGHTS,
            tool_name=None,
            expected_output="Comprehensive analysis with conclusions and insights",
            dependencies=[1, 2, 3]
        ))
        
        return steps
    
    def _create_planning_prompt(
        self, 
        query: str, 
        context: str, 
        available_tools: List[str]
    ) -> str:
        """Create prompt for LLM-based plan generation."""
        tool_descriptions = []
        for tool_name in available_tools:
            tool_info = tool_registry.get_tool_info(tool_name)
            if tool_info:
                tool_descriptions.append(f"- {tool_name}: {tool_info.get('description', 'Available tool')}")
        
        tools_text = "\n".join(tool_descriptions)
        
        prompt = f"""You are a research planning expert. Create a detailed research plan to thoroughly investigate the following query.

Research Query: {query}

Context: {context}

Available Tools:
{tools_text}

Create a research plan with 3-6 steps that will comprehensively address the query. For each step, specify:
1. A clear, actionable task description
2. The reasoning strategy to use (REACT for tool-based tasks, TREE_OF_THOUGHTS for analysis)
3. The preferred tool (if applicable)
4. Expected output from the step
5. Dependencies on previous steps (by step number)

Format your response as JSON:
{{
  "steps": [
    {{
      "step_number": 1,
      "task": "Detailed description of what to do",
      "reasoning_strategy": "REACT" or "TREE_OF_THOUGHTS",
      "tool_name": "tool_name" or null,
      "expected_output": "What this step should produce",
      "dependencies": [list of step numbers this depends on]
    }}
  ]
}}

Research Plan:"""
        
        return prompt
    
    def _parse_plan_response(self, response: str) -> List[ResearchStep]:
        """Parse LLM response into ResearchStep objects."""
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                plan_data = json.loads(json_str)
                
                steps = []
                for step_data in plan_data.get("steps", []):
                    # Map string to enum
                    reasoning_strategy = ReasoningStrategy.REACT
                    if step_data.get("reasoning_strategy") == "TREE_OF_THOUGHTS":
                        reasoning_strategy = ReasoningStrategy.TREE_OF_THOUGHTS
                    
                    step = ResearchStep(
                        step_number=step_data.get("step_number", len(steps) + 1),
                        task=step_data.get("task", ""),
                        reasoning_strategy=reasoning_strategy,
                        tool_name=step_data.get("tool_name"),
                        expected_output=step_data.get("expected_output", ""),
                        dependencies=step_data.get("dependencies", [])
                    )
                    steps.append(step)
                
                return steps
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing plan response: {e}")
        
        # Fallback to template-based planning
        return []
    
    def _estimate_duration(self, steps: List[ResearchStep]) -> int:
        """Estimate total duration for the research plan in minutes."""
        base_time_per_step = 5  # Base 5 minutes per step
        tool_time_multiplier = {
            "web_search": 2,     # 2x base time
            "pdf_parser": 3,     # 3x base time
            "data_analyzer": 2   # 2x base time
        }
        
        total_minutes = 0
        for step in steps:
            step_time = base_time_per_step
            
            if step.tool_name:
                multiplier = tool_time_multiplier.get(step.tool_name, 1)
                step_time *= multiplier
            
            if step.reasoning_strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
                step_time *= 1.5  # ToT takes longer
            
            total_minutes += step_time
        
        return int(total_minutes)
    
    def should_replan(self, current_step: ResearchStep, observation: str, context: str) -> bool:
        """
        Determine if the current plan should be modified based on new observations.
        """
        # Simple heuristics for replanning triggers
        replanning_triggers = [
            "no results found",
            "error",
            "insufficient information",
            "unexpected findings",
            "contradictory information",
            "access denied",
            "not available"
        ]
        
        observation_lower = observation.lower()
        
        # Check for explicit failure indicators
        for trigger in replanning_triggers:
            if trigger in observation_lower:
                return True
        
        # Check for very short responses (might indicate poor results)
        if len(observation.strip()) < 50:
            return True
        
        return False
    
    def replan_from_step(
        self, 
        original_plan: ResearchPlan, 
        current_step_number: int,
        new_context: str,
        available_tools: Optional[List[str]] = None
    ) -> ResearchPlan:
        """
        Generate a new plan starting from a specific step based on new information.
        """
        if available_tools is None:
            available_tools = tool_registry.get_tool_names()
        
        # Keep completed steps
        completed_steps = [
            step for step in original_plan.steps 
            if step.step_number < current_step_number and step.completed
        ]
        
        # Generate new steps from current point
        remaining_query = f"Continue research on: {original_plan.query}"
        if self.llm:
            new_steps = self._generate_steps_with_llm(remaining_query, new_context, available_tools)
        else:
            new_steps = self._generate_template_steps(remaining_query, available_tools)
        
        # Adjust step numbers
        for i, step in enumerate(new_steps):
            step.step_number = current_step_number + i
            # Update dependencies to account for completed steps
            step.dependencies = [dep for dep in step.dependencies if dep < current_step_number]
        
        all_steps = completed_steps + new_steps
        
        # Re-estimate duration for remaining work
        remaining_duration = self._estimate_duration(new_steps)
        
        return ResearchPlan(
            query=original_plan.query,
            steps=all_steps,
            strategy="replanned",
            estimated_duration=remaining_duration
        )
    
    def get_next_executable_step(self, plan: ResearchPlan) -> Optional[ResearchStep]:
        """
        Get the next step that can be executed based on dependencies.
        """
        completed_step_numbers = {
            step.step_number for step in plan.steps if step.completed
        }
        
        for step in plan.steps:
            if not step.completed:
                # Check if all dependencies are satisfied
                dependencies_satisfied = all(
                    dep in completed_step_numbers for dep in step.dependencies
                )
                if dependencies_satisfied:
                    return step
        
        return None
    
    def get_plan_summary(self, plan: ResearchPlan) -> str:
        """Generate a human-readable summary of the research plan."""
        summary = f"Research Plan for: {plan.query}\n"
        summary += f"Strategy: {plan.strategy}\n"
        summary += f"Estimated Duration: {plan.estimated_duration} minutes\n"
        summary += f"Total Steps: {len(plan.steps)}\n\n"
        
        for step in plan.steps:
            status = "✓" if step.completed else "○"
            deps = f" (depends on: {', '.join(map(str, step.dependencies))})" if step.dependencies else ""
            summary += f"{status} Step {step.step_number}: {step.task}{deps}\n"
        
        return summary
