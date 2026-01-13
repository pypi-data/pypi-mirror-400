"""Handler protocol definition"""

from typing import Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from .context import ProcessContext
    from .action import ActionSequence


@runtime_checkable
class HandlerProtocol(Protocol):
    """
    Protocol for screen handlers.
    
    A Handler defines what actions to perform when a specific screen is detected.
    It returns an ActionSequence containing:
    - List of actions to execute
    - Next state to transition to (optional)
    
    Example:
        class UsernameHandler:
            def create_action_sequence(self, context):
                username = context.credentials['username']
                
                return ActionSequence(
                    actions=[
                        Action(
                            command=ActionCommand.TYPE,
                            params={
                                'selector': (By.CSS, 'input[type="email"]'),
                                'text': username
                            },
                            message=f"Typing username: {username}"
                        ),
                        Action(
                            command=ActionCommand.CLICK,
                            params={'selector': (By.ID, 'next-button')},
                            message="Clicking Next"
                        ),
                    ],
                    next_state=PasswordState
                )
    """
    
    def create_action_sequence(self, context: 'ProcessContext') -> 'ActionSequence':
        """
        Generate action sequence for this screen.
        
        Called by ProcessRunner after screen is detected.
        Should return actions to perform and next state to transition to.
        
        Args:
            context: Process execution context with credentials, data, etc.
            
        Returns:
            ActionSequence with actions and optional next_state
            
        Example:
            def create_action_sequence(self, context):
                return ActionSequence(
                    actions=[
                        Action(ActionCommand.CLICK, {'selector': (By.ID, 'btn')}),
                    ],
                    next_state=NextState
                )
        """
        ...
