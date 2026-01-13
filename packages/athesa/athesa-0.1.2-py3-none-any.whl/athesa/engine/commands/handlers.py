"""Concrete command handler implementations

Each class handles one ActionCommand type.
Follows Single Responsibility and Open/Closed principles.
"""

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.bridge import BridgeProtocol


# Navigation Commands

class NavigateCommandHandler:
    """Handle NAVIGATE command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.navigate(params['url'])


class RefreshCommandHandler:
    """Handle REFRESH command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.refresh_page()


# Interaction Commands

class ClickCommandHandler:
    """Handle CLICK command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.click(params['selector'])


class TypeCommandHandler:
    """Handle TYPE command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.type_text(params['selector'], params['text'])


class ClearCommandHandler:
    """Handle CLEAR command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        selector = params['selector']
        # Clear by typing empty string (bridge-agnostic approach)
        bridge.type_text(selector, '')


class UploadFileCommandHandler:
    """Handle UPLOAD_FILE command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.upload_file(params['selector'], params['file_path'])


# Wait Commands

class WaitCommandHandler:
    """Handle WAIT command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        duration = params.get('duration', 1)
        time.sleep(duration)


class WaitForConditionCommandHandler:
    """Handle WAIT_FOR_CONDITION command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        condition = params['condition']
        timeout = params.get('timeout', 10)
        bridge.wait_for_condition(condition, timeout)


# JavaScript Commands

class ExecuteScriptCommandHandler:
    """Handle EXECUTE_SCRIPT command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        script = params['script']
        args = params.get('args', ())
        bridge.execute_script(script, *args)


# Window/Tab Management Commands

class SwitchWindowCommandHandler:
    """Handle SWITCH_WINDOW command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.switch_to_window(params['handle'])


class CloseWindowCommandHandler:
    """Handle CLOSE_WINDOW command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.close_current_window()


class OpenNewTabCommandHandler:
    """Handle OPEN_NEW_TAB command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.execute_script("window.open('', '_blank');")


# Frame Management Commands

class SwitchToFrameCommandHandler:
    """Handle SWITCH_TO_FRAME command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.switch_to_frame(params['frame'])


class SwitchToDefaultCommandHandler:
    """Handle SWITCH_TO_DEFAULT command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        bridge.switch_to_default_content()


# Custom Commands

class CustomCommandHandler:
    """Handle CUSTOM command"""
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        custom_fn = params.get('callable')
        if not custom_fn:
            raise ValueError("CUSTOM action requires 'callable' in params")
        custom_fn(bridge)
