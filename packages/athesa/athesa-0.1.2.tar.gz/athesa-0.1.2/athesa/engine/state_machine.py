"""Generic state machine for process execution"""

import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.state import StateProtocol
    from ..events.emitter import EventEmitter


class StateMachine:
    """
    Generic state machine for process workflows.
    
    Manages state transitions and emits events.
    's implementation.
    
    Example:
        from athesa.events import EventEmitter
        
        emitter = EventEmitter()
        emitter.add_listener('state_changed', lambda old, new: print(f"{old} -> {new}"))
        
        sm = StateMachine(
            initial_state=LoginInitialState,
            process_name="login_flow",
            event_emitter=emitter
        )
        
        # Transition
        sm.transition_to(UsernameState())
    """
    
    def __init__(
        self,
        initial_state: type,
        process_name: str = "unknown",
        event_emitter: Optional['EventEmitter'] = None
    ):
        """
        Initialize state machine.
        
        Args:
            initial_state: State class (not instance) to start from
            process_name: Process identifier for logging
            event_emitter: Optional event emitter for state_changed events
        """
        self._current_state: 'StateProtocol' = initial_state()
        self.process_name = process_name
        self._emitter = event_emitter
        self._logger = logging.getLogger(__name__)
        
        self._logger.info(
            f"[{self.process_name}] State machine initialized at {self._current_state.__class__.__name__}"
        )
    
    @property
    def current_state(self) -> 'StateProtocol':
        """Get current state instance"""
        return self._current_state
    
    def transition_to(self, new_state: 'StateProtocol') -> None:
        """
        Transition to a new state.
        
        Args:
            new_state: State instance (not class) to transition to
            
        Example:
            sm.transition_to(PasswordState())
        """
        old_state = self._current_state
        self._current_state = new_state
        
        old_name = old_state.__class__.__name__
        new_name = new_state.__class__.__name__
        
        self._logger.info(
            f"[{self.process_name}] Transition: {old_name} → {new_name}"
        )
        
        # Emit event
        if self._emitter:
            self._emitter.emit('state_changed', old_state, new_state)
    
    def reset(self, initial_state: type) -> None:
        """
        Reset to initial state.
        
        Args:
            initial_state: State class to reset to
        """
        self._current_state = initial_state()
        self._logger.info(
            f"[{self.process_name}] Reset to {self._current_state.__class__.__name__}"
        )
