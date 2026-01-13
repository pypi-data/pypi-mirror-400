"""Standard callback protocols for process events"""

from typing import Protocol, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.action import Action


class ProcessCallbacks(Protocol):
    """
    Standard callbacks for process lifecycle events.
    
    Implement this protocol to receive process events.
    All methods are optional - implement only what you need.
    
    Example:
        class MyProcessListener:
            def on_state_changed(self, old_state, new_state):
                print(f"State: {old_state.__class__.__name__} -> {new_state.__class__.__name__}")
            
            def on_screen_detected(self, screen_type):
                print(f"Detected: {screen_type.name}")
            
            def on_action_executed(self, action):
                if action.message:
                    print(f"Action: {action.message}")
            
            def on_process_completed(self, outcome):
                print(f"Process finished: {outcome}")
            
            def on_process_failed(self, error):
                print(f"Process failed: {error}")
        
        # Usage with EventEmitter
        listener = MyProcessListener()
        emitter = EventEmitter()
        
        emitter.add_listener('state_changed', listener.on_state_changed)
        emitter.add_listener('screen_detected', listener.on_screen_detected)
        emitter.add_listener('action_executed', listener.on_action_executed)
        emitter.add_listener('process:completed', listener.on_process_completed)
        emitter.add_listener('process:failed', listener.on_process_failed)
    """
    
    def on_state_changed(self, old_state: Any, new_state: Any) -> None:
        """
        Called when state machine transitions to new state.
        
        Args:
            old_state: Previous state instance
            new_state: New state instance
        """
        ...
    
    def on_screen_detected(self, screen_type: Any) -> None:
        """
        Called when a screen is successfully detected.
        
        Args:
            screen_type: Detected screen type (usually enum value)
        """
        ...
    
    def on_action_executing(self, action: 'Action') -> None:
        """
        Called before an action is executed.
        
        Args:
            action: Action about to be executed
        """
        ...
    
    def on_action_executed(self, action: 'Action') -> None:
        """
        Called after an action is successfully executed.
        
        Args:
            action: Action that was executed
        """
        ...
    
    def on_action_failed(self, action: 'Action', error: Exception) -> None:
        """
        Called when an action execution fails.
        
        Args:
            action: Action that failed
            error: Exception that occurred
        """
        ...
    
    def on_process_started(self, process_name: str) -> None:
        """
        Called when process execution starts.
        
        Args:
            process_name: Name of the process
        """
        ...
    
    def on_process_completed(self, outcome: str) -> None:
        """
        Called when process completes successfully.
        
        Args:
            outcome: Process outcome ('success', 'failure', 'retry')
        """
        ...
    
    def on_process_failed(self, error: Exception) -> None:
        """
        Called when process fails with unrecoverable error.
        
        Args:
            error: Exception that caused failure
        """
        ...
    
    def on_detection_timeout(self, expected_screens: list) -> None:
        """
        Called when screen detection times out.
        
        Args:
            expected_screens: List of screens that were expected
        """
        ...


# Standard event names (for consistency)
class ProcessEvents:
    """Standard event names used by Athesa framework"""
    
    # State events
    STATE_CHANGED = "state_changed"
    
    # Detection events
    SCREEN_DETECTED = "screen_detected"
    DETECTION_TIMEOUT = "detection_timeout"
    
    # Action events
    ACTION_EXECUTING = "action_executing"
    ACTION_EXECUTED = "action_executed"
    ACTION_FAILED = "action_failed"
    
    # Process events
    PROCESS_STARTED = "process:started"
    PROCESS_COMPLETED = "process:completed"
    PROCESS_FAILED = "process:failed"
