"""Events package - PyQt5 replacement"""

from .emitter import EventEmitter
from .callbacks import ProcessCallbacks

__all__ = ["EventEmitter", "ProcessCallbacks"]
