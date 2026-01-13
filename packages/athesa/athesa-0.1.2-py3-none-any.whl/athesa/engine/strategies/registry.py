"""Detection strategy registry factory

Centralizes strategy registration.
Follows Open/Closed principle.
"""

from typing import Dict
from ...core.screen import DetectionStrategy
from .protocol import ScreenDetectionStrategy
from .implementations import (
    VisibleAndEnabledStrategy,
    PresenceOnlyStrategy,
    CustomStrategy,
)


def create_detection_strategy_registry() -> Dict[DetectionStrategy, ScreenDetectionStrategy]:
    """
    Create detection strategy registry.
    
    Maps each DetectionStrategy enum to its implementation.
    This is the only place that needs to change when adding new strategies.
    
    Returns:
        Dictionary mapping DetectionStrategy enum to strategy instance
        
    Example:
        registry = create_detection_strategy_registry()
        strategy = registry[DetectionStrategy.VISIBLE_AND_ENABLED]
        is_present = strategy.is_present(bridge, selector)
    """
    return {
        DetectionStrategy.VISIBLE_AND_ENABLED: VisibleAndEnabledStrategy(),
        DetectionStrategy.PRESENCE_ONLY: PresenceOnlyStrategy(),
        DetectionStrategy.CUSTOM: CustomStrategy(),
    }
