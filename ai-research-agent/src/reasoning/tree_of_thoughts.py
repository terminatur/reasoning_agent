"""
File: src/reasoning/tree_of_thoughts.py
Purpose: Tree of Thoughts (ToT) framework implementation for complex multi-path reasoning
Functionality: Explores multiple reasoning paths, evaluates thought quality, and selects optimal solutions
Update Trigger: When ToT algorithms change, evaluation criteria are updated, or search strategies are modified
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional, Tuple
import json
from datetime import datetime
from dataclasses import dataclass
import heapq

try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ..config import config
from ..models import ReasoningStrategy

@dataclass
class ThoughtNode:
    """Represents a single thought in the reasoning tree."""
    id: str
    content: str
    parent_id: Optional[str]
    depth: int
    quality_score: float
    state: str  # "pending", "evaluated", "expanded", "terminal"
    children: List[str]
    metadata: Dict[str, Any]

class TreeOfThoughtsEngine:
    """
    Tree of Thoughts reasoning engine for complex problem solving.
    Explores multiple reasoning paths and selects the best solutions.
    """
    
    def __init__(self):
        self.model_name = config.get_model_config("reasoning")
        self.max_depth = 4  # Maximum depth of reasoning tree
        self.max_thoughts_per_level = 3  # Maximum thoughts to generate per level
        self.quality_threshold = 0.6  # Minimum quality score to continue
        self.llm = None
        
        if LANGCHAIN_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=config.OPENAI_API_KEY,
                    temperature=0.7  # Higher temperature for diverse thoughts
                )
            except Exception as e:
                print(f"Warning: Could not initialize LLM: {e}")
        else:
            print("Warning: LangChain not available. ToT engine will use mock responses.")
    
    def solve_problem(self, problem: str, context: str = "") -> Dict[str, Any]:
        """
        Solve a complex problem using Tree of Thoughts reasoning.
        """
        # Initialize the reasoning tree
        thought_tree = {}
        solution_candidates = []
        
        # Create root thought
        root_id = "root"
        root_thought = ThoughtNode(
            id=root_id,
            content=f"Problem: {problem}",
            parent_id=None,
            depth=0,
            quality_score=1.0,
            state="expanded",
            children=[],
            metadata={"context": context}
        )
        thought_tree[root_id] = root_thought
        
        # Breadth-first search through the thought space
        current_level = [root_id]
        
        for depth in range(1, self.max_depth + 1):
            next_level = []
            
            for parent_id in current_level:
                parent_thought = thought_tree[parent_id]
                
                # Generate child thoughts
                child_thoughts = self._generate_thoughts(
                    parent_thought, problem, context, thought_tree
                )
                
                # Evaluate each child thought
                for child_thought in child_thoughts:
                    child_id = f"thought_{len(thought_tree)}"
                    child_thought.id = child_id
                    child_thought.parent_id = parent_id
                    child_thought.depth = depth
                    
                    # Evaluate thought quality
                    quality_score = self._evaluate_thought(
                        child_thought, problem, context, thought_tree
                    )
                    child_thought.quality_score = quality_score
                    
                    # Add to tree
                    thought_tree[child_id] = child_thought
                    parent_thought.children.append(child_id)
                    
                    # Check if this is a potential solution
                    if self._is_solution_candidate(child_thought, problem):
                        solution_candidates.append(child_id)
                    
                    # Add to next level if quality is good enough
                    if quality_score >= self.quality_threshold and depth < self.max_depth:
                        next_level.append(child_id)
            
            # Prune: keep only the best thoughts for next level
            if len(next_level) > self.max_thoughts_per_level:
                next_level = self._select_best_thoughts(next_level, thought_tree)
            
            current_level = next_level
            
            # Early termination if we have good solutions
            if len(solution_candidates) >= 2:
                break
        
        # Select the best solution
        best_solution = self._select_best_solution(
            solution_candidates, thought_tree, problem
        )
        
        return {
            "problem": problem,
            "solution": best_solution,
            "thought_tree": self._serialize_tree(thought_tree),
            "reasoning_strategy": ReasoningStrategy.TREE_OF_THOUGHTS,
            "total_thoughts": len(thought_tree),
            "solution_candidates": len(solution_candidates)
        }
    
    def _generate_thoughts(
        self, 
        parent_thought: ThoughtNode, 
        problem: str, 
        context: str,
        thought_tree: Dict[str, ThoughtNode]
    ) -> List[ThoughtNode]:
        """Generate multiple child thoughts from a parent thought."""
        if not self.llm:
            # Mock thought generation
            return [
                ThoughtNode(
                    id="", content=f"Mock thought {i} for: {parent_thought.content[:50]}...",
                    parent_id="", depth=0, quality_score=0.7,
                    state="pending", children=[], metadata={}
                )
                for i in range(2)
            ]
        
        try:
            prompt = self._create_thought_generation_prompt(
                parent_thought, problem, context, thought_tree
            )
            response = self.llm.invoke(prompt)
            return self._parse_thought_response(response.content)
        except Exception as e:
            print(f"Error generating thoughts: {e}")
            return []
    
    def _evaluate_thought(
        self,
        thought: ThoughtNode,
        problem: str,
        context: str,
        thought_tree: Dict[str, ThoughtNode]
    ) -> float:
        """Evaluate the quality of a thought."""
        if not self.llm:
            # Mock evaluation based on content length and keywords
            content = thought.content.lower()
            score = 0.5
            
            # Boost score for solution-oriented content
            if any(word in content for word in ["solution", "answer", "conclusion", "result"]):
                score += 0.2
            
            # Boost score for specific, detailed content
            if len(content.split()) > 10:
                score += 0.1
            
            return min(score, 1.0)
        
        try:
            prompt = self._create_evaluation_prompt(thought, problem, context)
            response = self.llm.invoke(prompt)
            return self._parse_evaluation_response(response.content)
        except Exception as e:
            print(f"Error evaluating thought: {e}")
            return 0.5
    
    def _is_solution_candidate(self, thought: ThoughtNode, problem: str) -> bool:
        """Check if a thought is a potential solution to the problem."""
        content = thought.content.lower()
        solution_indicators = [
            "solution", "answer", "conclusion", "result", "therefore",
            "in summary", "final", "complete", "solved"
        ]
        
        return any(indicator in content for indicator in solution_indicators)
    
    def _select_best_thoughts(
        self, 
        thought_ids: List[str], 
        thought_tree: Dict[str, ThoughtNode]
    ) -> List[str]:
        """Select the best thoughts based on quality scores."""
        scored_thoughts = [
            (thought_tree[tid].quality_score, tid) for tid in thought_ids
        ]
        scored_thoughts.sort(reverse=True)
        
        return [tid for _, tid in scored_thoughts[:self.max_thoughts_per_level]]
    
    def _select_best_solution(
        self,
        solution_candidates: List[str],
        thought_tree: Dict[str, ThoughtNode],
        problem: str
    ) -> Dict[str, Any]:
        """Select the best solution from candidates."""
        if not solution_candidates:
            # No explicit solutions found, use the highest quality leaf node
            leaf_nodes = [
                thought for thought in thought_tree.values()
                if not thought.children and thought.depth > 0
            ]
            if leaf_nodes:
                best_leaf = max(leaf_nodes, key=lambda t: t.quality_score)
                return {
                    "content": best_leaf.content,
                    "quality_score": best_leaf.quality_score,
                    "reasoning_path": self._get_reasoning_path(best_leaf.id, thought_tree),
                    "type": "leaf_node"
                }
            else:
                return {
                    "content": "No solution found",
                    "quality_score": 0.0,
                    "reasoning_path": [],
                    "type": "no_solution"
                }
        
        # Select the best solution candidate
        best_candidate_id = max(
            solution_candidates,
            key=lambda cid: thought_tree[cid].quality_score
        )
        best_thought = thought_tree[best_candidate_id]
        
        return {
            "content": best_thought.content,
            "quality_score": best_thought.quality_score,
            "reasoning_path": self._get_reasoning_path(best_candidate_id, thought_tree),
            "type": "solution_candidate"
        }
    
    def _get_reasoning_path(
        self, 
        thought_id: str, 
        thought_tree: Dict[str, ThoughtNode]
    ) -> List[Dict[str, Any]]:
        """Get the reasoning path from root to a given thought."""
        path = []
        current_id = thought_id
        
        while current_id and current_id in thought_tree:
            thought = thought_tree[current_id]
            path.append({
                "id": thought.id,
                "content": thought.content,
                "depth": thought.depth,
                "quality_score": thought.quality_score
            })
            current_id = thought.parent_id
        
        return list(reversed(path))
    
    def _serialize_tree(self, thought_tree: Dict[str, ThoughtNode]) -> Dict[str, Any]:
        """Serialize the thought tree for output."""
        return {
            thought_id: {
                "content": thought.content,
                "parent_id": thought.parent_id,
                "depth": thought.depth,
                "quality_score": thought.quality_score,
                "state": thought.state,
                "children": thought.children
            }
            for thought_id, thought in thought_tree.items()
        }
    
    def _create_thought_generation_prompt(
        self,
        parent_thought: ThoughtNode,
        problem: str,
        context: str,
        thought_tree: Dict[str, ThoughtNode]
    ) -> str:
        """Create prompt for generating new thoughts."""
        reasoning_path = self._get_reasoning_path(parent_thought.id, thought_tree)
        path_text = " -> ".join([step["content"][:50] + "..." for step in reasoning_path])
        
        prompt = f"""You are exploring different approaches to solve this problem using Tree of Thoughts reasoning.

