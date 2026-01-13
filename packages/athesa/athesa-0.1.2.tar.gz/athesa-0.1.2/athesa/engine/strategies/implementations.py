"""Concrete detection strategy implementations

Each class implements one detection strategy.
"""

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.bridge import BridgeProtocol


class VisibleAndEnabledStrategy:
    """
    Strategy: Element must be visible and interactable.
    
    Default strategy for most UI interactions.
    Uses bridge.is_visible() which typically checks:
    - Element exists in DOM
    - Element is displayed (not hidden)
    - Element is enabled (not disabled)
    """
    
    def is_present(self, bridge: 'BridgeProtocol', selector: Tuple[str, str]) -> bool:
        """Check if element is visible and enabled"""
        return bridge.is_visible(selector)


class PresenceOnlyStrategy:
    """
    Strategy: Element just needs to exist in DOM.
    
    Useful for:
    - Hidden elements you want to detect
    - Elements that load before becoming visible
    - Background checking without interaction requirement
    """
    
    def is_present(self, bridge: 'BridgeProtocol', selector: Tuple[str, str]) -> bool:
        """Check if element exists in DOM (may be hidden)"""
        return bridge.is_existing(selector)


class CustomStrategy:
    """
    Strategy: Skip main selector check, use only verification criteria.
    
    Useful for:
    - Complex conditions not expressible with simple selectors
    - Checking multiple elements or states
    - Custom JS-based detection
    
    Note: This strategy always returns True for the main selector,
    relying entirely on verification_criteria in ScreenDefinition.
    """
    
    def is_present(self, bridge: 'BridgeProtocol', selector: Tuple[str, str]) -> bool:
        """Always returns True - relies on verification criteria"""
        return True
