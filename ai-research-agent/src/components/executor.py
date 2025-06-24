"""
File: src/components/executor.py
Purpose: Plan execution component that coordinates reasoning engines and tool usage for research steps
Functionality: Executes research plan steps, manages reasoning strategy selection, and handles error recovery
Update Trigger: When execution logic changes, new reasoning strategies are added, or error handling is improved
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..models import ResearchStep, ToolResult, AgentContext, ReasoningStrategy
from ..reasoning import ReasoningManager
from ..tools import tool_registry
from ..config import config

class PlanExecutor:
    """
    Executes research plan steps using appropriate reasoning strategies and tools.
    Coordinates between reasoning engines and tool registry for optimal execution.
    """
    
    def __init__(self):
        self.reasoning_manager = ReasoningManager()
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    def execute_step(
        self, 
        step: ResearchStep, 
        context: AgentContext,
        available_tools: Optional[List[str]] = None
    ) -> ToolResult:
        """
        Execute a single research step using the appropriate reasoning strategy.
        
        Args:
            step: The research step to execute
            context: Current agent context with memory and state
            available_tools: List of available tools (defaults to all tools)
        
        Returns:
            ToolResult with execution outcome
        """
        if available_tools is None:
            available_tools = tool_registry.get_tool_names()
        
        print(f"Executing Step {step.step_number}: {step.task}")
        
        # Prepare context for reasoning
        reasoning_context = self._prepare_reasoning_context(context)
        
        # Execute with retry logic
        for attempt in range(self.max_retries):
            try:
                result = self._execute_step_with_strategy(
                    step, reasoning_context, available_tools, attempt
                )
                
                if result.success:
                    print(f"Step {step.step_number} completed successfully")
                    return result
                else:
                    print(f"Step {step.step_number} failed (attempt {attempt + 1}): {result.error_message}")
                    
                    if attempt < self.max_retries - 1:
                        print(f"Retrying step {step.step_number}...")
                        continue
                    else:
                        print(f"Step {step.step_number} failed after {self.max_retries} attempts")
                        return result
                        
            except Exception as e:
                error_msg = f"Unexpected error in step execution: {str(e)}"
                print(error_msg)
                
                if attempt < self.max_retries - 1:
                    continue
                else:
                    return ToolResult(
                        tool_name="executor",
                        success=False,
                        result="",
                        error_message=error_msg,
                        execution_time=0.0
                    )
        
        # This should not be reached, but included for completeness
        return ToolResult(
            tool_name="executor",
            success=False,
            result="",
            error_message="Execution failed after all retry attempts",
            execution_time=0.0
        )
    
    def _execute_step_with_strategy(
        self,
        step: ResearchStep,
        context: str,
        available_tools: List[str],
        attempt: int
    ) -> ToolResult:
        """Execute step using the specified reasoning strategy."""
        start_time = datetime.now()
        
        try:
            # Select reasoning strategy
            strategy = self._select_reasoning_strategy(step, attempt)
            
            # Execute reasoning
            reasoning_result = self.reasoning_manager.execute_reasoning(
                task=step.task,
                context=context,
                strategy=strategy,
                available_tools=available_tools
            )
            
            # Process reasoning result
            result = self._process_reasoning_result(step, reasoning_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                tool_name="reasoning_engine",
                success=False,
                result="",
                error_message=f"Reasoning execution failed: {str(e)}",
                execution_time=execution_time
            )
    
    def _select_reasoning_strategy(self, step: ResearchStep, attempt: int) -> str:
        """
        Select the appropriate reasoning strategy for the step.
        May adjust strategy based on retry attempts.
        """
        # Use the step's preferred strategy
        base_strategy = step.reasoning_strategy.value.lower()
        
        # On retry attempts, may switch strategies for better results
        if attempt > 0:
            if base_strategy == "react":
                # Try tree of thoughts for more thorough analysis
                return "tree_of_thoughts"
            else:
                # Fall back to react for more direct execution
                return "react"
        
        return base_strategy
    
    def _prepare_reasoning_context(self, agent_context: AgentContext) -> str:
        """Prepare context string for reasoning engines."""
        context_parts = []
        
        # Add current query
        if agent_context.query:
            context_parts.append(f"Research Query: {agent_context.query}")
        
        # Add plan information
        if agent_context.plan:
            completed_steps = sum(1 for step in agent_context.plan.steps if step.completed)
            total_steps = len(agent_context.plan.steps)
            context_parts.append(f"Progress: {completed_steps}/{total_steps} steps completed")
        
        # Add recent results
        if agent_context.results:
            context_parts.append("Recent Results:")
            for result in agent_context.results[-3:]:  # Last 3 results
                if result.success:
                    summary = str(result.result)[:200] + "..." if len(str(result.result)) > 200 else str(result.result)
                    context_parts.append(f"- {result.tool_name}: {summary}")
        
        # Add reasoning history
        if agent_context.reasoning_history:
            context_parts.append("Previous Reasoning:")
            for reasoning in agent_context.reasoning_history[-2:]:  # Last 2 reasoning steps
                context_parts.append(f"- {reasoning.get('summary', 'Previous reasoning step')}")
        
        return "\n".join(context_parts)
    
    def _process_reasoning_result(self, step: ResearchStep, reasoning_result: Dict[str, Any]) -> ToolResult:
        """Process the result from the reasoning engine into a ToolResult."""
        success = reasoning_result.get("success", False)
        
        if success:
            # Extract the final answer or result
            final_answer = reasoning_result.get("final_answer")
            if not final_answer and "solution" in reasoning_result:
                # Handle Tree of Thoughts results
                solution = reasoning_result["solution"]
                final_answer = solution.get("content", "No solution content")
            
            result_data = {
                "answer": final_answer,
                "reasoning_strategy": reasoning_result.get("reasoning_strategy"),
                "iterations": reasoning_result.get("iterations_used", 1),
                "reasoning_steps": reasoning_result.get("reasoning_steps", []),
                "metadata": {
                    "step_number": step.step_number,
                    "task": step.task,
                    "expected_output": step.expected_output
                }
            }
            
            return ToolResult(
                tool_name="reasoning_engine",
                success=True,
                result=result_data,
                error_message=None,
                execution_time=0.0,  # Will be set by caller
                metadata={"reasoning_type": reasoning_result.get("reasoning_strategy")}
            )
        else:
            error_message = reasoning_result.get("error", "Reasoning failed without specific error")
            return ToolResult(
                tool_name="reasoning_engine",
                success=False,
                result="",
                error_message=error_message,
                execution_time=0.0,  # Will be set by caller
                metadata={"step_number": step.step_number}
            )
    
    def validate_step_dependencies(self, step: ResearchStep, completed_steps: List[int]) -> bool:
        """
        Validate that all dependencies for a step have been completed.
        
        Args:
            step: The step to validate
            completed_steps: List of completed step numbers
        
        Returns:
            True if all dependencies are satisfied
        """
        return all(dep in completed_steps for dep in step.dependencies)
    
    def get_execution_summary(self, results: List[ToolResult]) -> Dict[str, Any]:
        """Generate a summary of execution results."""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        total_execution_time = sum(r.execution_time for r in results)
        
        # Analyze reasoning strategies used
        strategy_usage = {}
        for result in successful_results:
            if isinstance(result.result, dict):
                strategy = result.result.get("reasoning_strategy")
                if strategy:
                    strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
        
        return {
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "success_rate": len(successful_results) / len(results) if results else 0,
            "total_execution_time": total_execution_time,
            "average_execution_time": total_execution_time / len(results) if results else 0,
            "strategy_usage": strategy_usage,
            "error_summary": [r.error_message for r in failed_results if r.error_message]
        }
    
    def extract_key_findings(self, results: List[ToolResult]) -> List[str]:
        """Extract key findings from execution results."""
        findings = []
        
        for result in results:
            if not result.success:
                continue
                
            if isinstance(result.result, dict):
                answer = result.result.get("answer", "")
                if answer and len(answer.strip()) > 50:  # Meaningful content
                    # Extract first sentence or meaningful chunk
                    sentences = answer.split('. ')
                    if sentences:
                        finding = sentences[0]
                        if len(finding) > 200:
                            finding = finding[:200] + "..."
                        findings.append(finding)
            elif isinstance(result.result, str) and len(result.result.strip()) > 50:
                # Direct string result
                finding = result.result.strip()
                if len(finding) > 200:
                    finding = finding[:200] + "..."
                findings.append(finding)
        
        return findings
    
    def should_terminate_early(self, results: List[ToolResult], failure_threshold: float = 0.5) -> bool:
        """
        Determine if execution should terminate early due to too many failures.
        
        Args:
            results: List of execution results so far
            failure_threshold: Fraction of failures that triggers early termination
        
        Returns:
            True if execution should terminate early
        """
        if len(results) < 2:  # Need at least 2 results to evaluate
            return False
        
        failed_count = sum(1 for r in results if not r.success)
        failure_rate = failed_count / len(results)
        
        return failure_rate > failure_threshold
    
    def get_recommended_next_steps(self, current_results: List[ToolResult], remaining_steps: List[ResearchStep]) -> List[str]:
        """
        Get recommendations for next steps based on current execution results.
        """
        recommendations = []
        
        # Analyze recent failures
        recent_failures = [r for r in current_results[-3:] if not r.success]
        if len(recent_failures) >= 2:
            recommendations.append("Consider replanning due to consecutive failures")
        
        # Check for information gaps
        successful_results = [r for r in current_results if r.success]
        if len(successful_results) < len(current_results) * 0.7:  # Less than 70% success
            recommendations.append("Focus on more reliable information sources")
        
        # Analyze remaining step complexity
        complex_steps = [s for s in remaining_steps if s.reasoning_strategy == ReasoningStrategy.TREE_OF_THOUGHTS]
        if complex_steps and len(successful_results) < 2:
            recommendations.append("Gather more foundational information before complex analysis")
        
        if not recommendations:
            recommendations.append("Continue with planned execution")
        
        return recommendations
