"""
File: src/reasoning/__init__.py
Purpose: Reasoning module initialization and unified reasoning interface
Functionality: Exports reasoning engines and provides strategy selection for different types of tasks
Update Trigger: When new reasoning strategies are added or reasoning selection logic is modified
Last Modified: 2024-06-24
"""
from .react import ReActEngine
from .tree_of_thoughts import TreeOfThoughtsEngine

__all__ = ["ReActEngine", "TreeOfThoughtsEngine", "ReasoningManager"]

class ReasoningManager:
    """
    Unified reasoning management interface that coordinates different reasoning strategies.
    Automatically selects the appropriate reasoning strategy based on task complexity.
    """
    
    def __init__(self):
        self.react_engine = ReActEngine()
        self.tot_engine = TreeOfThoughtsEngine()
        
    def execute_reasoning(self, task: str, context: str = "", strategy: str = "auto", **kwargs):
        """
        Execute reasoning using the specified or automatically selected strategy.
        
        Args:
            task: The task or problem to solve
            context: Additional context for the reasoning
            strategy: "react", "tree_of_thoughts", or "auto" for automatic selection
            **kwargs: Additional parameters for specific reasoning engines
        """
        if strategy == "auto":
            strategy = self._select_strategy(task, context)
        
        if strategy == "tree_of_thoughts":
            return self._execute_tree_of_thoughts(task, context, **kwargs)
        else:
            # Default to ReAct
            return self._execute_react(task, context, **kwargs)
    
    def _select_strategy(self, task: str, context: str) -> str:
        """
        Automatically select the best reasoning strategy based on task characteristics.
        """
        task_lower = task.lower()
        
        # Use Tree of Thoughts for complex, open-ended problems
        tot_indicators = [
            "analyze", "compare", "evaluate", "complex", "multiple",
            "alternatives", "trade-offs", "pros and cons", "strategy",
            "approach", "methodology", "framework", "comprehensive"
        ]
        
        # Use ReAct for straightforward information gathering and tool-based tasks
        react_indicators = [
            "search", "find", "lookup", "get", "retrieve", "download",
            "extract", "parse", "calculate", "convert", "translate"
        ]
        
        tot_score = sum(1 for indicator in tot_indicators if indicator in task_lower)
        react_score = sum(1 for indicator in react_indicators if indicator in task_lower)
        
        # Consider context length as well
        if len(context) > 1000:  # Long context suggests complex problem
            tot_score += 1
        
        # Consider task length
        if len(task.split()) > 20:  # Long task description suggests complexity
            tot_score += 1
        
        return "tree_of_thoughts" if tot_score > react_score else "react"
    
    def _execute_react(self, task: str, context: str, **kwargs):
        """Execute ReAct reasoning."""
        available_tools = kwargs.get("available_tools")
        return self.react_engine.execute_step(task, context, available_tools)
    
    def _execute_tree_of_thoughts(self, task: str, context: str, **kwargs):
        """Execute Tree of Thoughts reasoning."""
        return self.tot_engine.solve_problem(task, context)
    
    def get_strategy_recommendation(self, task: str, context: str = "") -> dict:
        """
        Get a recommendation for which reasoning strategy to use.
        """
        recommended_strategy = self._select_strategy(task, context)
        
        task_analysis = {
            "recommended_strategy": recommended_strategy,
            "reasoning": self._explain_strategy_choice(task, context, recommended_strategy),
            "alternatives": ["react", "tree_of_thoughts"],
            "task_complexity": self._assess_task_complexity(task, context)
        }
        
        return task_analysis
    
    def _explain_strategy_choice(self, task: str, context: str, strategy: str) -> str:
        """Explain why a particular strategy was chosen."""
        if strategy == "tree_of_thoughts":
            return ("Tree of Thoughts selected due to task complexity, need for multiple "
                   "reasoning paths, or analytical nature of the problem.")
        else:
            return ("ReAct selected for straightforward task that benefits from "
                   "tool-based information gathering and step-by-step reasoning.")
    
    def _assess_task_complexity(self, task: str, context: str) -> str:
        """Assess the complexity level of the task."""
        complexity_score = 0
        
        # Task length
        if len(task.split()) > 20:
            complexity_score += 1
        
        # Context length
        if len(context) > 1000:
            complexity_score += 1
        
        # Complex keywords
        complex_keywords = [
            "analyze", "evaluate", "compare", "synthesize", "comprehensive",
            "multi-faceted", "complex", "nuanced", "trade-offs"
        ]
        complexity_score += sum(1 for keyword in complex_keywords if keyword in task.lower())
        
        if complexity_score >= 3:
            return "high"
        elif complexity_score >= 1:
            return "medium"
        else:
            return "low"
    
    def get_available_strategies(self) -> list:
        """Get list of available reasoning strategies."""
        return ["react", "tree_of_thoughts"]
    
    def get_strategy_info(self, strategy: str) -> dict:
        """Get information about a specific reasoning strategy."""
        info = {
            "react": {
                "name": "ReAct (Reason+Act)",
                "description": "Iterative reasoning with tool usage for grounded problem solving",
                "best_for": ["Information gathering", "Tool-based tasks", "Step-by-step reasoning"],
                "limitations": ["May not explore all solution paths", "Linear reasoning approach"]
            },
            "tree_of_thoughts": {
                "name": "Tree of Thoughts",
                "description": "Multi-path reasoning that explores different solution approaches",
                "best_for": ["Complex analysis", "Multiple solution paths", "Creative problem solving"],
                "limitations": ["Higher computational cost", "May be overkill for simple tasks"]
            }
        }
        
        return info.get(strategy, {"name": "Unknown", "description": "Strategy not found"})
