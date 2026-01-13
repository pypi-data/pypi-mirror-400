"""
Athesa - State-driven web automation framework

A protocol-oriented framework for building maintainable web automation processes
using state machines, screen detection, and declarative action sequences.
"""

__version__ = "0.1.0"
__author__ = "Athesa Contributors"
__license__ = "MIT"

from .core.process import ProcessProtocol
from .core.state import StateProtocol
from .core.handler import HandlerProtocol
from .core.screen import ScreenDefinition, DetectionStrategy
from .core.action import Action, ActionSequence, ActionCommand
from .core.context import ProcessContext
from .core.bridge import BridgeProtocol

from .engine.state_machine import StateMachine
from .engine.process_runner import ProcessRunner
from .engine.page_detector import PageDetector
from .engine.action_executor import ActionExecutor

from .events.emitter import EventEmitter
from .events.callbacks import ProcessCallbacks

from .factory.registry import ProcessRegistry, registry

__all__ = [
    # Core protocols
    "ProcessProtocol",
    "StateProtocol",
    "HandlerProtocol",
    "BridgeProtocol",
    
    # Core types
    "ScreenDefinition",
    "DetectionStrategy",
    "Action",
    "ActionSequence",
    "ActionCommand",
    "ProcessContext",
    
    # Engine
    "StateMachine",
    "ProcessRunner",
    "PageDetector",
    "ActionExecutor",
    
    # Events
    "EventEmitter",
    "ProcessCallbacks",
    
    # Factory
    "ProcessRegistry",
    "registry",
]
