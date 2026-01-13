"""ProcessRunner configuration

Centralized configuration for ProcessRunner behavior.
Eliminates hard-coded values and improves testability.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProcessRunnerConfig:
    """
    Configuration for ProcessRunner execution behavior.
    
    Attributes:
        detection_timeout: Seconds to wait for screen detection
        detection_retry_timeout: Seconds to wait for retry after recovery
        enable_recovery: Whether to attempt recovery on detection failure
        max_recovery_attempts: Maximum recovery attempts per detection failure
        poll_interval: Seconds between detection checks (PageDetector)
        
    Example:
        # Default config
        config = ProcessRunnerConfig()
        
        # Custom config
        config = ProcessRunnerConfig(
            detection_timeout=30.0,
            enable_recovery=False
        )
        
        runner = ProcessRunner(process, context, bridge, config=config)
    """
    
    # Screen detection timeouts
    detection_timeout: float = 60.0
    detection_retry_timeout: float = 60.0
    
    # Recovery behavior
    enable_recovery: bool = True
    max_recovery_attempts: int = 1
    
    # Detection polling
    poll_interval: float = 0.5
    
    # Event emission (future use)
    emit_events: bool = True
    
    def __post_init__(self):
        """Validate configuration values"""
        validations = {
            'detection_timeout': (self.detection_timeout, lambda x: x > 0, 'must be positive'),
            'detection_retry_timeout': (self.detection_retry_timeout, lambda x: x > 0, 'must be positive'),
            'max_recovery_attempts': (self.max_recovery_attempts, lambda x: x >= 0, 'must be non-negative'),
            'poll_interval': (self.poll_interval, lambda x: x > 0, 'must be positive'),
        }
        
        for field_name, (value, validator, message) in validations.items():
            if not validator(value):
                raise ValueError(f"{field_name} {message}")


# Default singleton instance
DEFAULT_CONFIG = ProcessRunnerConfig()
