"""Screen detection strategy protocol"""

from typing import Protocol, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.bridge import BridgeProtocol


class ScreenDetectionStrategy(Protocol):
    """
    Protocol for screen detection strategies.
    
    Each strategy implements a different way to verify element presence.
    This follows the Strategy Pattern for clean, testable detection logic.
    
    Example:
        class VisibleAndEnabledStrategy:
            def is_present(self, bridge: BridgeProtocol, selector: tuple) -> bool:
                return bridge.is_visible(selector)
    """
    
    def is_present(self, bridge: 'BridgeProtocol', selector: Tuple[str, str]) -> bool:
        """
        Check if element matching selector is present according to strategy.
        
        Args:
            bridge: Browser automation bridge
            selector: Tuple of (by, value) e.g., (By.CSS, '#login')
            
        Returns:
            True if element is present according to this strategy
            
        Example:
            strategy = VisibleAndEnabledStrategy()
            present = strategy.is_present(bridge, ('css', '#button'))
        """
        ...
