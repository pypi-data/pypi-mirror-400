"""
Steward Agent Wrapper - Universal Agent Monitoring Wrapper

This module provides the StewardAgentWrapper class that transparently wraps
ANY agent (from any framework) and monitors it with Steward Agent oversight.

Key Features:
    - Framework-agnostic: Works with CrewAI, LangChain, AutoGen, custom agents
    - Transparent: Agent behaves normally, monitoring happens in background
    - Adaptive: Uses adapters to handle framework-specific behaviors
    - Async-ready: Non-blocking monitoring for production environments
    - Error-resilient: Graceful fallbacks if monitoring fails

Architecture:
    ```
    User Code → StewardAgentWrapper → AgentAdapter → Framework Agent
                        ↓
                   Steward Agent Core (monitoring, CTQ, modes)
    ```

Usage Example:
    ```python
    from src.wrapper import StewardAgentWrapper
    from src.adapters import CrewAIAdapter
    from src.core import StewardAgent

    # Your agent (any framework)
    my_agent = CrewAIAgent(role="researcher", ...)

    # Wrap it
    adapter = CrewAIAdapter()
    steward = StewardAgent()
    wrapped_agent = StewardAgentWrapper(my_agent, adapter, steward)

    # Use normally - monitoring happens automatically
    result = wrapped_agent.execute("research AI safety")

    # Steward Agent provides feedback, CTQ scores, mode switching
    ```

Zero Framework Dependencies:
    This module MUST NOT import any agent framework.
    Only standard library and internal Steward Agent components.
"""

import logging
import asyncio
import time
from typing import Any, Optional, Dict, Callable, Union
from functools import wraps
from datetime import datetime

try:
    from .agent_protocol import AgentAdapter, AgentExecutionContext, AgentExecutionResult
    from ..core.steward_agent import StewardAgent
    from ..utils.data_models import AgentReasoningTrace, SocraticNudge, HITLAlert
    from ..utils.observer_interface import StewardEvent, StewardEventType
except ImportError:
    from agent_protocol import AgentAdapter, AgentExecutionContext, AgentExecutionResult
    from core.steward_agent import StewardAgent
    from utils.data_models import AgentReasoningTrace, SocraticNudge, HITLAlert
    from utils.observer_interface import StewardEvent, StewardEventType


