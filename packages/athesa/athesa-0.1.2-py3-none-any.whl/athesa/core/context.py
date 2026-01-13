"""Process execution context"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .state import StateProtocol


class ProcessContext:
    """
    Execution context for a process run.
    
    Holds all data needed during process execution:
    - Credentials
    - Input data
    - Temporary storage
    - State transition method
    
    Example:
        context = ProcessContext(
            credentials={'username': 'user@example.com', 'password': 'secret'},
            data={'target_video': 'video.mp4', 'title': 'My Video'}
        )
        
        # Access in handlers
        username = context.credentials['username']
        video = context.data['target_video']
        
        # Store temporary data
        context.temp['channel_id'] = '12345'
    """
    
    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize process context.
        
        Args:
            credentials: Login credentials (username, password, etc.)
            data: Input data for the process
            **kwargs: Additional context data
        """
        self.credentials = credentials or {}
        self.data = data or {}
        self.temp: Dict[str, Any] = {}  # Temporary storage during execution
        self.metadata: Dict[str, Any] = kwargs
        
        # Set by ProcessRunner
        self._state_machine: Optional[Any] = None
        self._process: Optional[Any] = None
    
    def transition_to(self, new_state: 'StateProtocol') -> None:
        """
        Transition to a new state.
        
        Called by states or handlers to manually transition.
        Only works if context is bound to a ProcessRunner.
        
        Args:
            new_state: State instance to transition to
            
        Example:
            context.transition_to(PasswordState())
        """
        if self._state_machine is None:
            raise RuntimeError("Context not bound to a ProcessRunner")
        self._state_machine.transition_to(new_state)
    
    def set_state_machine(self, state_machine: Any) -> None:
        """Internal: Bind state machine (called by ProcessRunner)"""
        self._state_machine = state_machine
    
    def set_process(self, process: Any) -> None:
        """Internal: Bind process (called by ProcessRunner)"""
        self._process = process
    
    @property
    def process(self) -> Any:
        """Get current process"""
        return self._process
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from data or metadata.
        
        Args:
            key: Key to look up
            default: Default value if not found
            
        Returns:
            Value from data, metadata, or default
        """
        if key in self.data:
            return self.data[key]
        return self.metadata.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in temp storage.
        
        Args:
            key: Key to set
            value: Value to store
        """
        self.temp[key] = value
