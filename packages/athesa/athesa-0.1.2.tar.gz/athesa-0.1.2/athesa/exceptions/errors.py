"""Framework exceptions"""


class AthesaError(Exception):
    """Base exception for all Athesa errors"""
    pass


class ActionFailedException(AthesaError):
    """Raised when an action execution fails"""
    pass


class ProcessInterruptedException(AthesaError):
    """
    Raised when a global interrupt screen is detected during action execution.
    
    Attributes:
        detected_screen: The interrupt screen type that was detected
    """
    def __init__(self, detected_screen, message="Process interrupted"):
        self.detected_screen = detected_screen
        super().__init__(message)


class HandlerNotFoundError(AthesaError):
    """Raised when no handler is registered for a detected screen"""
    pass


class AutomationStoppedException(AthesaError):
    """Raised when user requests automation stop"""
    pass


class DetectionTimeoutError(AthesaError):
    """Raised when screen detection times out"""
    pass


class BridgeError(AthesaError):
    """Raised when browser bridge operation fails"""
    pass
