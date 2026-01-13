"""
Generic Adapter - Universal Adapter for Any Python Agent

This is the simplest possible adapter that works with ANY Python object
that has an execute() method. It's the "batteries included" adapter that
requires no framework-specific knowledge.

Use Cases:
    - Custom agents you write yourself
    - Simple Python classes with execute()
    - Functions wrapped as agents
    - Prototyping and testing
    - When you don't need framework-specific features

Features:
    - Works with any object having execute() method
    - Gracefully handles missing attributes
    - Simple string-based reasoning extraction
    - Best-effort feedback injection
    - No framework dependencies

Usage Example:
    ```python
    from src.adapters import GenericAdapter
    from src.wrapper import StewardAgentWrapper
    from src.core import StewardAgent

    # Your custom agent
    class MyCustomAgent:
        def __init__(self, name):
            self.name = name
            self.context = []

        def execute(self, task):
            result = f"Completed: {task}"
            self.context.append(result)
            return result

    # Wrap with GenericAdapter
    agent = MyCustomAgent("assistant")
    adapter = GenericAdapter()
    steward = StewardAgent()
    wrapped = StewardAgentWrapper(agent, adapter, steward)

    # Use normally - monitored automatically
    result = wrapped.execute("research AI safety")
    ```

Zero Framework Dependencies:
    This adapter has NO dependencies on any agent framework.
    Works with plain Python objects only.
"""

import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime

try:
    from ..wrapper.agent_protocol import (
        AgentAdapter,
        AgentExecutionContext,
        AgentExecutionResult
    )
    from ..utils.data_models import (
        AgentReasoningTrace,
        SocraticNudge,
        HITLAlert
    )
except ImportError:
    from wrapper.agent_protocol import (
        AgentAdapter,
        AgentExecutionContext,
        AgentExecutionResult
    )
    from utils.data_models import (
        AgentReasoningTrace,
        SocraticNudge,
        HITLAlert
    )


