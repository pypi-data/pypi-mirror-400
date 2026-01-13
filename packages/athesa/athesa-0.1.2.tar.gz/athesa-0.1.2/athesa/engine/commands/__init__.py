"""Command handlers for action execution

This module implements the Command Pattern for ActionExecutor.
Each ActionCommand has a dedicated handler class.
"""

from .protocol import CommandHandler
from .handlers import (
    NavigateCommandHandler,
    ClickCommandHandler,
    TypeCommandHandler,
    ClearCommandHandler,
    UploadFileCommandHandler,
    WaitCommandHandler,
    WaitForConditionCommandHandler,
    ExecuteScriptCommandHandler,
    RefreshCommandHandler,
    SwitchWindowCommandHandler,
    CloseWindowCommandHandler,
    OpenNewTabCommandHandler,
    SwitchToFrameCommandHandler,
    SwitchToDefaultCommandHandler,
    CustomCommandHandler,
)
from .registry import create_command_registry

__all__ = [
    'CommandHandler',
    'NavigateCommandHandler',
    'ClickCommandHandler',
    'TypeCommandHandler',
    'ClearCommandHandler',
    'UploadFileCommandHandler',
    'WaitCommandHandler',
    'WaitForConditionCommandHandler',
    'ExecuteScriptCommandHandler',
    'RefreshCommandHandler',
    'SwitchWindowCommandHandler',
    'CloseWindowCommandHandler',
    'OpenNewTabCommandHandler',
    'SwitchToFrameCommandHandler',
    'SwitchToDefaultCommandHandler',
    'CustomCommandHandler',
    'create_command_registry',
]
