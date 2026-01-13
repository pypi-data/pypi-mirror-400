"""
CrewAI Adapter - Framework-Specific Adapter for CrewAI Agents

This adapter enables Steward Agent to monitor CrewAI agents transparently.
It handles CrewAI-specific output formats, agent structures, and feedback injection.

Supports:
    - CrewAI Agent objects
    - CrewAI Crew objects
    - CrewAI Task objects
    - CrewOutput parsing
    - Agent role/goal/backstory extraction

Usage Example:
    ```python
    from crewai import Agent
    from src.adapters import CrewAIAdapter
    from src.wrapper import StewardAgentWrapper
    from src.core import StewardAgent

    # Create CrewAI agent
    agent = Agent(
        role="Researcher",
        goal="Find latest AI developments",
        backstory="Expert AI researcher"
    )

    # Wrap with Steward Agent monitoring
    adapter = CrewAIAdapter()
    steward = StewardAgent()
    wrapped = StewardAgentWrapper(agent, adapter, steward)

    # Use normally - monitored automatically
    result = wrapped.execute("Research AI safety")
    ```

Framework Dependency:
    This adapter imports CrewAI but handles ImportError gracefully.
    If CrewAI is not installed, adapter will report it doesn't support agents.
"""

import logging
from typing import Any, Dict, Optional, Union

# Try to import CrewAI
try:
    from crewai import Agent, Task, Crew
    from crewai.agent import Agent as CrewAIAgent
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # Placeholders for type hints
    class Agent: pass
    class Task: pass
    class Crew: pass
    class CrewAIAgent: pass

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


