"""
Steward Monitor Decorator - Pythonic Monitoring via Decorators

This module provides the @steward_monitor decorator for adding Steward Agent
monitoring to functions, methods, and classes with minimal code changes.

The decorator approach is the most Pythonic way to add monitoring:
- Clean syntax: Just add @steward_monitor
- Non-invasive: Original code unchanged
- Transparent: Functions work normally
- Flexible: Works with functions, methods, and classes

Usage Examples:

    # Example 1: Decorate a function
    from src.wrapper import steward_monitor
    from src.adapters import GenericAdapter

    @steward_monitor(adapter=GenericAdapter())
    def my_agent(query):
        return f"Processing: {query}"

    result = my_agent("test")  # Monitored automatically


    # Example 2: Decorate a class
    @steward_monitor(adapter=GenericAdapter())
    class MyAgent:
        def execute(self, task):
            return f"Completed: {task}"

    agent = MyAgent()
    result = agent.execute("task")  # Monitored automatically


    # Example 3: Decorate with configuration
    @steward_monitor(
        adapter=GenericAdapter(),
        async_monitoring=True,
        monitoring_enabled=True
    )
    def production_agent(query):
        return process_important_task(query)

Zero Framework Dependencies:
    This module MUST NOT import any agent framework.
    Only standard library and internal Steward Agent components.
"""

import logging
import inspect
from typing import Any, Optional, Callable, Type, Union
from functools import wraps

try:
    from .agent_protocol import AgentAdapter
    from .steward_agent_wrapper import StewardAgentWrapper
    from ..core.steward_agent import StewardAgent
except ImportError:
    from .agent_protocol import AgentAdapter
    from wrapper.steward_agent_wrapper import StewardAgentWrapper
    from core.steward_agent import StewardAgent


def steward_monitor(
    adapter: Optional[AgentAdapter] = None,
    steward_agent: Optional[StewardAgent] = None,
    monitoring_enabled: bool = True,
    async_monitoring: bool = True,
    fail_on_monitoring_error: bool = False,
    logger: Optional[logging.Logger] = None
):
    """
    Decorator to add Steward Agent monitoring to functions, methods, or classes.

    This decorator wraps the target with StewardAgentWrapper, enabling transparent
    monitoring without modifying the original code.

    Args:
        adapter: AgentAdapter instance for framework-specific handling.
                 If None, GenericAdapter will be used (requires generic_adapter module)
        steward_agent: Steward Agent instance. Created if None.
        monitoring_enabled: Enable/disable monitoring (default: True)
        async_monitoring: Run monitoring asynchronously (default: True)
        fail_on_monitoring_error: Raise errors if monitoring fails (default: False)
        logger: Optional logger instance

    Returns:
        Decorated function/class with Steward Agent monitoring

    Usage:
        # Minimal usage
        @steward_monitor()
        def my_function(query):
            return process(query)

        # With configuration
        @steward_monitor(
            adapter=MyCustomAdapter(),
            async_monitoring=True
        )
        class MyAgent:
            def execute(self, task):
                return do_work(task)

    Note:
        - Functions: The function itself is wrapped
        - Classes: The class's execute() method is wrapped
        - Methods: Individual methods can be decorated
    """
    # Handle adapter defaulting
    if adapter is None:
        # Lazy import GenericAdapter to avoid circular dependency
        try:
            from ..adapters.generic_adapter import GenericAdapter
            adapter = GenericAdapter()
        except ImportError:
            raise ValueError(
                "adapter parameter is required when GenericAdapter is not available. "
                "Please provide an adapter or ensure GenericAdapter is installed."
            )

    # Get logger
    log = logger or logging.getLogger(__name__)

    def decorator(target: Union[Callable, Type]) -> Union[Callable, Type]:
        """
        Inner decorator that wraps the target.

        Args:
            target: Function or class to decorate

        Returns:
            Wrapped function or class
        """
        # Case 1: Decorating a class
        if inspect.isclass(target):
            return _wrap_class(
                target, adapter, steward_agent, monitoring_enabled,
                async_monitoring, fail_on_monitoring_error, log
            )

        # Case 2: Decorating a function or method
        elif callable(target):
            return _wrap_function(
                target, adapter, steward_agent, monitoring_enabled,
                async_monitoring, fail_on_monitoring_error, log
            )

        else:
            raise TypeError(
                f"@steward_monitor can only decorate functions or classes, "
                f"not {type(target).__name__}"
            )

    return decorator


