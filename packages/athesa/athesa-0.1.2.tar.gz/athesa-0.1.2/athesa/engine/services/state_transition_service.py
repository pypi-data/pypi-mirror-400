"""State transition service - handles state transitions

Eliminates fragile string matching for failure state detection.
"""

import logging
from typing import List, Type, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.state import StateProtocol
    from .state_machine import StateMachine


class StateTransitionService:
    """
    Handles state transitions with intelligent failure state detection.
    
    Manage state transitions, especially to failure states.
    Eliminates fragile string matching from ProcessRunner.
    
    Example:
        service = StateTransitionService(state_machine, process)
        
        # Transition to next state
        service.transition_to_next(PasswordState)
        
        # Transition to failure
        service.transition_to_failure("Login failed", final_states)
    """
    
    def __init__(
        self,
        state_machine: 'StateMachine'
    ):
        """
        Initialize state transition service.
        
        Args:
            state_machine: StateMachine instance to control
        """
        self.state_machine = state_machine
        self._logger = logging.getLogger(__name__)
    
    def transition_to_next(self, next_state: 'StateProtocol') -> None:
        """
        Transition to next state.
        
        Handles both state instances and callables.
        
        Args:
            next_state: State instance or callable that returns state instance
        """
        if callable(next_state):
            state_instance = next_state()
        else:
            state_instance = next_state
        
        self.state_machine.transition_to(state_instance)
    
    def transition_to_failure(
        self,
        reason: str,
        final_states: tuple
    ) -> None:
        """
        Transition to appropriate failure state.
        
        Strategy:
        1. Check if states have 'is_failure' property (explicit)
        2. Fall back to name matching (implicit)
        
        Args:
            reason: Reason for failure (for logging)
            final_states: Tuple of final state classes
        """
        failure_state = self._find_failure_state(final_states)
        
        if failure_state:
            self.state_machine.transition_to(failure_state())
            self._logger.error(f"Transitioned to failure state: {reason}")
        else:
            self._logger.error(f"No failure state found. Reason: {reason}")
            raise ValueError("No failure state defined in process")
    
    def _find_failure_state(self, final_states: tuple) -> Optional[Type['StateProtocol']]:
        """
        Find appropriate failure state.
        
        Strategy:
        1. Look for states with is_failure = True (explicit)
        2. Look for 'failure' or 'failed' in name (implicit)
        3. Use last final state (fallback)
        
        Args:
            final_states: Tuple of final state classes
            
        Returns:
            Failure state class or None
        """
        # Strategy 1: Explicit declaration
        for state_class in final_states:
            if hasattr(state_class, 'is_failure') and state_class.is_failure:
                return state_class
        
        # Strategy 2: Name matching (legacy support)
        failure_states = [
            s for s in final_states
            if 'failure' in s.__name__.lower() or 'failed' in s.__name__.lower()
        ]
        
        if failure_states:
            return failure_states[0]
        
        # Strategy 3: Fallback to last state
        if final_states:
            self._logger.warning(
                "No explicit failure state found, using last final state as fallback"
            )
            return final_states[-1]
        
        return None
