"""Action executor - executes browser actions via bridge"""

import logging
from typing import List, Optional, Any, TYPE_CHECKING

from ..core.action import Action, ActionCommand
from ..exceptions.errors import ActionFailedException, AutomationStoppedException
from .commands import create_command_registry

if TYPE_CHECKING:
    from ..core.bridge import BridgeProtocol
    from ..events.emitter import EventEmitter


class ActionExecutor:
    """
    Executes actions via BridgeProtocol.
    
    Maps ActionCommand to bridge method calls using Command Pattern.
    Handles errors and event emission.
    """
    
    def __init__(
        self,
        bridge: 'BridgeProtocol',
        event_emitter: Optional['EventEmitter'] = None,
        pause_event: Optional[Any] = None,
        stop_event: Optional[Any] = None
    ):
        """
        Initialize action executor.
        
        Args:
            bridge: Browser automation bridge
            event_emitter: Optional event emitter
            pause_event: Optional pause event
            stop_event: Optional stop event
        """
        self.bridge = bridge
        self._emitter = event_emitter
        self._pause_event = pause_event
        self._stop_event = stop_event
        self._logger = logging.getLogger(__name__)
        
        # Initialize command registry (Command Pattern)
        self._command_registry = create_command_registry()
    
    def execute(self, action: Action) -> None:
        """
        Execute a single action.
        
        Args:
            action: Action to execute
            
        Raises:
            ActionFailedException: If execution fails
            AutomationStoppedException: If user requests stop
        """
        self._check_pause_and_stop()
        
        # Emit pre-execution event
        if self._emitter:
            self._emitter.emit('action_executing', action)
        
        if action.message:
            self._logger.info(f"Action: {action.message}")
        
        try:
            self._execute_command(action.command, action.params)
            
            # Emit post-execution event
            if self._emitter:
                self._emitter.emit('action_executed', action)
        
        except Exception as e:
            self._logger.error(f"Action failed: {action.command.name} - {e}")
            
            if self._emitter:
                self._emitter.emit('action_failed', action, e)
            
            raise ActionFailedException(f"{action.command.name} failed: {e}") from e
    
    def execute_sequence(self, actions: List[Action]) -> None:
        """
        Execute a sequence of actions.
        
        Args:
            actions: List of actions to execute
        """
        for action in actions:
            self.execute(action)
    
    def _execute_command(self, command: ActionCommand, params: dict) -> None:
        """
        Execute specific command via bridge.
        
        Uses Command Pattern with handler registry for clean, extensible design.
        
        Args:
            command: Action command type
            params: Command parameters
            
        Raises:
            ValueError: If command is not registered
        """
        handler = self._command_registry.get(command)
        if not handler:
            raise ValueError(f"Unknown action command: {command}")
        
        handler.execute(self.bridge, params)
    
    def _check_pause_and_stop(self) -> None:
        """Check for pause/stop requests"""
        if self._pause_event:
            self._pause_event.wait()
        
        if self._stop_event and self._stop_event.is_set():
            raise AutomationStoppedException("Action stopped by user request")
