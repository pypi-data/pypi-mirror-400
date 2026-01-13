"""Process runner - executes processes from start to finish"""

import logging
from typing import Optional, TYPE_CHECKING

from .process_runner_config import ProcessRunnerConfig, DEFAULT_CONFIG
from .services import (
    RecoveryService,
    OutcomeClassifier,
    StateTransitionService,
    ProcessExecutionCoordinator
)

if TYPE_CHECKING:
    from ..core.process import ProcessProtocol
    from ..core.context import ProcessContext
    from ..core.bridge import BridgeProtocol
    from ..events.emitter import EventEmitter


class ProcessRunner:
    """
    Executes a process from start to finish.
    
    Refactored to follow SOLID principles:
    - Constructor: Dependency injection (no component creation)
    - Execution: Delegated to ProcessExecutionCoordinator
    - Configuration: ProcessRunnerConfig for all settings
    
    Example:
        from athesa import ProcessRunner, ProcessContext
        from athesa.adapters.selenium import SeleniumBridge
        
        # Setup
        bridge = SeleniumBridge(driver)
        process = MyLoginProcess()
        context = ProcessContext(credentials={'username': 'test'})
        
        # Run with defaults
        runner = ProcessRunner(process, context, bridge)
        outcome = runner.run()
        
        # Run with custom config
        from athesa.engine import ProcessRunnerConfig
        config = ProcessRunnerConfig(detection_timeout=30.0)
        runner = ProcessRunner(process, context, bridge, config=config)
        outcome = runner.run()
    """
    
    def __init__(
        self,
        process: 'ProcessProtocol',
        context: 'ProcessContext',
        bridge: 'BridgeProtocol',
        event_emitter: Optional['EventEmitter'] = None,
        config: Optional[ProcessRunnerConfig] = None
    ):
        """
        Initialize process runner.
        
        Args:
            process: Process to execute
            context: Execution context
            bridge: Browser automation bridge
            event_emitter: Optional event emitter for observability
            config: Optional configuration (uses defaults if not provided)
        """
        from .state_machine import StateMachine
        from .page_detector import PageDetector
        from .action_executor import ActionExecutor
        
        self.process = process
        self.context = context
        self.bridge = bridge
        self.config = config or DEFAULT_CONFIG
        self._emitter = event_emitter
        self._logger = logging.getLogger(__name__)
        
        # Extract pause/stop events from context
        pause_event = getattr(context, 'pause_event', None)
        stop_event = getattr(context, 'stop_event', None)
        
        # Initialize components
        self.state_machine = StateMachine(
            initial_state=process.initial_state,
            process_name=process.name,
            event_emitter=event_emitter
        )
        
        self.page_detector = PageDetector(
            bridge=bridge,
            process_screens=process.screens,
            global_interrupts=process.global_interrupts,
            event_emitter=event_emitter,
            pause_event=pause_event,
            stop_event=stop_event
        )
        
        self.action_executor = ActionExecutor(
            bridge=bridge,
            event_emitter=event_emitter,
            pause_event=pause_event,
            stop_event=stop_event
        )
        
        # Initialize services
        self._recovery_service = RecoveryService(bridge, self.action_executor)
        self._outcome_classifier = OutcomeClassifier()
        self._transition_service = StateTransitionService(self.state_machine)
        
        # Bind state machine to context
        context.set_state_machine(self.state_machine)
        context.set_process(process)
    
    def run(self) -> str:
        """
        Execute the process.
        
        Delegates to ProcessExecutionCoordinator for actual execution.
        
        Returns:
            Outcome string: 'success', 'failure', or 'retry'
            
        Raises:
            AutomationStoppedException: If user requests stop
        """
        # Create coordinator
        coordinator = ProcessExecutionCoordinator(
            state_machine=self.state_machine,
            page_detector=self.page_detector,
            action_executor=self.action_executor,
            recovery_service=self._recovery_service,
            outcome_classifier=self._outcome_classifier,
            transition_service=self._transition_service,
            process=self.process,
            context=self.context,
            config=self.config,
            event_emitter=self._emitter,
            logger=self._logger
        )
        
        # Execute
        return coordinator.execute()
