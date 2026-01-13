"""Process execution coordinator - orchestrates process execution
"""

import logging
from typing import Optional, TYPE_CHECKING, List

from ...exceptions.errors import ActionFailedException, ProcessInterruptedException, HandlerNotFoundError

if TYPE_CHECKING:
    from ..state_machine import StateMachine
    from ..page_detector import PageDetector
    from ..action_executor import ActionExecutor
    from .recovery_service import RecoveryService
    from .outcome_classifier import OutcomeClassifier
    from .state_transition_service import StateTransitionService
    from ...core.process import ProcessProtocol
    from ...core.context import ProcessContext
    from ...core.action import Action
    from ..process_runner_config import ProcessRunnerConfig


class ProcessExecutionCoordinator:
    """
    Coordinates process execution workflow.

    Example:
        coordinator = ProcessExecutionCoordinator(
            state_machine, page_detector, action_executor,
            recovery_service, outcome_classifier, transition_service,
            process, context, config, emitter, logger
        )
        outcome = coordinator.execute()
    """
    
    def __init__(
        self,
        state_machine: 'StateMachine',
        page_detector: 'PageDetector',
        action_executor: 'ActionExecutor',
        recovery_service: 'RecoveryService',
        outcome_classifier: 'OutcomeClassifier',
        transition_service: 'StateTransitionService',
        process: 'ProcessProtocol',
        context: 'ProcessContext',
        config: 'ProcessRunnerConfig',
        event_emitter: Optional[any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize execution coordinator with all dependencies"""
        self.state_machine = state_machine
        self.page_detector = page_detector
        self.action_executor = action_executor
        self.recovery_service = recovery_service
        self.outcome_classifier = outcome_classifier
        self.transition_service = transition_service
        self.process = process
        self.context = context
        self.config = config
        self._emitter = event_emitter
        self._logger = logger or logging.getLogger(__name__)
        
        # Extract pause/stop from context
        self._pause_event = getattr(context, 'pause_event', None)
        self._stop_event = getattr(context, 'stop_event', None)
    
    def execute(self) -> str:
        """
        Execute the complete process workflow.
        
        Returns:
            Outcome string: 'success', 'failure', or 'retry'
            
        Raises:
            AutomationStoppedException: If user requests stop
        """
        # Emit start event
        if self._emitter:
            self._emitter.emit('process:started', self.process.name)
        
        self._logger.info(f"Starting process: {self.process.name}")
        
        try:
            # Execute initial workflow
            self._execute_workflow()
            
            # Main execution loop
            outcome = self._execute_main_loop()
            
            self._logger.info(f"Process finished with outcome: {outcome}")
            
            if self._emitter:
                self._emitter.emit('process:completed', outcome)
            
            return outcome
        
        except Exception as e:
            self._logger.error(f"Process failed with error: {e}", exc_info=True)
            
            if self._emitter:
                self._emitter.emit('process:failed', e)
            
            raise
    
    def _execute_workflow(self) -> None:
        """Execute initial workflow actions if provided"""
        workflow = self.process.get_workflow()
        if not workflow:
            return
        
        self._logger.info("Executing initial workflow actions")
        
        try:
            for action in workflow:
                self._check_pause_and_stop()
                self.action_executor.execute(action)
        except ActionFailedException as e:
            self._logger.error(f"Initial workflow failed: {e}")
            self.transition_service.transition_to_failure(
                f"Initial workflow failed: {e}",
                self.process.final_states
            )
            raise
    
    def _execute_main_loop(self) -> str:
        """
        Execute main detection and handling loop.
        
        Returns:
            Outcome string after completion
        """
        while not self._is_finished():
            self._check_pause_and_stop()
            
            # Execute one screen detection/handling cycle
            if not self._execute_screen_cycle():
                # Cycle failed, but state might have transitioned
                continue
        
        # Process finished - classify outcome
        return self.outcome_classifier.classify(self.state_machine.current_state)
    
    def _execute_screen_cycle(self) -> bool:
        """
        Execute one screen detection and handling cycle.
        
        Returns:
            True if cycle succeeded, False if detection failed
        """
        # Get expected screens
        current_state = self.state_machine.current_state
        expected_screens = self._get_expected_screens(current_state)
        
        # Detect screen
        detected = self._detect_screen_with_recovery(expected_screens)
        
        if detected is None:
            # Detection failed even after recovery
            self._handle_detection_failure(current_state)
            return False
        
        # Execute handler for detected screen
        self._execute_handler(detected)
        return True
    
    def _get_expected_screens(self, current_state) -> List:
        """Get combined list of expected screens (state + global)"""
        state_screens = current_state.get_expected_screens()
        global_screens = self.process.global_interrupts
        
        # Combine, preserving order and removing duplicates
        return list(dict.fromkeys(state_screens + global_screens))
    
    def _detect_screen_with_recovery(self, expected_screens: List) -> Optional[any]:
        """
        Detect screen with optional recovery attempt.
        
        Returns:
            Detected screen type or None
        """
        detected = self.page_detector.wait_for_screen(
            expected_screens,
            timeout=self.config.detection_timeout
        )
        
        if detected is None and self.config.enable_recovery:
            # Try recovery
            if self.recovery_service.attempt_recovery():
                detected = self.page_detector.wait_for_screen(
                    expected_screens,
                    timeout=self.config.detection_retry_timeout
                )
        
        return detected
    
    def _execute_handler(self, detected_screen: any) -> None:
        """
        Execute handler for detected screen.
        
        Args:
            detected_screen: Screen type that was detected
        """
        # Get handler
        handler = self.process.registry.get(detected_screen)
        if not handler:
            raise HandlerNotFoundError(
                f"No handler registered for screen: {detected_screen}"
            )
        
        # Execute handler
        try:
            sequence = handler.create_action_sequence(self.context)
            
            # Execute actions
            for action in sequence.actions:
                self._check_pause_and_stop()
                self.action_executor.execute(action)
            
            # Transition to next state
            if sequence.next_state:
                self.transition_service.transition_to_next(sequence.next_state)
            
            # Call success callback
            if sequence.on_success:
                sequence.on_success()
        
        except ProcessInterruptedException as e:
            self._logger.warning(
                f"Process interrupted by screen: {e.detected_screen}"
            )
            self._handle_interrupt(e)
        
        except ActionFailedException as e:
            self._logger.error(f"Action failed: {e}")
            self.transition_service.transition_to_failure(
                str(e),
                self.process.final_states
            )
            raise
    
    def _handle_detection_failure(self, current_state) -> None:
        """Handle screen detection timeout"""
        # Let state handle failure
        current_state.on_detection_failed(self.context)
        
        # If state didn't transition, force failure
        if self.state_machine.current_state == current_state:
            self._logger.warning("State did not handle detection failure, forcing failure transition")
            self.transition_service.transition_to_failure(
                "Screen detection timeout",
                self.process.final_states
            )
    
    def _handle_interrupt(self, exception: ProcessInterruptedException) -> None:
        """Handle process interruption by global interrupt screen"""
        handler = self.process.registry.get(exception.detected_screen)
        
        if handler:
            sequence = handler.create_action_sequence(self.context)
            self.transition_service.transition_to_next(sequence.next_state)
        else:
            self.transition_service.transition_to_failure(
                f"Interrupt: {exception.detected_screen}",
                self.process.final_states
            )
    
    def _is_finished(self) -> bool:
        """Check if process has reached a final state"""
        return isinstance(self.state_machine.current_state, self.process.final_states)
    
    def _check_pause_and_stop(self) -> None:
        """Check for pause/stop requests"""
        if self._pause_event:
            self._pause_event.wait()
        
        if self._stop_event and self._stop_event.is_set():
            from ...exceptions.errors import AutomationStoppedException
            raise AutomationStoppedException("Process stopped by user request")
