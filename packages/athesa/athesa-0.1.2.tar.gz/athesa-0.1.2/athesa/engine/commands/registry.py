"""Command registry factory

Centralizes command handler registration.
Follows Open/Closed principle - adding new commands only requires
updating this registry, no changes to ActionExecutor.
"""

from typing import Dict
from ...core.action import ActionCommand
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


def create_command_registry() -> Dict[ActionCommand, CommandHandler]:
    """
    Create command handler registry.
    
    Maps each ActionCommand to its handler implementation.
    This is the only place that needs to change when adding new commands.
    
    Returns:
        Dictionary mapping ActionCommand enum to handler instance
        
    Example:
        registry = create_command_registry()
        handler = registry[ActionCommand.CLICK]
        handler.execute(bridge, {'selector': (By.ID, 'btn')})
    """
    return {
        # Navigation
        ActionCommand.NAVIGATE: NavigateCommandHandler(),
        ActionCommand.REFRESH: RefreshCommandHandler(),
        
        # Interactions
        ActionCommand.CLICK: ClickCommandHandler(),
        ActionCommand.TYPE: TypeCommandHandler(),
        ActionCommand.CLEAR: ClearCommandHandler(),
        ActionCommand.UPLOAD_FILE: UploadFileCommandHandler(),
        
        # Waits
        ActionCommand.WAIT: WaitCommandHandler(),
        ActionCommand.WAIT_FOR_CONDITION: WaitForConditionCommandHandler(),
        
        # JavaScript
        ActionCommand.EXECUTE_SCRIPT: ExecuteScriptCommandHandler(),
        
        # Window/Tab management
        ActionCommand.SWITCH_WINDOW: SwitchWindowCommandHandler(),
        ActionCommand.CLOSE_WINDOW: CloseWindowCommandHandler(),
        ActionCommand.OPEN_NEW_TAB: OpenNewTabCommandHandler(),
        
        # Frame management
        ActionCommand.SWITCH_TO_FRAME: SwitchToFrameCommandHandler(),
        ActionCommand.SWITCH_TO_DEFAULT: SwitchToDefaultCommandHandler(),
        
        # Custom
        ActionCommand.CUSTOM: CustomCommandHandler(),
    }