Problem: {problem}
Context: {context}

Current reasoning path: {path_text}

Current thought: {parent_thought.content}

Generate 2-3 distinct next thoughts that could help solve this problem. Each thought should:
1. Be a logical next step from the current thought
2. Explore a different angle or approach
3. Be specific and actionable

Format your response as:
THOUGHT1: [your first thought]
THOUGHT2: [your second thought]
THOUGHT3: [your third thought] (optional)

Your thoughts:"""
        
        return prompt
    
    def _create_evaluation_prompt(
        self,
        thought: ThoughtNode,
        problem: str,
        context: str
    ) -> str:
        """Create prompt for evaluating thought quality."""
        prompt = f"""Evaluate the quality of this thought for solving the given problem.

Problem: {problem}
Context: {context}
Thought to evaluate: {thought.content}

Rate this thought on a scale of 0.0 to 1.0 based on:
- Relevance to the problem (0-0.3)
- Logical reasoning quality (0-0.3)
- Potential to lead to a solution (0-0.4)

Provide only a single number between 0.0 and 1.0.

Quality score:"""
        
        return prompt
    
    def _parse_thought_response(self, response: str) -> List[ThoughtNode]:
        """Parse LLM response into thought nodes."""
        thoughts = []
        lines = response.strip().split('\n')
        
        for line in lines:
            if line.startswith('THOUGHT'):
                # Extract thought content
                if ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        thoughts.append(ThoughtNode(
                            id="", content=content, parent_id="", depth=0,
                            quality_score=0.0, state="pending", children=[], metadata={}
                        ))
        
        return thoughts
    
    def _parse_evaluation_response(self, response: str) -> float:
        """Parse evaluation response to extract quality score."""
        try:
            # Look for a number in the response
            import re
            numbers = re.findall(r'0?\.\d+|1\.0|0', response)
            if numbers:
                score = float(numbers[0])
                return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except ValueError:
            pass
        
        return 0.5  # Default score if parsing fails
    
    def get_reasoning_summary(self, tot_result: Dict[str, Any]) -> str:
        """Generate a summary of the Tree of Thoughts reasoning."""
        solution = tot_result.get("solution", {})
        reasoning_path = solution.get("reasoning_path", [])
        
        summary = f"Tree of Thoughts reasoning explored {tot_result.get('total_thoughts', 0)} thoughts.\n"
        summary += f"Found {tot_result.get('solution_candidates', 0)} solution candidates.\n"
        summary += f"Best solution quality: {solution.get('quality_score', 0):.2f}\n\n"
        
        if reasoning_path:
            summary += "Reasoning path:\n"
            for i, step in enumerate(reasoning_path):
                summary += f"{i}: {step['content'][:100]}...\n"
        
        summary += f"\nFinal solution: {solution.get('content', 'No solution')[:200]}..."
        return summary
