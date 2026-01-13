"""
Agent Protocol - Universal Interface for Framework-Agnostic Agent Monitoring

This module defines the protocol and adapter interface that enables Steward Agent
to monitor ANY agent framework (CrewAI, LangChain, AutoGen, custom agents, etc.)
without importing or depending on those frameworks.

Architecture:
    - MonitorableAgent: Protocol defining what makes an agent observable
    - AgentAdapter: Abstract base class for framework-specific adapters

Usage Example:
    ```python
    from src.wrapper import StewardAgentWrapper
    from src.adapters import CrewAIAdapter
    from src.core import StewardAgent

    # Your agent from any framework
    agent = MyFrameworkAgent(...)

    # Adapt and wrap it
    adapter = CrewAIAdapter()
    steward = StewardAgent()
    wrapped = StewardAgentWrapper(agent, adapter, steward)

    # Use normally - monitoring happens transparently
    result = wrapped.execute("task")
    ```

Zero Framework Dependencies:
    This module MUST NOT import any agent framework (crewai, langchain, etc.).
    Only standard library, typing, and internal Steward Agent components allowed.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Any, Dict, List, Optional, Union, runtime_checkable
from dataclasses import dataclass

try:
    from ..utils.data_models import AgentReasoningTrace, SocraticNudge, HITLAlert
except ImportError:
    from utils.data_models import AgentReasoningTrace, SocraticNudge, HITLAlert


@runtime_checkable
class MonitorableAgent(Protocol):
    """
    Protocol defining the minimum interface for an agent to be monitorable.

    Any agent that implements these methods can be wrapped by StewardAgentWrapper,
    regardless of which framework it comes from.

    Required Methods:
        execute(task): Execute a task and return result

    Optional Methods:
        plan(goal): Plan steps to achieve a goal (for planner agents)
        get_state(): Get current agent state/context

    Framework Examples:
        - CrewAI Agent: Has execute() via kickoff()
        - LangChain Agent: Has execute() via invoke()
        - AutoGen Agent: Has execute() via run()
        - Custom Agent: Implement execute() method

    Note: This is a Protocol, not a base class. Agents don't need to inherit it,
          they just need to implement the methods.
    """

    def execute(self, task: Union[str, Dict, Any]) -> Any:
        """
        Execute a task and return the result.

        Args:
            task: Task specification (string, dict, or framework-specific object)

        Returns:
            Result of task execution (framework-specific format)

        Note:
            Different frameworks call this method different names:
            - CrewAI: agent.kickoff()
            - LangChain: agent.invoke()
            - AutoGen: agent.run()

            Adapters normalize these to execute()
        """
        ...


@dataclass
class AgentExecutionContext:
    """
    Context information about an agent execution.

    Adapters extract this information from framework-specific objects
    and provide it in a normalized format.
    """
    agent_id: str
    agent_type: str  # "planner", "executor", "generic"
    framework: str  # "crewai", "langchain", "custom"
    goal: Optional[str] = None
    task: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentExecutionResult:
    """
    Normalized result from agent execution.

    Adapters convert framework-specific outputs to this format.
    """
    output: Any  # The actual result/output
    reasoning: Optional[str] = None  # Extracted reasoning text
    success: bool = True
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentAdapter(ABC):
    """
    Abstract base class for framework-specific adapters.

    Each adapter translates between a specific framework's agent implementation
    and Steward Agent's universal monitoring interface.

    Responsibilities:
        1. Extract reasoning traces from framework-specific outputs
        2. Inject Steward Agent feedback into framework agents
        3. Provide agent metadata for monitoring
        4. Determine if adapter supports a given agent

    Implementation Guide:
        Create a subclass for each framework (< 50 lines typically):

        ```python
        class MyFrameworkAdapter(AgentAdapter):
            def supports_agent(self, agent):
                return isinstance(agent, MyFrameworkAgentClass)

            def extract_reasoning(self, agent, execution_result):
                # Convert framework output to AgentReasoningTrace
                return AgentReasoningTrace(...)

            def inject_feedback(self, agent, feedback):
                # Add feedback to agent's context/memory
                agent.add_to_context(feedback)

            def get_agent_metadata(self, agent):
                return {
                    "framework": "myframework",
                    "agent_type": "executor",
                    ...
                }
        ```

    Adapter Examples:
        - CrewAIAdapter: Handles CrewAI Agent objects
        - LangChainAdapter: Handles LangChain agents
        - GenericAdapter: Handles any Python object with execute()
    """

    @abstractmethod
    def supports_agent(self, agent: Any) -> bool:
        """
        Check if this adapter can handle the given agent.

        Args:
            agent: Agent object to check

        Returns:
            True if this adapter supports the agent, False otherwise

        Example:
            ```python
            def supports_agent(self, agent):
                return isinstance(agent, CrewAIAgent)
            ```
        """
        pass

    @abstractmethod
    def get_execution_methods(self) -> List[str]:
        """
        Return list of method names that trigger agent execution.

        This allows the wrapper to be truly framework-agnostic by delegating
        the knowledge of which methods need monitoring to the adapter.

        Returns:
            List of method names to monitor (e.g., ['execute', 'kickoff'])

        Example:
            ```python
            # CrewAIAdapter
            def get_execution_methods(self):
                return ['execute', 'kickoff']

            # LangChainAdapter
            def get_execution_methods(self):
                return ['invoke', 'run']

            # GenericAdapter
            def get_execution_methods(self):
                return ['execute']
            ```

        Note:
            This removes hardcoded method names from the wrapper, making it
            truly framework-agnostic. New frameworks only need a new adapter,
            no wrapper changes required.
        """
        pass

    @abstractmethod
    def extract_reasoning(
        self,
        agent: Any,
        execution_result: Any,
        execution_context: Optional[AgentExecutionContext] = None
    ) -> AgentReasoningTrace:
        """
        Extract reasoning trace from agent execution result.

        This is the key method that converts framework-specific outputs
        into Steward Agent's universal AgentReasoningTrace format.

        Args:
            agent: The agent that executed
            execution_result: Framework-specific execution result
            execution_context: Optional context about the execution

        Returns:
            AgentReasoningTrace with extracted reasoning, output, metadata

        Example:
            ```python
            def extract_reasoning(self, agent, execution_result, context):
                return AgentReasoningTrace(
                    agent_name=agent.name,
                    agent_type="executor",
                    reasoning_text=execution_result.reasoning,
                    final_output=execution_result.output,
                    goal=context.goal if context else "",
                    context_information={"framework": "myframework"}
                )
            ```
        """
        pass

    @abstractmethod
    def inject_feedback(
        self,
        agent: Any,
        feedback: Union[SocraticNudge, HITLAlert, str],
        execution_context: Optional[AgentExecutionContext] = None
    ) -> None:
        """
        Inject Steward Agent feedback into the agent.

        Different frameworks have different ways to provide feedback:
        - Add to agent's context/memory
        - Modify agent's prompt
        - Store in agent's state

        Args:
            agent: Agent to inject feedback into
            feedback: Feedback from Steward Agent (nudge, alert, or raw text)
            execution_context: Optional context about the execution

        Example:
            ```python
            def inject_feedback(self, agent, feedback, context):
                if isinstance(feedback, SocraticNudge):
                    agent.add_to_context(feedback.message)
                elif isinstance(feedback, HITLAlert):
                    agent.pause_with_alert(feedback.message)
            ```
        """
        pass

    @abstractmethod
    def get_agent_metadata(self, agent: Any) -> Dict[str, Any]:
        """
        Extract metadata about the agent for monitoring.

        Args:
            agent: Agent to get metadata from

        Returns:
            Dictionary with agent metadata (framework, type, capabilities, etc.)

        Example:
            ```python
            def get_agent_metadata(self, agent):
                return {
                    "framework": "myframework",
                    "agent_type": "executor",
                    "agent_name": agent.name,
                    "capabilities": ["execute", "plan"],
                    "version": agent.version
                }
            ```
        """
        pass

    def normalize_execution_result(self, result: Any) -> AgentExecutionResult:
        """
        Convert framework-specific result to normalized format.

        Optional method - override if your framework needs custom normalization.

        Args:
            result: Framework-specific execution result

        Returns:
            Normalized AgentExecutionResult
        """
        return AgentExecutionResult(
            output=result,
            success=True,
            metadata={"raw_result": str(result)}
        )

    def create_execution_context(
        self,
        agent: Any,
        task: Any,
        goal: Optional[str] = None,
        **kwargs
    ) -> AgentExecutionContext:
        """
        Create execution context from agent and task.

        Optional method - override for custom context creation.

        Args:
            agent: Agent being executed
            task: Task being executed
            goal: Optional goal description
            **kwargs: Additional context parameters

        Returns:
            AgentExecutionContext with normalized information
        """
        metadata = self.get_agent_metadata(agent)
        return AgentExecutionContext(
            agent_id=metadata.get("agent_name", "unknown"),
            agent_type=metadata.get("agent_type", "generic"),
            framework=metadata.get("framework", "unknown"),
            goal=goal,
            task=str(task),
            context=kwargs,
            metadata=metadata
        )


__all__ = [
    'MonitorableAgent',
    'AgentAdapter',
    'AgentExecutionContext',
    'AgentExecutionResult',
]
