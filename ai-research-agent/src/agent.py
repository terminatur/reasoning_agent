"""
File: src/agent.py
Purpose: Main research agent class that orchestrates the complete research workflow using FSM-based state management
Functionality: Coordinates planning, execution, synthesis, and memory management with state-driven behavior
Update Trigger: When agent behavior changes, new states are added, or workflow coordination is modified
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from .config import config
from .models import AgentState, AgentContext, ResearchReport, ToolResult
from .state_machine import state_machine
from .components import ResearchPlanner, PlanExecutor, ResearchSynthesizer
from .memory import MemoryManager
from .tools import tool_registry

class ResearchAgent:
    """
    Autonomous AI Research Agent that performs deep, multi-step research.
    Uses finite state machine for predictable, observable behavior.
    """
    
    def __init__(self):
        # Initialize context and state
        self.context = AgentContext()
        
        # Initialize components
        self.planner = ResearchPlanner()
        self.executor = PlanExecutor()
        self.synthesizer = ResearchSynthesizer()
        self.memory = MemoryManager()
        
        # Validate configuration
        try:
            config.validate_required_keys()
            print("Configuration validated successfully")
        except ValueError as e:
            print(f"Configuration warning: {e}")
        
        print("ResearchAgent initialized successfully")
        self._log_system_status()
    
    def research(self, query: str, strategy: str = "decomposition_first") -> ResearchReport:
        """
        Conduct comprehensive research on the given query.
        
        Args:
            query: Research question or topic to investigate
            strategy: Planning strategy ("decomposition_first" or "interleaved")
        
        Returns:
            ResearchReport with findings, analysis, and citations
        """
        print(f"\n🔬 Starting research: {query}")
        print(f"Strategy: {strategy}")
        
        # Initialize research context
        self.context.query = query
        self.memory.add_conversation_message("user", query)
        
        try:
            # Execute research workflow using state machine
            report = self._execute_research_workflow(strategy)
            
            # Store final report in long-term memory
            self.memory.store_research_report(report)
            
            print("✅ Research completed successfully")
            return report
            
        except Exception as e:
            # Transition to error state
            state_machine.transition(self.context, AgentState.ERROR, f"Research failed: {e}")
            print(f"❌ Research failed: {e}")
            
            # Create error report
            error_report = ResearchReport(
                query=query,
                executive_summary=f"Research failed due to error: {str(e)}",
                detailed_findings="Unable to complete research due to system error.",
                conclusions="Research could not be completed successfully.",
                citations=[],
                methodology="Research workflow interrupted by error",
                limitations="Complete failure - no findings available"
            )
            return error_report
    
    def _execute_research_workflow(self, strategy: str) -> ResearchReport:
        """Execute the complete research workflow using state machine."""
        
        # State: PLANNING
        state_machine.transition(self.context, AgentState.PLANNING, "Starting research planning")
        plan = self.planner.generate_plan(
            query=self.context.query,
            strategy=strategy,
            context=self.memory.get_context_window(),
            available_tools=tool_registry.get_tool_names()
        )
        
        self.context.plan = plan
        self.memory.update_plan(plan)
        
        print(f"📋 Generated plan with {len(plan.steps)} steps")
        print(self.planner.get_plan_summary(plan))
        
        # State: EXECUTING
        state_machine.transition(self.context, AgentState.EXECUTING, "Starting plan execution")
        
        execution_results = []
        completed_step_numbers = []
        
        while True:
            # Get next executable step
            next_step = self.planner.get_next_executable_step(plan)
            
            if not next_step:
                print("✅ All plan steps completed")
                break
            
            # Validate dependencies
            if not self.executor.validate_step_dependencies(next_step, completed_step_numbers):
                print(f"⚠️ Dependencies not met for step {next_step.step_number}")
                break
            
            # Update current step
            self.context.current_step = next_step.step_number
            
            # Execute step
            result = self.executor.execute_step(
                step=next_step,
                context=self.context,
                available_tools=tool_registry.get_tool_names()
            )
            
            # Record result
            execution_results.append(result)
            self.context.results.append(result)
            
            # Update step status
            next_step.completed = result.success
            next_step.result = result
            
            if result.success:
                completed_step_numbers.append(next_step.step_number)
                self.memory.add_observation(
                    f"Completed step {next_step.step_number}: {next_step.task}",
                    result
                )
            else:
                self.memory.add_observation(
                    f"Failed step {next_step.step_number}: {result.error_message}",
                    result
                )
                
                # Check if we should replan
                if self.planner.should_replan(next_step, str(result.result), self.memory.get_context_window()):
                    state_machine.transition(self.context, AgentState.REPLANNING, "Replanning due to step failure")
                    
                    new_plan = self.planner.replan_from_step(
                        original_plan=plan,
                        current_step_number=next_step.step_number,
                        new_context=self.memory.get_context_window(),
                        available_tools=tool_registry.get_tool_names()
                    )
                    
                    self.context.plan = new_plan
                    plan = new_plan
                    self.memory.update_plan(new_plan)
                    
                    print(f"🔄 Replanned from step {next_step.step_number}")
                    
                    state_machine.transition(self.context, AgentState.EXECUTING, "Resuming execution with new plan")
                    continue
            
            # Check for early termination
            if self.executor.should_terminate_early(execution_results):
                print("⚠️ Early termination due to excessive failures")
                break
        
        # State: SYNTHESIZING
        state_machine.transition(self.context, AgentState.SYNTHESIZING, "Generating final report")
        
        report = self.synthesizer.generate_report(
            query=self.context.query,
            research_results=execution_results,
            context=self.memory.get_context_window(),
            report_style="comprehensive"
        )
        
        print(f"📄 Generated report with {report.word_count} words and {len(report.citations)} citations")
        
        # State: DONE
        state_machine.transition(self.context, AgentState.DONE, "Research completed successfully")
        
        return report
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and statistics."""
        return {
            "state": self.context.state.value,
            "query": self.context.query,
            "current_step": self.context.current_step,
            "plan_progress": self.memory.short_term.get_plan_progress(),
            "memory_stats": self.memory.get_memory_stats(),
            "tools_available": tool_registry.get_tool_names(),
            "last_updated": self.context.last_updated.isoformat()
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution results."""
        if not self.context.results:
            return {"message": "No execution results available"}
        
        return self.executor.get_execution_summary(self.context.results)
    
    def export_report(self, format_type: str = "markdown") -> Optional[str]:
        """Export the most recent research report."""
        # Get the last successful report from memory
        recent_reports = self.memory.long_term.get_research_reports(limit=1)
        
        if not recent_reports:
            return None
        
        # This would need to be implemented to reconstruct report from memory
        # For now, return a placeholder
        return f"Export functionality not yet implemented for format: {format_type}"
    
    def clear_session(self) -> None:
        """Clear current session data while preserving long-term memory."""
        self.context = AgentContext()
        self.memory.clear_short_term_memory(preserve_plan=False)
        state_machine.reset()
        print("Session cleared successfully")
    
    def _log_system_status(self) -> None:
        """Log system status for debugging."""
        status = {
            "tools_initialized": len(tool_registry.get_tool_names()),
            "planner_has_llm": self.planner.llm is not None,
            "synthesizer_has_llm": self.synthesizer.llm is not None,
            "memory_backend": "pinecone" if hasattr(self.memory.long_term, 'initialized') and self.memory.long_term.initialized else "local",
            "config_valid": True
        }
        
        try:
            config.validate_required_keys()
        except ValueError:
            status["config_valid"] = False
        
        print(f"System Status: {status}")
    
    def pause(self) -> bool:
        """Pause the current research process."""
        if self.context.state in [AgentState.EXECUTING, AgentState.PLANNING, AgentState.SYNTHESIZING]:
            # Save current state for resumption
            self.memory.add_conversation_message("system", f"Research paused at state: {self.context.state}")
            print(f"Research paused at state: {self.context.state}")
            return True
        return False
    
    def resume(self) -> bool:
        """Resume a paused research process."""
        if self.context.plan and self.context.state != AgentState.DONE:
            print(f"Resuming research from state: {self.context.state}")
            return True
        return False
    
    def get_plan_summary(self) -> Optional[str]:
        """Get a summary of the current research plan."""
        if self.context.plan:
            return self.planner.get_plan_summary(self.context.plan)
        return None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return tool_registry.get_tool_names()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return tool_registry.get_tool_info(tool_name)

# Create global agent instance for easy access
research_agent = ResearchAgent()
