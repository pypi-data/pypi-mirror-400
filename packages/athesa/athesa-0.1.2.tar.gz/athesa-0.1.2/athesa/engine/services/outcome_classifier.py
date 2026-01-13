"""Outcome classifier - classifies process final state
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.state import StateProtocol


class OutcomeClassifier:
    """
    Classifies process outcome based on final state.
    
    Determine if process succeeded, failed, or should retry.
    
    Uses protocol-based approach: checks if state has 'outcome' property,
    falls back to name-based heuristics.
    
    Example:
        classifier = OutcomeClassifier()
        outcome = classifier.classify(final_state)
        # Returns: 'success', 'failure', or 'retry'
    """
    
    def __init__(self):
        """Initialize outcome classifier."""
        self._logger = logging.getLogger(__name__)
    
    def classify(self, final_state: 'StateProtocol') -> str:
        """
        Classify final state outcome.
        
        Args:
            final_state: Process final state
            
        Returns:
            String outcome: 'success', 'failure', or 'retry'
            
        Strategy:
            1. If state has 'outcome' property, use it (explicit)
            2. Fall back to name-based heuristics (implicit)
        """
        # Strategy 1: Check if state explicitly declares outcome
        if hasattr(final_state, 'outcome'):
            outcome = final_state.outcome
            if outcome:
                self._logger.debug(f"State {final_state.__class__.__name__} declares outcome: {outcome}")
                return outcome
        
        # Strategy 2: Fall back to name-based heuristics
        return self._classify_by_name(final_state)
    
    def _classify_by_name(self, final_state: 'StateProtocol') -> str:
        """
        Classify by state class name (fallback strategy).
        
        Args:
            final_state: State to classify
            
        Returns:
            Inferred outcome based on name patterns
        """
        state_name = final_state.__class__.__name__.lower()
        
        if 'success' in state_name or 'succeed' in state_name or 'complete' in state_name:
            return 'success'
        elif 'retry' in state_name:
            return 'retry'
        else:
            # Default to failure
            return 'failure'
