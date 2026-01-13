"""Process protocol definition"""

from typing import Protocol, Type, Dict, List, Tuple, runtime_checkable


@runtime_checkable
class ProcessProtocol(Protocol):
    """
    Protocol for defining automation processes.
    
    A Process defines a complete workflow from start to finish, including:
    - Initial state
    - Screen-to-handler registry
    - Screen definitions
    - Final states (success/failure/retry)
    
    No inheritance required - any class implementing these properties works.
    
    Example:
        class LoginProcess:
            @property
            def name(self) -> str:
                return "login_flow"
            
            @property
            def initial_state(self):
                return LoginInitialState
            
            @property
            def registry(self):
                return {
                    LoginScreens.USERNAME: UsernameHandler(),
                    LoginScreens.PASSWORD: PasswordHandler(),
                }
            
            @property
            def screens(self):
                return [
                    ScreenDefinition(
                        type=LoginScreens.USERNAME,
                        selector=(By.CSS, 'input[type="email"]')
                    ),
                    ...
                ]
            
            @property
            def final_states(self):
                return (LoginSuccessState, LoginFailureState)
    """
    
    @property
    def name(self) -> str:
        """
        Unique process identifier.
        
        Returns:
            Process name (e.g., "google_login", "youtube_upload")
        """
        ...
    
    @property
    def initial_state(self) -> Type['StateProtocol']:
        """
        Starting state of the process.
        
        Returns:
            State class (not instance) to start from
        """
        ...
    
    @property
    def registry(self) -> Dict[type, 'HandlerProtocol']:
        """
        Mapping of screen types to their handlers.
        
        When a screen is detected, ProcessRunner looks up its handler here.
        
        Returns:
            Dictionary mapping screen enum values to handler instances
            
        Example:
            {
                GoogleLoginScreens.USERNAME: UsernameHandler(),
                GoogleLoginScreens.PASSWORD: PasswordHandler(),
            }
        """
        ...
    
    @property
    def screens(self) -> List['ScreenDefinition']:
        """
        All screens that can appear in this process.
        
        PageDetector uses these definitions to identify current page state.
        
        Returns:
            List of ScreenDefinition objects
        """
        ...
    
    @property
    def final_states(self) -> Tuple[Type['StateProtocol'], ...]:
        """
        States that mark process completion.
        
        ProcessRunner stops when current state is in this tuple.
        
        Returns:
            Tuple of state classes representing terminal states
            
        Example:
            (LoginSuccessState, LoginFailureState, LoginRetryState)
        """
        ...
    
    @property
    def global_interrupts(self) -> List[type]:
        """
        Screens that can appear at any time (optional).
        
        These are checked before state-specific screens.
        Useful for cookie consents, popups, etc.
        
        Returns:
            List of screen types that can interrupt any state
            
        Default:
            Empty list
        """
        return []
    
    def get_workflow(self) -> 'WorkflowGenerator':
        """
        Optional workflow generator (optional).
        
        If provided, yields actions before state handling.
        Useful for linear flows with some branching.
        
        Returns:
            Generator yielding Action objects, or None
            
        Default:
            None
        """
        return None


# Type alias for clarity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import StateProtocol
    from .handler import HandlerProtocol
    from .screen import ScreenDefinition
    from typing import Generator
    from .action import Action
    WorkflowGenerator = Generator[Action, None, None]
