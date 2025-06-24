"""
File: src/state_machine.py
Purpose: Finite State Machine implementation for managing agent lifecycle and state transitions
Functionality: Defines valid state transitions, handles state validation, and provides observable agent behavior
Update Trigger: When new states are added, transition rules change, or state validation logic is modified
Last Modified: 2024-06-24
"""
from typing import Dict, List, Optional, Set
from enum import Enum

from .models import AgentState, AgentContext

class StateTransition:
    """Represents a valid state transition with optional conditions."""
    
    def __init__(self, from_state: AgentState, to_state: AgentState, condition: Optional[str] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
    
    def __repr__(self) -> str:
        condition_str = f" (if {self.condition})" if self.condition else ""
        return f"{self.from_state} -> {self.to_state}{condition_str}"

class ResearchAgentStateMachine:
    """
    Finite State Machine for the Research Agent.
    Ensures predictable, robust, and observable behavior.
    """
    
    def __init__(self):
        self.valid_transitions = self._define_transitions()
        self.transition_history: List[AgentState] = []
        
    def _define_transitions(self) -> Dict[AgentState, Set[AgentState]]:
        """Define all valid state transitions."""
        return {
            AgentState.IDLE: {
                AgentState.PLANNING,
                AgentState.ERROR
            },
            AgentState.PLANNING: {
                AgentState.EXECUTING,
                AgentState.ERROR,
                AgentState.IDLE  # Cancel planning
            },
            AgentState.EXECUTING: {
                AgentState.REPLANNING,
                AgentState.SYNTHESIZING,
                AgentState.ERROR,
                AgentState.IDLE  # Early termination
            },
            AgentState.REPLANNING: {
                AgentState.EXECUTING,
                AgentState.PLANNING,
                AgentState.ERROR,
                AgentState.IDLE  # Cancel replanning
            },
            AgentState.SYNTHESIZING: {
                AgentState.DONE,
                AgentState.ERROR,
                AgentState.EXECUTING  # Need more data
            },
            AgentState.DONE: {
                AgentState.IDLE,  # Start new research
                AgentState.PLANNING  # Continue with new query
            },
            AgentState.ERROR: {
                AgentState.IDLE,  # Reset after error
                AgentState.PLANNING,  # Retry from planning
                AgentState.EXECUTING  # Retry from execution
            }
        }
    
    def can_transition(self, from_state: AgentState, to_state: AgentState) -> bool:
        """Check if a state transition is valid."""
        return to_state in self.valid_transitions.get(from_state, set())
    
    def transition(self, context: AgentContext, new_state: AgentState, reason: str = "") -> bool:
        """
        Attempt to transition the agent to a new state.
        Returns True if successful, False if invalid transition.
        """
        current_state = context.state
        
        # Check if transition is valid
        if not self.can_transition(current_state, new_state):
            raise ValueError(
                f"Invalid transition from {current_state} to {new_state}. "
                f"Valid transitions from {current_state}: {self.valid_transitions.get(current_state, set())}"
            )
        
        # Record transition
        self.transition_history.append(new_state)
        
        # Update context
        old_state = context.state
        context.state = new_state
        context.update_timestamp()
        
        print(f"State transition: {old_state} -> {new_state}" + (f" ({reason})" if reason else ""))
        
        return True
    
    def get_valid_transitions(self, current_state: AgentState) -> Set[AgentState]:
        """Get all valid transitions from the current state."""
        return self.valid_transitions.get(current_state, set())
    
    def get_transition_history(self) -> List[AgentState]:
        """Get the history of state transitions."""
        return self.transition_history.copy()
    
    def reset(self) -> None:
        """Reset the state machine to initial state."""
        self.transition_history.clear()
    
    def is_terminal_state(self, state: AgentState) -> bool:
        """Check if the given state is a terminal state."""
        terminal_states = {AgentState.DONE, AgentState.ERROR}
        return state in terminal_states
    
    def is_active_state(self, state: AgentState) -> bool:
        """Check if the agent is actively working (not idle, done, or error)."""
        active_states = {
            AgentState.PLANNING,
            AgentState.EXECUTING,
            AgentState.REPLANNING,
            AgentState.SYNTHESIZING
        }
        return state in active_states
    
    def validate_state_sequence(self, states: List[AgentState]) -> bool:
        """Validate that a sequence of states represents valid transitions."""
        if not states:
            return True
        
        for i in range(len(states) - 1):
            if not self.can_transition(states[i], states[i + 1]):
                return False
        
        return True
    
    def suggest_recovery_transitions(self, error_state: AgentState) -> List[AgentState]:
        """Suggest possible recovery transitions from an error state."""
        if error_state != AgentState.ERROR:
            return []
        
        # Common recovery patterns
        recovery_options = [
            AgentState.IDLE,      # Complete reset
            AgentState.PLANNING,  # Retry planning
            AgentState.EXECUTING  # Retry execution
        ]
        
        return [state for state in recovery_options if self.can_transition(error_state, state)]

# Global state machine instance
state_machine = ResearchAgentStateMachine()