def _wrap_function(
    func: Callable,
    adapter: AgentAdapter,
    steward_agent: Optional[StewardAgent],
    monitoring_enabled: bool,
    async_monitoring: bool,
    fail_on_monitoring_error: bool,
    logger: logging.Logger
) -> Callable:
    """
    Wrap a function with Steward Agent monitoring.

    Args:
        func: Function to wrap
        adapter: AgentAdapter instance
        steward_agent: Optional Steward Agent instance
        monitoring_enabled: Enable monitoring flag
        async_monitoring: Async monitoring flag
        fail_on_monitoring_error: Fail on error flag
        logger: Logger instance

    Returns:
        Wrapped function
    """
    @wraps(func)
    def monitored_function(*args, **kwargs):
        """Monitored version of the original function."""
        # Create a callable wrapper object that adapter can work with
        class FunctionAgent:
            """Minimal agent wrapper for functions."""
            def __init__(self, fn):
                self._fn = fn
                self.__name__ = fn.__name__
                self.__doc__ = fn.__doc__

            def execute(self, *a, **kw):
                return self._fn(*a, **kw)

        # Create agent wrapper
        function_agent = FunctionAgent(func)

        # Wrap with Steward Agent
        wrapper = StewardAgentWrapper(
            agent=function_agent,
            adapter=adapter,
            steward_agent=steward_agent,
            monitoring_enabled=monitoring_enabled,
            async_monitoring=async_monitoring,
            fail_on_monitoring_error=fail_on_monitoring_error,
            logger=logger
        )

        # Execute through wrapper
        return wrapper.execute(*args, **kwargs)

    # Preserve original function metadata
    monitored_function._steward_monitored = True
    monitored_function._original_function = func

    return monitored_function


def _wrap_class(
    cls: Type,
    adapter: AgentAdapter,
    steward_agent: Optional[StewardAgent],
    monitoring_enabled: bool,
    async_monitoring: bool,
    fail_on_monitoring_error: bool,
    logger: logging.Logger
) -> Type:
    """
    Wrap a class with Steward Agent monitoring.

    This wraps the class's execute() method (or other specified methods)
    with monitoring.

    Args:
        cls: Class to wrap
        adapter: AgentAdapter instance
        steward_agent: Optional Steward Agent instance
        monitoring_enabled: Enable monitoring flag
        async_monitoring: Async monitoring flag
        fail_on_monitoring_error: Fail on error flag
        logger: Logger instance

    Returns:
        Wrapped class

    Raises:
        ValueError: If class doesn't have execute() method
    """
    # Check if class has execute method
    if not hasattr(cls, 'execute'):
        raise ValueError(
            f"Class {cls.__name__} must have an execute() method to be monitored. "
            f"Available methods: {[m for m in dir(cls) if not m.startswith('_')]}"
        )

    # Create wrapped class
    class MonitoredClass(cls):
        """Monitored version of the original class."""

        def __init__(self, *args, **kwargs):
            """Initialize with Steward Agent wrapper."""
            # Initialize parent class
            super().__init__(*args, **kwargs)

            # Create Steward Agent wrapper for this instance
            self._steward_wrapper = StewardAgentWrapper(
                agent=self,
                adapter=adapter,
                steward_agent=steward_agent,
                monitoring_enabled=monitoring_enabled,
                async_monitoring=async_monitoring,
                fail_on_monitoring_error=fail_on_monitoring_error,
                logger=logger
            )

            logger.debug(
                f"Steward monitoring initialized for {cls.__name__} instance"
            )

        def execute(self, *args, **kwargs):
            """Monitored execute method."""
            # Use parent's execute through steward wrapper
            return self._steward_wrapper.execute(*args, **kwargs)

        @property
        def steward_wrapper(self) -> StewardAgentWrapper:
            """Access to the Steward Agent wrapper."""
            return self._steward_wrapper

        @property
        def monitoring_enabled(self) -> bool:
            """Check if monitoring is enabled."""
            return self._steward_wrapper._monitoring_enabled

        def enable_monitoring(self) -> None:
            """Enable Steward Agent monitoring."""
            self._steward_wrapper.enable_monitoring()

        def disable_monitoring(self) -> None:
            """Disable Steward Agent monitoring."""
            self._steward_wrapper.disable_monitoring()

        def get_monitoring_statistics(self) -> dict:
            """Get monitoring statistics."""
            return self._steward_wrapper.get_statistics()

    # Preserve class metadata
    MonitoredClass.__name__ = cls.__name__
    MonitoredClass.__qualname__ = cls.__qualname__
    MonitoredClass.__module__ = cls.__module__
    MonitoredClass._steward_monitored = True
    MonitoredClass._original_class = cls

    return MonitoredClass


# Convenience function for manual wrapping
def wrap_with_monitoring(
    agent: Any,
    adapter: AgentAdapter,
    **wrapper_kwargs
) -> Any:
    """
    Manually wrap an agent with Steward Agent monitoring.

    This is a convenience function for when you can't use decorators.

    Args:
        agent: Agent instance to wrap
        adapter: AgentAdapter instance
        **wrapper_kwargs: Additional arguments for StewardAgentWrapper

    Returns:
        Wrapped agent instance

    Usage:
        agent = MyAgent()
        adapter = GenericAdapter()
        wrapped = wrap_with_monitoring(agent, adapter)
        result = wrapped.execute("task")
    """
    return StewardAgentWrapper(
        agent=agent,
        adapter=adapter,
        **wrapper_kwargs
    )


__all__ = [
    'steward_monitor',
    'wrap_with_monitoring',
]
