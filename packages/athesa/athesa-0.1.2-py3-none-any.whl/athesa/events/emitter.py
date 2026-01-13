"""Event emitter system for framework observability

Pythonic event system with clear, intention-revealing names.
"""

import logging
import warnings
from typing import Callable, Dict, List, Any


class EventEmitter:
    """
    Event emitter for framework events.
    
    Pure Python callback system with clear, Pythonic naming.
    
    Example:
        emitter = EventEmitter()
        
        # Add listeners
        emitter.add_listener('state_changed', lambda old, new: print(f"{old} -> {new}"))
        emitter.add_listener('screen_detected', lambda screen: print(f"Found: {screen}"))
        
        # Emit events
        emitter.emit('state_changed', LoginState, PasswordState)
        emitter.emit('screen_detected', LoginScreens.USERNAME)
        
        # Remove listener
        callback = lambda x: print(x)
        emitter.add_listener('test', callback)
        emitter.remove_listener('test', callback)
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize event emitter.
        
        Args:
            logger: Optional logger for debug output
        """
        self._listeners: Dict[str, List[Callable]] = {}
        self._logger = logger or logging.getLogger(__name__)
    
    def add_listener(self, event: str, callback: Callable) -> None:
        """
        Register event listener.
        
        Args:
            event: Event name (e.g., 'state_changed', 'screen_detected')
            callback: Function to call when event is emitted
            
        Example:
            def on_state_change(old_state, new_state):
                print(f"Transitioned: {old_state} -> {new_state}")
            
            emitter.add_listener('state_changed', on_state_change)
        """
        if event not in self._listeners:
            self._listeners[event] = []
        
        if callback not in self._listeners[event]:
            self._listeners[event].append(callback)
            self._logger.debug(f"Registered listener for '{event}'")
    
    def add_listener_once(self, event: str, callback: Callable) -> None:
        """
        Register one-time event listener (auto-removed after first emit).
        
        Args:
            event: Event name
            callback: Function to call once
        """
        def wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            self.remove_listener(event, wrapper)
        
        self.add_listener(event, wrapper)
    
    def emit(self, event: str, *args, **kwargs) -> None:
        """
        Emit event to all registered listeners.
        
        Args:
            event: Event name
            *args: Positional arguments for listeners
            **kwargs: Keyword arguments for listeners
            
        Example:
            emitter.emit('state_changed', old_state=LoginState, new_state=PasswordState)
        """
        if event not in self._listeners:
            return
            
        self._logger.debug(f"Emitting '{event}' to {len(self._listeners[event])} listeners")
        
        for callback in self._listeners[event][:]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                self._logger.error(f"Error in event listener for '{event}': {e}", exc_info=True)
    
    def remove_listener(self, event: str, callback: Callable = None) -> None:
        """
        Remove event listener(s).
        
        Args:
            event: Event name
            callback: Specific callback to remove, or None to remove all
            
        Example:
            emitter.remove_listener('state_changed', my_callback)
            emitter.remove_listener('state_changed')
        """
        if event not in self._listeners:
            return
        
        if callback is None:
            del self._listeners[event]
            self._logger.debug(f"Removed all listeners for '{event}'")
            return
        
        if callback not in self._listeners[event]:
            return
            
        self._listeners[event].remove(callback)
        self._logger.debug(f"Removed listener for '{event}'")
        
        if not self._listeners[event]:
            del self._listeners[event]
    
    def get_listeners(self, event: str) -> List[Callable]:
        """
        Get all listeners for an event.
        
        Args:
            event: Event name
            
        Returns:
            List of registered callbacks
        """
        return self._listeners.get(event, []).copy()
    
    def get_event_names(self) -> List[str]:
        """
        Get all registered event names.
        
        Returns:
            List of event names with listeners
        """
        return list(self._listeners.keys())
    
    def count_listeners(self, event: str) -> int:
        """
        Count listeners for an event.
        
        Args:
            event: Event name
            
        Returns:
            Number of registered listeners
        """
        return len(self._listeners.get(event, []))
    
    # ==========================================
    # DEPRECATED: Backwards compatibility
    # These will be removed in v2.0
    # ==========================================
    
    def on(self, event: str, callback: Callable) -> None:
        """
        DEPRECATED: Use add_listener() instead.
        
        Register event listener (backwards compatibility).
        """
        warnings.warn(
            "EventEmitter.on() is deprecated, use add_listener() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.add_listener(event, callback)
    
    def once(self, event: str, callback: Callable) -> None:
        """
        DEPRECATED: Use add_listener_once() instead.
        
        Register one-time listener (backwards compatibility).
        """
        warnings.warn(
            "EventEmitter.once() is deprecated, use add_listener_once() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.add_listener_once(event, callback)
    
    def off(self, event: str, callback: Callable = None) -> None:
        """
        DEPRECATED: Use remove_listener() instead.
        
        Remove event listener (backwards compatibility).
        """
        warnings.warn(
            "EventEmitter.off() is deprecated, use remove_listener() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.remove_listener(event, callback)
    
    def listeners(self, event: str) -> List[Callable]:
        """
        DEPRECATED: Use get_listeners() instead.
        
        Get listeners (backwards compatibility).
        """
        warnings.warn(
            "EventEmitter.listeners() is deprecated, use get_listeners() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_listeners(event)
    
    def event_names(self) -> List[str]:
        """
        DEPRECATED: Use get_event_names() instead.
        
        Get event names (backwards compatibility).
        """
        warnings.warn(
            "EventEmitter.event_names() is deprecated, use get_event_names() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_event_names()
    
    def listener_count(self, event: str) -> int:
        """
        DEPRECATED: Use count_listeners() instead.
        
        Count listeners (backwards compatibility).
        """
        warnings.warn(
            "EventEmitter.listener_count() is deprecated, use count_listeners() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.count_listeners(event)
