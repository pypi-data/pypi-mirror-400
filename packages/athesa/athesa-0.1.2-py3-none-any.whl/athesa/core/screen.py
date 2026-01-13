"""Screen definition and detection strategies"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, List, Callable, Any, Optional


class DetectionStrategy(Enum):
    """
    How to verify an element's presence on the page.
    
    Different strategies for different scenarios:
    - VISIBLE_AND_ENABLED: Element must be visible and interactable
    - PRESENCE_ONLY: Element just needs to exist in DOM
    - CUSTOM: Use verification_criteria lambdas only
    """
    VISIBLE_AND_ENABLED = auto()  # Default: element visible and interactable
    PRESENCE_ONLY = auto()        # Element exists in DOM (may be hidden)
    CUSTOM = auto()               # Use verification_criteria only


@dataclass
class ScreenDefinition:
    """
    Defines how to identify a screen/page state.
    
    A screen is detected by:
    1. Main selector (CSS, XPath, etc.)
    2. Detection strategy (visible vs presence)
    3. Optional verification criteria (lambda checks)
    
    Attributes:
        type: Unique identifier (usually enum value)
        selector: Tuple of (by, value) e.g., (By.CSS, '#login-form')
        selector_name: Human-readable name for logging/debugging
        detection_strategy: How to verify element presence
        verification_criteria: Additional lambda checks
        metadata: Custom metadata for this screen
        
    Example:
        ScreenDefinition(
            type=LoginScreens.USERNAME,
            selector=(By.CSS, 'input[type="email"]'),
            selector_name="Email Input Field",
            detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED,
            verification_criteria=[
                lambda driver: not driver.find_elements(By.ID, 'error-message')
            ]
        )
    """
    # Required
    type: Any  # Usually Enum value
    selector: Tuple[str, str]  # (by, value) e.g., (By.CSS, '#id')
    
    # Optional
    selector_name: Optional[str] = None
    detection_strategy: DetectionStrategy = DetectionStrategy.VISIBLE_AND_ENABLED
    verification_criteria: List[Callable[[Any], bool]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Auto-generate selector_name if not provided"""
        if not self.selector_name:
            # Use type name as fallback
            if hasattr(self.type, 'name'):
                self.selector_name = self.type.name
            else:
                self.selector_name = str(self.type)
