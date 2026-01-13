"""State protocol definition"""

from typing import Protocol, List, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from .context import ProcessContext


@runtime_checkable
class StateProtocol(Protocol):
    """
    Protocol for process states.
    
    A State represents a step in the workflow. Each state knows:
    - What screens to expect
    - How to handle them (via process registry)
    - What to do if detection fails
    
    Example:
        class UsernameState:
            def handle(self, context):
                # State-specific logic can go here
                # Or just let ProcessRunner handle screen detection
                pass
            
            def get_expected_screens(self):
                return [
                    GoogleLoginScreens.USERNAME,
                    GoogleLoginScreens.ERROR,
                    GoogleLoginScreens.WRONG_USERNAME,
                ]
            
            def on_detection_failed(self, context):
                # Custom failure handling
                context.transition_to(LoginFailureState())
    """
    
    def handle(self, context: 'ProcessContext') -> None:
        """
        Main state logic.
        
        Called by ProcessRunner when entering this state.
        Typically just returns to let ProcessRunner handle screen detection,
        but can contain custom logic if needed.
        
        Args:
            context: Process execution context
        """
        ...
    
    def get_expected_screens(self) -> List[type]:
        """
        Screen types this state anticipates.
        
        ProcessRunner uses this list to detect which screen appeared.
        Order matters: first match wins.
        
        Returns:
            List of screen type enums
            
        Example:
            [
                LoginScreens.USERNAME,
                LoginScreens.ERROR,
                LoginScreens.ALREADY_LOGGED_IN,
            ]
        """
        ...
    
    def on_detection_failed(self, context: 'ProcessContext') -> None:
        """
        Called when expected screens are not detected within timeout.
        
        Default behavior (if not overridden): transition to failure state.
        Override this to customize failure handling.
        
        Args:
            context: Process execution context
            
        Example:
            def on_detection_failed(self, context):
                logging.error("Login screen not found")
                context.transition_to(LoginFailureState())
        """
        ...
