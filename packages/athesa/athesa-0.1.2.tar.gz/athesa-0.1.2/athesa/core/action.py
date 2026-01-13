"""Action definitions for browser automation"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional, List, Type, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .state import StateProtocol


class ActionCommand(Enum):
    """
    Primitive browser operations.
    
    These commands are executed by ActionExecutor via BridgeProtocol.
    """
    # Navigation
    NAVIGATE = auto()          # Navigate to URL
    REFRESH = auto()           # Refresh page
    
    # Interactions
    CLICK = auto()             # Click element
    TYPE = auto()              # Type text
    CLEAR = auto()             # Clear input field
    SELECT = auto()            # Select from dropdown
    UPLOAD_FILE = auto()       # Upload file to input[type=file]
    
    # Waits
    WAIT = auto()              # Wait for duration
    WAIT_FOR_CONDITION = auto  ()              # Wait for custom condition
    
    # JavaScript
    EXECUTE_SCRIPT = auto()    # Run JavaScript
    
    # Window/Tab management
    SWITCH_WINDOW = auto()     # Switch to window/tab
    CLOSE_WINDOW = auto()      # Close current window
    OPEN_NEW_TAB = auto()      # Open new tab
    
    # Frame management
    SWITCH_TO_FRAME = auto()   # Switch to iframe
    SWITCH_TO_DEFAULT = auto() # Switch back to main content
    
    # Custom
    CUSTOM = auto()            # User-defined custom action


@dataclass
class Action:
    """
    Single browser action.
    
    Represents one atomic operation (click, type, navigate, etc.)
    
    Attributes:
        command: Type of action to perform
        params: Parameters for the action (selector, text, url, etc.)
        message: Optional user-facing message for logging/UI
        
    Example:
        Action(
            command=ActionCommand.TYPE,
            params={
                'selector': (By.CSS, 'input[name="email"]'),
                'text': 'user@example.com'
            },
            message="Entering email address"
        )
    """
    command: ActionCommand
    params: dict
    message: Optional[str] = None


@dataclass
class ActionSequence:
    """
    Sequence of actions with optional state transition.
    
    Returned by handlers to define what to do when a screen is detected.
    
    Attributes:
        actions: List of actions to execute in order
        next_state: State class to transition to after actions (optional)
        on_success: Callback on successful execution (optional)
        on_failure: Callback on execution failure (optional)
        
    Example:
        ActionSequence(
            actions=[
                Action(ActionCommand.TYPE, {...}),
                Action(ActionCommand.CLICK, {...}),
            ],
            next_state=PasswordState
        )
    """
    actions: List[Action]
    next_state: Optional[Type['StateProtocol']] = None
    on_success: Optional[Callable] = None
    on_failure: Optional[Callable[[Exception], None]] = None
