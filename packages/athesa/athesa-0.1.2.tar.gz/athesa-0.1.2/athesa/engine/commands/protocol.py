"""Command handler protocol definition"""

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.bridge import BridgeProtocol


class CommandHandler(Protocol):
    """
    Protocol for command handlers.
    
    Each handler implements a single ActionCommand's execution logic.
    This follows the Command Pattern and Single Responsibility Principle.
    
    Example:
        class ClickCommandHandler:
            def execute(self, bridge: BridgeProtocol, params: dict) -> None:
                bridge.click(params['selector'])
    """
    
    def execute(self, bridge: 'BridgeProtocol', params: dict) -> None:
        """
        Execute the command with given parameters.
        
        Args:
            bridge: Browser automation bridge
            params: Command-specific parameters
            
        Raises:
            ValueError: If required params are missing
            Exception: If bridge operation fails
        """
        ...