class GenericAdapter(AgentAdapter):
    """
    Universal adapter for any Python object with an execute() method.

    This is the simplest adapter - it makes minimal assumptions about
    the agent and works with any Python object that has execute().

    Reasoning Extraction Strategy:
        - If result is a dict with 'reasoning' key, use it
        - If result is a dict with 'output' key, use it as output
        - Otherwise, convert result to string
        - Falls back gracefully if reasoning not available

    Feedback Injection Strategy:
        - If agent has 'context' attribute (list/dict), append feedback
        - If agent has 'feedback' attribute (list), append feedback
        - Otherwise, log feedback but don't inject
        - Never fails - always graceful degradation

    Metadata Extraction:
        - Uses agent's __name__, __class__.__name__, or 'unknown'
        - Checks for common attributes (name, type, role, etc.)
        - Returns basic metadata dict

    Attributes:
        logger: Logger instance for debugging
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Generic Adapter.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("GenericAdapter initialized")

    def supports_agent(self, agent: Any) -> bool:
        """
        Check if agent has an execute() method.

        This is the only requirement for GenericAdapter.

        Args:
            agent: Object to check

        Returns:
            True if object has execute() method, False otherwise
        """
        has_execute = (
            hasattr(agent, 'execute') and
            callable(getattr(agent, 'execute'))
        )

        if not has_execute:
            self.logger.debug(
                f"Agent {type(agent).__name__} does not have execute() method"
            )

        return has_execute

    def extract_reasoning(
        self,
        agent: Any,
        execution_result: Any,
        execution_context: Optional[AgentExecutionContext] = None
    ) -> AgentReasoningTrace:
        """
        Extract reasoning trace from execution result.

        Strategy:
            1. If result is dict, try to extract 'reasoning', 'output', 'thoughts'
            2. If result has these as attributes, use them
            3. Otherwise, use string representation as output
            4. Goal comes from context if available

        Args:
            agent: The agent that executed
            execution_result: Result from agent execution
            execution_context: Optional execution context

        Returns:
            AgentReasoningTrace with extracted information
        """
        # Extract agent name
        agent_name = self._get_agent_name(agent)

        # Extract reasoning and output from result
        reasoning_text, final_output = self._extract_from_result(execution_result)

        # Get goal from context or default
        goal = ""
        if execution_context:
            goal = execution_context.goal or execution_context.task or ""

        # Get agent type and derive agent tag
        agent_type = self._get_agent_type(agent)
        agent_tag = "A" if agent_type == "planner" else "B"

        # Get step info from context or generate defaults
        step_id = f"generic_{agent_name}_{datetime.now().timestamp()}"
        step_number = 1
        if execution_context:
            step_id = getattr(execution_context, 'step_id', step_id)
            step_number = getattr(execution_context, 'step_number', step_number)

        # Create reasoning trace
        trace = AgentReasoningTrace(
            agent_name=agent_name,
            agent_type=agent_type,
            agent_tag=agent_tag,
            step_id=step_id,
            step_number=step_number,
            reasoning_text=reasoning_text,
            final_output=final_output,
            goal=goal,
            context_information=self._extract_context_info(agent, execution_context)
        )

        self.logger.debug(
            f"Extracted reasoning trace for {agent_name}: "
            f"output_length={len(str(final_output))}"
        )

        return trace

    def inject_feedback(
        self,
        agent: Any,
        feedback: Union[SocraticNudge, HITLAlert, str],
        execution_context: Optional[AgentExecutionContext] = None
    ) -> None:
        """
        Inject Steward Agent feedback into agent.

        Strategy (tries in order):
            1. If agent has 'context' list, append feedback
            2. If agent has 'feedback' list, append feedback
            3. If agent has 'history' list, append feedback
            4. Otherwise, log warning (no injection)

        This is best-effort - never fails, always graceful.

        Args:
            agent: Agent to inject feedback into
            feedback: Feedback to inject
            execution_context: Optional execution context
        """
        # Convert feedback to string
        feedback_text = self._feedback_to_string(feedback)

        # Try different injection strategies
        injected = False

        # Strategy 1: Agent has 'context' attribute (list or dict)
        if hasattr(agent, 'context'):
            context = getattr(agent, 'context')
            if isinstance(context, list):
                context.append(feedback_text)
                injected = True
                self.logger.debug("Feedback injected into agent.context (list)")
            elif isinstance(context, dict):
                context['steward_feedback'] = context.get('steward_feedback', []) + [feedback_text]
                injected = True
                self.logger.debug("Feedback injected into agent.context (dict)")

        # Strategy 2: Agent has 'feedback' attribute
        if not injected and hasattr(agent, 'feedback'):
            feedback_list = getattr(agent, 'feedback')
            if isinstance(feedback_list, list):
                feedback_list.append(feedback_text)
                injected = True
                self.logger.debug("Feedback injected into agent.feedback")

        # Strategy 3: Agent has 'history' attribute
        if not injected and hasattr(agent, 'history'):
            history = getattr(agent, 'history')
            if isinstance(history, list):
                history.append({'type': 'steward_feedback', 'content': feedback_text})
                injected = True
                self.logger.debug("Feedback injected into agent.history")

        # Fallback: Log but don't fail
        if not injected:
            self.logger.warning(
                f"Could not inject feedback into {type(agent).__name__}. "
                f"Agent has no 'context', 'feedback', or 'history' attribute. "
                f"Feedback: {feedback_text[:100]}..."
            )

    def get_agent_metadata(self, agent: Any) -> Dict[str, Any]:
        """
        Extract metadata about the agent.

        Tries to extract:
            - agent_name: From name, __name__, __class__.__name__
            - agent_type: From type, role, agent_type attributes
            - framework: Always 'generic' for this adapter
            - capabilities: Based on available methods

        Args:
            agent: Agent to extract metadata from

        Returns:
            Dictionary with agent metadata
        """
        metadata = {
            'framework': 'generic',
            'adapter': 'GenericAdapter',
            'agent_name': self._get_agent_name(agent),
            'agent_type': self._get_agent_type(agent),
            'agent_class': type(agent).__name__,
            'capabilities': self._get_capabilities(agent),
            'has_context': hasattr(agent, 'context'),
            'has_feedback': hasattr(agent, 'feedback'),
            'has_history': hasattr(agent, 'history'),
        }

        self.logger.debug(f"Extracted metadata for {metadata['agent_name']}")

        return metadata

    # ========================================
    # Helper Methods
    # ========================================

    def _get_agent_name(self, agent: Any) -> str:
        """Get agent name from various possible attributes."""
        # Try common name attributes
        if hasattr(agent, 'name'):
            return str(agent.name)
        if hasattr(agent, '__name__'):
            return agent.__name__
        return type(agent).__name__

    def _get_agent_type(self, agent: Any) -> str:
        """Get agent type from various possible attributes."""
        # Try common type attributes
        if hasattr(agent, 'agent_type'):
            return str(agent.agent_type)
        if hasattr(agent, 'type'):
            return str(agent.type)
        if hasattr(agent, 'role'):
            return str(agent.role)
        return 'generic'

    def _extract_from_result(self, result: Any) -> tuple[str, str]:
        """
        Extract reasoning and output from result.

        Returns:
            Tuple of (reasoning_text, final_output)
        """
        reasoning_text = ""
        final_output = ""

        # Case 1: Result is a dictionary
        if isinstance(result, dict):
            reasoning_text = str(result.get('reasoning', result.get('thoughts', '')))
            final_output = str(result.get('output', result.get('result', str(result))))

        # Case 2: Result has reasoning/output attributes
        elif hasattr(result, 'reasoning') or hasattr(result, 'output'):
            reasoning_text = str(getattr(result, 'reasoning', ''))
            final_output = str(getattr(result, 'output', str(result)))

        # Case 3: Result is simple value
        else:
            final_output = str(result)
            reasoning_text = f"Executed task, returned: {final_output[:100]}"

        return reasoning_text, final_output

    def _extract_context_info(
        self,
        agent: Any,
        execution_context: Optional[AgentExecutionContext]
    ) -> Dict[str, Any]:
        """Extract context information for reasoning trace."""
        context_info = {
            'adapter': 'GenericAdapter',
            'timestamp': datetime.now().isoformat(),
        }

        if execution_context:
            context_info['execution_context'] = {
                'agent_id': execution_context.agent_id,
                'framework': execution_context.framework,
                'task': execution_context.task,
            }

        # Add agent-specific context if available
        if hasattr(agent, 'context'):
            context_info['agent_context'] = str(agent.context)

        return context_info

    def _feedback_to_string(self, feedback: Union[SocraticNudge, HITLAlert, str]) -> str:
        """Convert feedback to string representation."""
        if isinstance(feedback, str):
            return feedback
        elif isinstance(feedback, SocraticNudge):
            return f"[Socratic Nudge] {feedback.question}"
        elif isinstance(feedback, HITLAlert):
            return f"[HITL Alert] {feedback.alert_message}"
        else:
            return str(feedback)

    def _get_capabilities(self, agent: Any) -> list[str]:
        """Get list of agent capabilities based on available methods."""
        capabilities = ['execute']  # Always has execute if we got here

        # Check for common agent methods
        if hasattr(agent, 'plan') and callable(getattr(agent, 'plan')):
            capabilities.append('plan')
        if hasattr(agent, 'think') and callable(getattr(agent, 'think')):
            capabilities.append('think')
        if hasattr(agent, 'reflect') and callable(getattr(agent, 'reflect')):
            capabilities.append('reflect')

        return capabilities


__all__ = ['GenericAdapter']
