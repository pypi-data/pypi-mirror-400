"""Detection strategies for screen presence checking

This module implements Strategy Pattern for PageDetector.
Each DetectionStrategy enum has a corresponding concrete strategy class.
"""

from .protocol import ScreenDetectionStrategy
from .implementations import (
    VisibleAndEnabledStrategy,
    PresenceOnlyStrategy,
    CustomStrategy,
)
from .registry import create_detection_strategy_registry

__all__ = [
    'ScreenDetectionStrategy',
    'VisibleAndEnabledStrategy',
    'PresenceOnlyStrategy',
    'CustomStrategy',
    'create_detection_strategy_registry',
]
