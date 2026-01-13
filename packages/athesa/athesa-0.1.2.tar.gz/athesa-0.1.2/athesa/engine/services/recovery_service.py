"""Recovery service - handles screen detection failure recovery
"""

import logging
from typing import TYPE_CHECKING

from ...core.action import Action, ActionCommand
from ...exceptions.errors import ActionFailedException

if TYPE_CHECKING:
    from ...core.bridge import BridgeProtocol
    from ..action_executor import ActionExecutor


class RecoveryService:
    """
    Handles recovery when expected screen is not detected.
    
    Attempt to recover from detection failures
    by refreshing the page or other recovery strategies.
    
    Example:
        service = RecoveryService(bridge, action_executor)
        if service.attempt_recovery():
            # Retry detection
        else:
            # Handle failure
    """
    
    def __init__(
        self,
        bridge: 'BridgeProtocol',
        action_executor: 'ActionExecutor'
    ):
        """
        Initialize recovery service.
        
        Args:
            bridge: Browser automation bridge
            action_executor: Action executor for recovery actions
        """
        self.bridge = bridge
        self.action_executor = action_executor
        self._logger = logging.getLogger(__name__)
    
    def attempt_recovery(self) -> bool:
        """
        Attempt recovery by refreshing page.
        
        Returns:
            True if recovery action succeeded, False otherwise
            
        Note:
            Currently implements page refresh strategy.
            Can be extended with additional recovery strategies.
        """
        self._logger.warning("Expected screen not found. Attempting recovery...")
        
        try:
            # Get current URL and refresh
            current_url = self.bridge.get_current_url()
            refresh_action = Action(
                command=ActionCommand.NAVIGATE,
                params={'url': current_url},
                message="Recovery: Refreshing page"
            )
            
            self.action_executor.execute(refresh_action)
            self._logger.info("Recovery action (page refresh) succeeded")
            return True
        
        except ActionFailedException as e:
            self._logger.error(f"Recovery action failed: {e}")
            return False