class StewardAgentWrapper:
    """
    Universal wrapper that monitors any agent with Steward Agent oversight.

    This class wraps an agent from ANY framework and provides transparent
    monitoring, feedback injection, and adaptive oversight.

    Attributes:
        agent: The wrapped agent (framework-specific)
        adapter: Adapter for framework-specific operations
        steward_agent: Steward Agent instance for monitoring
        monitoring_enabled: Whether monitoring is active
        async_monitoring: Whether to monitor asynchronously (non-blocking)

    Example:
        ```python
        # Wrap a CrewAI agent
        from src.adapters import CrewAIAdapter

        agent = CrewAIAgent(...)
        adapter = CrewAIAdapter()
        steward = StewardAgent()

        wrapped = StewardAgentWrapper(agent, adapter, steward)
        result = wrapped.execute("task")  # Monitored automatically
        ```
    """

    def __init__(
        self,
        agent: Any,
        adapter: AgentAdapter,
        agent_id: str,
        agent_tag: str,
        steward_agent: Optional[StewardAgent] = None,
        monitoring_enabled: bool = True,
        async_monitoring: bool = False,
        fail_on_monitoring_error: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Steward Agent Wrapper.

        Supports ANY agent with ANY identifier and tag - no limitations.

        Args:
            agent: Agent to wrap (any framework)
            adapter: Adapter for framework-specific operations
            agent_id: Unique identifier for this agent (e.g., "planner", "executor", "researcher", "critic")
            agent_tag: Role category or custom tag (e.g., "A", "B", "C", "planner", "executor", "researcher")
                      No restrictions - use any meaningful tag for your use case
            steward_agent: Steward Agent instance (created if None)
            monitoring_enabled: Enable/disable monitoring for this specific agent
            async_monitoring: Run monitoring asynchronously (non-blocking).
                             Default False for safety (works in all contexts).
                             Set True only when running in async context with event loop
                             (e.g., FastAPI with await, asyncio.run(), etc.)
            fail_on_monitoring_error: Raise error if monitoring fails
            logger: Optional logger instance

        Raises:
            ValueError: If adapter doesn't support the agent or agent_id/agent_tag invalid
        """
        # Validate adapter supports this agent
        if not adapter.supports_agent(agent):
            raise ValueError(
                f"Adapter {type(adapter).__name__} does not support agent type {type(agent).__name__}"
            )

        # Validate agent_id and agent_tag
        if not agent_id or not isinstance(agent_id, str):
            raise ValueError("agent_id is required and must be a non-empty string")

        if not agent_tag or not isinstance(agent_tag, str):
            raise ValueError("agent_tag is required and must be a non-empty string")

        self._agent = agent
        self._adapter = adapter
        self._agent_id = agent_id
        self._agent_tag = agent_tag
        self._steward_agent = steward_agent or StewardAgent()  # Lazy init
        self._monitoring_enabled = monitoring_enabled
        self._async_monitoring = async_monitoring
        self._fail_on_monitoring_error = fail_on_monitoring_error

        # Logging
        self._logger = logger or logging.getLogger(__name__)

        # Execution history
        self._execution_history: list[Dict[str, Any]] = []
        self._current_execution_context: Optional[AgentExecutionContext] = None

        # Statistics
        self._total_executions = 0
        self._successful_executions = 0
        self._monitoring_errors = 0

        # Register this wrapper with Steward Agent
        if self._steward_agent:
            self._steward_agent.register_agent(
                agent_id=self._agent_id,
                agent_tag=self._agent_tag,
                monitoring_enabled=self._monitoring_enabled,
                wrapper=self
            )

        self._logger.info(
            f"StewardAgentWrapper initialized for {type(agent).__name__} "
            f"(agent_id={agent_id}, agent_tag={agent_tag}, monitoring={monitoring_enabled}) "
            f"using {type(adapter).__name__}"
        )

    # ========================================
    # Transparent Method Interception
    # ========================================

    def __getattr__(self, name: str) -> Any:
        """
        Intercept method calls to wrapped agent.

        This enables transparent wrapping - any method called on the wrapper
        gets forwarded to the underlying agent, with monitoring if it's execute().

        Args:
            name: Method name being accessed

        Returns:
            Method from wrapped agent (potentially wrapped with monitoring)
        """
        # Get attribute from wrapped agent
        attr = getattr(self._agent, name)

        # If it's not callable, return as-is
        if not callable(attr):
            return attr

        # Ask adapter if this method should be monitored (framework-agnostic)
        # Adapter knows which methods trigger execution for this framework
        if name in self._adapter.get_execution_methods():
            return self._create_monitored_method(attr, name)

        # Otherwise return as-is
        return attr

    def _create_monitored_method(self, method: Callable, method_name: str) -> Callable:
        """
        Create a monitored version of an agent method.

        Args:
            method: Original agent method
            method_name: Name of the method

        Returns:
            Wrapped method with monitoring
        """
        @wraps(method)
        def monitored_method(*args, **kwargs):
            return self._execute_with_monitoring(method, args, kwargs, method_name)

        return monitored_method

    # ========================================
    # Core Monitoring Logic
    # ========================================

    def _execute_with_monitoring(
        self,
        method: Callable,
        args: tuple,
        kwargs: dict,
        method_name: str
    ) -> Any:
        """
        Execute agent method with Steward Agent monitoring.

        Flow:
            1. Pre-execution: Extract context, create execution context
            2. Execute: Call actual agent method
            3. Post-execution: Extract reasoning, send to Steward Agent
            4. Feedback: Inject Steward Agent feedback into agent
            5. Return: Return original result

        Args:
            method: Agent method to execute
            args: Positional arguments
            kwargs: Keyword arguments
            method_name: Name of method being executed

        Returns:
            Result from agent execution
        """
        self._total_executions += 1
        start_time = time.time()

        try:
            # 1. Pre-execution: Create context
            task = args[0] if args else kwargs.get('task', 'unknown')
            goal = kwargs.get('goal')

            execution_context = self._adapter.create_execution_context(
                agent=self._agent,
                task=task,
                goal=goal,
                **kwargs
            )
            self._current_execution_context = execution_context

            self._logger.debug(
                f"Executing {method_name} with monitoring: "
                f"agent={execution_context.agent_id}, task={task}"
            )

            # 2. Execute agent method
            result = method(*args, **kwargs)

            # 3. Post-execution: Monitor if enabled
            if self._monitoring_enabled:
                if self._async_monitoring:
                    # Non-blocking monitoring
                    asyncio.create_task(
                        self._monitor_execution_async(result, execution_context, start_time)
                    )
                else:
                    # Blocking monitoring
                    self._monitor_execution_sync(result, execution_context, start_time)

            self._successful_executions += 1
            return result

        except Exception as e:
            self._logger.error(f"Error in agent execution: {e}")
            # Record failure but don't break agent execution
            execution_time = time.time() - start_time
            self._record_execution({
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            })
            raise

    def _monitor_execution_sync(
        self,
        result: Any,
        execution_context: AgentExecutionContext,
        start_time: float
    ) -> None:
        """
        Synchronous (blocking) monitoring.

        Args:
            result: Agent execution result
            execution_context: Context about the execution
            start_time: Execution start timestamp
        """
        try:
            # Extract reasoning trace
            reasoning_trace = self._adapter.extract_reasoning(
                agent=self._agent,
                execution_result=result,
                execution_context=execution_context
            )

            # Send to Steward Agent for monitoring
            # process_agent_reasoning_step returns tuple: (socratic_nudge, hitl_alert, mode_state)
            import asyncio
            socratic_nudge, hitl_alert, mode_state = asyncio.run(
                self._steward_agent.process_agent_reasoning_step(
                    agent_type=execution_context.agent_type,
                    reasoning_trace=reasoning_trace
                )
            )

            # Inject feedback into agent (use socratic_nudge as primary feedback)
            feedback = socratic_nudge or hitl_alert
            if feedback:
                self._inject_feedback(feedback)

            # Record execution
            execution_time = time.time() - start_time
            self._record_execution({
                'success': True,
                'result': result,
                'reasoning_trace': reasoning_trace,
                'feedback': feedback,
                'execution_time': execution_time
            })

        except Exception as e:
            self._monitoring_errors += 1
            self._logger.error(f"Error in monitoring: {e}")
            if self._fail_on_monitoring_error:
                raise

    async def _monitor_execution_async(
        self,
        result: Any,
        execution_context: AgentExecutionContext,
        start_time: float
    ) -> None:
        """
        Asynchronous (non-blocking) monitoring.

        Args:
            result: Agent execution result
            execution_context: Context about the execution
            start_time: Execution start timestamp
        """
        try:
            # Extract reasoning trace
            reasoning_trace = self._adapter.extract_reasoning(
                agent=self._agent,
                execution_result=result,
                execution_context=execution_context
            )

            # Send to Steward Agent for monitoring (make async if possible)
            socratic_nudge, hitl_alert, mode_state = await self._process_with_steward_async(
                agent_type=execution_context.agent_type,
                reasoning_trace=reasoning_trace
            )

            # Inject feedback into agent (use socratic_nudge as primary feedback)
            feedback = socratic_nudge or hitl_alert
            if feedback:
                self._inject_feedback(feedback)

            # Record execution
            execution_time = time.time() - start_time
            self._record_execution({
                'success': True,
                'result': result,
                'reasoning_trace': reasoning_trace,
                'feedback': feedback,
                'execution_time': execution_time
            })

        except Exception as e:
            self._monitoring_errors += 1
            self._logger.error(f"Error in async monitoring: {e}")
            if self._fail_on_monitoring_error:
                raise

    async def _process_with_steward_async(
        self,
        agent_type: str,
        reasoning_trace: AgentReasoningTrace
    ) -> tuple:
        """
        Process reasoning trace with Steward Agent asynchronously.

        Args:
            agent_type: Type of agent being monitored
            reasoning_trace: Extracted reasoning trace

        Returns:
            Tuple of (socratic_nudge, hitl_alert, mode_state)
        """
        # Call the async method directly (it's already async)
        return await self._steward_agent.process_agent_reasoning_step(
            agent_type=agent_type,
            reasoning_trace=reasoning_trace
        )

    def _inject_feedback(self, feedback: Union[SocraticNudge, HITLAlert, Any]) -> None:
        """
        Inject Steward Agent feedback into wrapped agent.

        Args:
            feedback: Feedback from Steward Agent
        """
        try:
            self._adapter.inject_feedback(
                agent=self._agent,
                feedback=feedback,
                execution_context=self._current_execution_context
            )
            self._logger.debug(f"Feedback injected: {type(feedback).__name__}")
        except Exception as e:
            self._logger.error(f"Error injecting feedback: {e}")

    def _record_execution(self, execution_record: Dict[str, Any]) -> None:
        """
        Record execution for history/debugging.

        Args:
            execution_record: Dictionary with execution details
        """
        execution_record['timestamp'] = datetime.now().isoformat()
        execution_record['agent_id'] = (
            self._current_execution_context.agent_id
            if self._current_execution_context
            else 'unknown'
        )
        self._execution_history.append(execution_record)

        # Keep last 100 executions only
        if len(self._execution_history) > 100:
            self._execution_history = self._execution_history[-100:]

    # ========================================
    # Public API
    # ========================================

    def enable_monitoring(self) -> None:
        """Enable Steward Agent monitoring."""
        self._monitoring_enabled = True
        self._logger.info("Monitoring enabled")

    def disable_monitoring(self) -> None:
        """Disable Steward Agent monitoring."""
        self._monitoring_enabled = False
        self._logger.info("Monitoring disabled")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get wrapper statistics.

        Returns:
            Dictionary with execution statistics
        """
        return {
            'total_executions': self._total_executions,
            'successful_executions': self._successful_executions,
            'monitoring_errors': self._monitoring_errors,
            'success_rate': (
                self._successful_executions / self._total_executions
                if self._total_executions > 0
                else 0.0
            ),
            'monitoring_enabled': self._monitoring_enabled,
            'async_monitoring': self._async_monitoring
        }

    def get_execution_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Get recent execution history.

        Args:
            limit: Maximum number of executions to return

        Returns:
            List of recent execution records
        """
        return self._execution_history[-limit:]

    @property
    def unwrapped_agent(self) -> Any:
        """Access the unwrapped agent directly."""
        return self._agent

    @property
    def steward_agent(self) -> StewardAgent:
        """Access the Steward Agent instance."""
        return self._steward_agent

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"StewardAgentWrapper("
            f"agent={type(self._agent).__name__}, "
            f"adapter={type(self._adapter).__name__}, "
            f"monitoring={'enabled' if self._monitoring_enabled else 'disabled'}"
            f")"
        )


__all__ = ['StewardAgentWrapper']