class CrewAIAdapter(AgentAdapter):
    """
    Adapter for CrewAI agents, crews, and tasks.

    This adapter translates between CrewAI's agent framework and Steward Agent's
    universal monitoring interface.

    CrewAI-Specific Handling:
        - Extracts reasoning from CrewOutput objects
        - Handles .raw and .content attributes
        - Injects feedback into agent context
        - Extracts role, goal, backstory from agents

    Attributes:
        logger: Logger instance
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize CrewAI Adapter.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

        if not CREWAI_AVAILABLE:
            self.logger.warning(
                "CrewAI is not installed. CrewAIAdapter will not support any agents. "
                "Install with: pip install crewai"
            )
        else:
            self.logger.debug("CrewAIAdapter initialized with CrewAI support")

    def supports_agent(self, agent: Any) -> bool:
        """
        Check if agent is a CrewAI Agent, Crew, or Task.

        Args:
            agent: Object to check

        Returns:
            True if agent is from CrewAI framework
        """
        if not CREWAI_AVAILABLE:
            return False

        is_supported = isinstance(agent, (Agent, CrewAIAgent, Crew, Task))

        if not is_supported:
            self.logger.debug(
                f"Agent type {type(agent).__name__} is not a CrewAI agent"
            )

        return is_supported

    def get_execution_methods(self) -> list:
        """
        Return list of method names that trigger CrewAI agent execution.

        CrewAI agents use:
            - execute(): Generic execution method
            - kickoff(): Main CrewAI execution method

        Returns:
            List of method names to monitor: ['execute', 'kickoff']
        """
        return ['execute', 'kickoff']

    def extract_reasoning(
        self,
        agent: Any,
        execution_result: Any,
        execution_context: Optional[AgentExecutionContext] = None
    ) -> AgentReasoningTrace:
        """
        Extract reasoning trace from CrewAI execution result.

        Handles CrewAI-specific output formats:
            - CrewOutput objects (has .raw, .content)
            - TaskOutput objects
            - String outputs
            - Dict outputs

        Args:
            agent: CrewAI agent that executed
            execution_result: Result from agent execution
            execution_context: Optional execution context

        Returns:
            AgentReasoningTrace with extracted information
        """
        # Extract agent name and type
        agent_name = self._get_agent_name(agent)
        agent_type = self._get_agent_type(agent)

        # Extract reasoning and output from CrewAI result
        reasoning_text, final_output = self._extract_from_crew_output(execution_result)

        # Get goal
        goal = ""
        if execution_context:
            goal = execution_context.goal or execution_context.task or ""
        elif hasattr(agent, 'goal'):
            goal = str(agent.goal)

        # Create reasoning trace
        trace = AgentReasoningTrace(
            agent_name=agent_name,
            agent_type=agent_type,
            reasoning_text=reasoning_text,
            final_output=final_output,
            goal=goal,
            context_information=self._extract_context_info(agent, execution_context)
        )

        self.logger.debug(
            f"Extracted CrewAI reasoning trace for {agent_name}: "
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
        Inject Steward Agent feedback into CrewAI agent.

        Strategy:
            1. If agent has context attribute, append feedback
            2. If agent has memory, add to memory
            3. Otherwise, log warning

        Args:
            agent: CrewAI agent to inject feedback into
            feedback: Feedback from Steward Agent
            execution_context: Optional execution context
        """
        feedback_text = self._feedback_to_string(feedback)

        injected = False

        # Strategy 1: Agent has context
        if hasattr(agent, 'context') and agent.context is not None:
            if isinstance(agent.context, list):
                agent.context.append(feedback_text)
                injected = True
                self.logger.debug("Feedback injected into CrewAI agent.context")
            elif isinstance(agent.context, str):
                agent.context += f"\n\n{feedback_text}"
                injected = True
                self.logger.debug("Feedback appended to CrewAI agent.context string")

        # Strategy 2: Agent has memory
        if not injected and hasattr(agent, 'memory'):
            try:
                agent.memory.add(feedback_text)
                injected = True
                self.logger.debug("Feedback added to CrewAI agent.memory")
            except Exception as e:
                self.logger.debug(f"Could not add to agent.memory: {e}")

        # Fallback: Log warning
        if not injected:
            self.logger.warning(
                f"Could not inject feedback into CrewAI agent {agent_name}. "
                f"Agent has no compatible context or memory attribute."
            )

    def get_agent_metadata(self, agent: Any) -> Dict[str, Any]:
        """
        Extract metadata from CrewAI agent.

        Extracts:
            - role: Agent's role
            - goal: Agent's goal
            - backstory: Agent's backstory
            - verbose: Verbosity setting
            - allow_delegation: Delegation setting
            - tools: Available tools

        Args:
            agent: CrewAI agent

        Returns:
            Dictionary with agent metadata
        """
        metadata = {
            'framework': 'crewai',
            'adapter': 'CrewAIAdapter',
            'agent_name': self._get_agent_name(agent),
            'agent_type': self._get_agent_type(agent),
            'agent_class': type(agent).__name__,
        }

        # Extract CrewAI-specific attributes
        if hasattr(agent, 'role'):
            metadata['role'] = str(agent.role)
        if hasattr(agent, 'goal'):
            metadata['goal'] = str(agent.goal)
        if hasattr(agent, 'backstory'):
            metadata['backstory'] = str(agent.backstory)[:200]  # Limit length
        if hasattr(agent, 'verbose'):
            metadata['verbose'] = agent.verbose
        if hasattr(agent, 'allow_delegation'):
            metadata['allow_delegation'] = agent.allow_delegation
        if hasattr(agent, 'tools'):
            metadata['tools_count'] = len(agent.tools) if agent.tools else 0

        self.logger.debug(f"Extracted metadata for CrewAI agent {metadata['agent_name']}")

        return metadata

    # ========================================
    # Helper Methods
    # ========================================

    def _get_agent_name(self, agent: Any) -> str:
        """Get agent name from CrewAI agent."""
        if hasattr(agent, 'role'):
            return str(agent.role)
        if hasattr(agent, 'name'):
            return str(agent.name)
        return type(agent).__name__

    def _get_agent_type(self, agent: Any) -> str:
        """Determine agent type from CrewAI agent."""
        # Check if it's a planner or executor based on role/goal
        if hasattr(agent, 'role'):
            role = str(agent.role).lower()
            if 'plan' in role or 'manager' in role or 'coordinator' in role:
                return 'planner'
            return 'executor'
        return 'generic'

    def _extract_from_crew_output(self, result: Any) -> tuple[str, str]:
        """
        Extract reasoning and output from CrewAI result.

        Handles different CrewAI output formats.

        Returns:
            Tuple of (reasoning_text, final_output)
        """
        reasoning_text = ""
        final_output = ""

        # Case 1: CrewOutput object (has .raw attribute)
        if hasattr(result, 'raw'):
            final_output = str(result.raw)
            reasoning_text = f"CrewAI Output (raw): {final_output}"

        # Case 2: Has .content attribute
        elif hasattr(result, 'content'):
            final_output = str(result.content)
            reasoning_text = f"CrewAI Output (content): {final_output}"

        # Case 3: TaskOutput object
        elif hasattr(result, 'output'):
            final_output = str(result.output)
            if hasattr(result, 'description'):
                reasoning_text = f"Task: {result.description}\nOutput: {final_output}"
            else:
                reasoning_text = f"Task Output: {final_output}"

        # Case 4: Dictionary
        elif isinstance(result, dict):
            final_output = str(result.get('output', result.get('result', str(result))))
            reasoning_text = str(result.get('reasoning', f"CrewAI result: {final_output}"))

        # Case 5: String or other
        else:
            final_output = str(result)
            reasoning_text = f"CrewAI execution result: {final_output}"

        return reasoning_text, final_output

    def _extract_context_info(
        self,
        agent: Any,
        execution_context: Optional[AgentExecutionContext]
    ) -> Dict[str, Any]:
        """Extract context information for reasoning trace."""
        context_info = {
            'adapter': 'CrewAIAdapter',
            'framework': 'crewai',
        }

        if execution_context:
            context_info['execution_context'] = {
                'agent_id': execution_context.agent_id,
                'task': execution_context.task,
            }

        # Add CrewAI-specific context
        if hasattr(agent, 'role'):
            context_info['agent_role'] = str(agent.role)
        if hasattr(agent, 'goal'):
            context_info['agent_goal'] = str(agent.goal)

        return context_info

    def _feedback_to_string(self, feedback: Union[SocraticNudge, HITLAlert, str]) -> str:
        """Convert feedback to string representation."""
        if isinstance(feedback, str):
            return feedback
        elif isinstance(feedback, SocraticNudge):
            return f"[Steward Agent - Socratic Nudge]\n{feedback.question}"
        elif isinstance(feedback, HITLAlert):
            return f"[Steward Agent - HITL Alert]\n{feedback.alert_message}\nPriority: {feedback.priority}"
        else:
            return str(feedback)


__all__ = ['CrewAIAdapter']
