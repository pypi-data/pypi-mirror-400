"""Core protocol definitions"""

from .process import ProcessProtocol
from .state import StateProtocol
from .handler import HandlerProtocol
from .screen import ScreenDefinition, DetectionStrategy
from .action import Action, ActionSequence, ActionCommand
from .context import ProcessContext
from .bridge import BridgeProtocol

__all__ = [
    "ProcessProtocol",
    "StateProtocol",
    "HandlerProtocol",
    "BridgeProtocol",
    "ScreenDefinition",
    "DetectionStrategy",
    "Action",
    "ActionSequence",
    "ActionCommand",
    "ProcessContext",
]
