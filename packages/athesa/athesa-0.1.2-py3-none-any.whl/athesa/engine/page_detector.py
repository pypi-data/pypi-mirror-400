"""Page detector - identifies current screen state"""

import logging
import time
from typing import List, Optional, Any, TYPE_CHECKING

from ..core.screen import ScreenDefinition, DetectionStrategy
from ..exceptions.errors import AutomationStoppedException
from .strategies import create_detection_strategy_registry

if TYPE_CHECKING:
    from ..core.bridge import BridgeProtocol
    from ..events.emitter import EventEmitter


class PageDetector:
    """
    Detects which screen is currently displayed.
    
    Uses ScreenDefinition list to identify page state via selectors and verification criteria.
    Employs Strategy Pattern for different detection approaches.
    Handles global interrupts and timeout detection.
    """
    
    def __init__(
        self,
        bridge: 'BridgeProtocol',
        process_screens: List[ScreenDefinition],
        global_interrupts: List[Any] = None,
        event_emitter: Optional['EventEmitter'] = None,
        pause_event: Optional[Any] = None,
        stop_event: Optional[Any] = None
    ):
        """
        Initialize page detector.
        
        Args:
            bridge: Browser automation bridge
            process_screens: All screen definitions for this process
            global_interrupts: Screen types that can appear at any time
            event_emitter: Optional event emitter
            pause_event: Optional threading.Event for pause
            stop_event: Optional threading.Event for stop
        """
        self.bridge = bridge
        self.process_screens = process_screens
        self._global_interrupts = global_interrupts or []
        self._emitter = event_emitter
        self._pause_event = pause_event
        self._stop_event = stop_event
        self._poll_interval = 0.5  # Check every 500ms
        self._logger = logging.getLogger(__name__)
        
        # Initialize detection strategy registry (Strategy Pattern)
        self._strategy_registry = create_detection_strategy_registry()
    
    def wait_for_screen(
        self,
        expected_types: List[Any],
        timeout: float = 60
    ) -> Optional[Any]:
        """
        Wait for one of the expected screens to appear.
        
        Args:
            expected_types: List of screen types to wait for
            timeout: Maximum seconds to wait
            
        Returns:
            Detected screen type, or None if timeout
            
        Example:
            detected = detector.wait_for_screen(
                [LoginScreens.USERNAME, LoginScreens.ERROR],
                timeout=30
            )
            if detected == LoginScreens.USERNAME:
                # Handle username screen
        """
        end_time = time.monotonic() + timeout
        
        while time.monotonic() < end_time:
            # Check pause/stop
            self._check_pause_and_stop()
            
            # Try to detect screen
            detected = self._detect_screen(expected_types)
            if detected:
                self._logger.info(f"Screen detected: {detected}")
                
                if self._emitter:
                    self._emitter.emit('screen_detected', detected)
                
                return detected
            
            # Sleep before next check
            remaining = max(0.0, end_time - time.monotonic())
            time.sleep(min(self._poll_interval, remaining))
        
        # Timeout
        self._logger.warning(
            f"Detection timeout ({timeout}s). Expected: {[str(t) for t in expected_types]}"
        )
        
        if self._emitter:
            self._emitter.emit('detection_timeout', expected_types)
        
        return None
    
    def detect_immediate(self, expected_types: List[Any]) -> Optional[Any]:
        """
        Immediately check for screens without waiting.
        
        Args:
            expected_types: List of screen types to check
            
        Returns:
            Detected screen type, or None
        """
        return self._detect_screen(expected_types)
    
    def _detect_screen(self, expected_types: List[Any]) -> Optional[Any]:
        """
        Try to detect one of the expected screens.
        
        Args:
            expected_types: List of screen types to detect
            
        Returns:
            Detected screen type, or None
        """
        # Get screen definitions for expected types
        screens_to_check = [
            screen for screen in self.process_screens
            if screen.type in expected_types
        ]
        
        for screen in screens_to_check:
            if self._is_screen_present(screen):
                return screen.type
        
        return None
    
    def _is_screen_present(self, screen: ScreenDefinition) -> bool:
        """
        Check if a specific screen is present.
        
        Uses Strategy Pattern to select appropriate detection method.
        
        Args:
            screen: Screen definition to check
            
        Returns:
            True if screen matches criteria
        """
        # Get strategy for this screen's detection approach
        strategy = self._strategy_registry[screen.detection_strategy]
        element_present = strategy.is_present(self.bridge, screen.selector)
        
        if not element_present:
            return False
        
        # Check verification criteria (if any)
        if screen.verification_criteria:
            return self._check_criteria(screen.verification_criteria)
        
        return True
    
    def _check_criteria(self, criteria: List) -> bool:
        """
        Check all verification criteria.
        
        Args:
            criteria: List of lambda functions
            
        Returns:
            True if all criteria pass
        """
        # Get raw driver for lambdas (assumes bridge has .driver attribute)
        driver = getattr(self.bridge, 'driver', None)
        if not driver:
            self._logger.warning("Bridge has no 'driver' attribute, skipping criteria checks")
            return True
        
        for criterion in criteria:
            try:
                if not criterion(driver):
                    return False
            except Exception as e:
                self._logger.debug(f"Criterion check failed: {e}")
                return False
        
        return True
    
    def _check_pause_and_stop(self) -> None:
        """Check for pause/stop requests"""
        if self._pause_event:
            self._pause_event.wait()
        
        if self._stop_event and self._stop_event.is_set():
            raise AutomationStoppedException("Detection stopped by user request")
