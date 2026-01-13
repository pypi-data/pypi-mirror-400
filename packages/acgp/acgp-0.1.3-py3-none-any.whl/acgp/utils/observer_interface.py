"""
Observer Pattern Interfaces for Steward Agent System

Defines the interfaces for implementing proper observer pattern between
Steward Agent and agent wrappers, replacing the current callback-based system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

try:
    from .data_models import AgentReasoningTrace, ConversationEntry
except ImportError:
    from data_models import AgentReasoningTrace, ConversationEntry


class StewardEventType(Enum):
    """Types of events that can be observed by Steward Agent."""
    
    REASONING_TRACE = "reasoning_trace"
    CONVERSATION_ENTRY = "conversation_entry"
    AGENT_START = "agent_start"
    AGENT_COMPLETE = "agent_complete"
    FEEDBACK_REQUEST = "feedback_request"
    ERROR_OCCURRED = "error_occurred"
    QUALITY_GATE_STATS = "quality_gate_stats"


class StewardEvent:
    """
    Event data structure for Steward Agent observations.
    """
    
    def __init__(
        self,
        event_type: StewardEventType,
        agent_type: str,
        agent_tag: str,
        data: Any,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Steward Event.
        
        Args:
            event_type: Type of event
            agent_type: Agent type ('planner' or 'executor')
            agent_tag: Agent tag ('A' or 'B')
            data: Event data (reasoning trace, conversation entry, etc.)
            timestamp: Event timestamp (defaults to now)
            metadata: Additional metadata
        """
        self.event_type = event_type
        self.agent_type = agent_type
        self.agent_tag = agent_tag
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        
        # Generate unique event ID
        self.event_id = f"{agent_tag}_{event_type.value}_{int(self.timestamp.timestamp()*1000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "agent_type": self.agent_type,
            "agent_tag": self.agent_tag,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "data": self._serialize_data()
        }
    
    def _serialize_data(self) -> Any:
        """Serialize event data for JSON."""
        if isinstance(self.data, (AgentReasoningTrace, ConversationEntry)):
            return self.data.to_dict() if hasattr(self.data, 'to_dict') else self.data.__dict__
        elif hasattr(self.data, '__dict__'):
            return self.data.__dict__
        else:
            return self.data


class IStewardAgentObserver(ABC):
    """
    Interface for Steward Agent observers.
    
    Objects implementing this interface can observe and react to agent events.
    """
    
    @abstractmethod
    def on_agent_event(self, event: StewardEvent) -> None:
        """
        Handle an agent event.
        
        Args:
            event: The event that occurred
        """
        pass
    
    @abstractmethod
    def get_observer_id(self) -> str:
        """
        Get unique identifier for this observer.
        
        Returns:
            Unique observer identifier
        """
        pass
    
    @abstractmethod
    def is_interested_in_event(self, event_type: StewardEventType, agent_tag: str) -> bool:
        """
        Check if this observer is interested in a specific event type.
        
        Args:
            event_type: Type of event
            agent_tag: Agent tag that generated the event
            
        Returns:
            True if interested, False otherwise
        """
        pass


class IObservableAgent(ABC):
    """
    Interface for agents that can be observed.
    
    Agent wrappers implement this interface to allow observers to register.
    """
    
    @abstractmethod
    def register_observer(self, observer: IStewardAgentObserver) -> None:
        """
        Register an observer for this agent.
        
        Args:
            observer: Observer to register
        """
        pass
    
    @abstractmethod
    def unregister_observer(self, observer_id: str) -> bool:
        """
        Unregister an observer by ID.
        
        Args:
            observer_id: ID of observer to unregister
            
        Returns:
            True if observer was found and removed
        """
        pass
    
    @abstractmethod
    def notify_observers(self, event: StewardEvent) -> None:
        """
        Notify all registered observers of an event.
        
        Args:
            event: Event to broadcast
        """
        pass
    
    @abstractmethod
    def get_registered_observers(self) -> List[str]:
        """
        Get list of registered observer IDs.
        
        Returns:
            List of observer IDs
        """
        pass


class ObservableAgentMixin(IObservableAgent):
    """
    Mixin class that provides observable functionality to agent wrappers.
    
    Agent wrappers can inherit from this to get observer management functionality.
    """
    
    def __init__(self):
        """Initialize observable functionality."""
        self._observers: Dict[str, IStewardAgentObserver] = {}
        self._event_queue: List[StewardEvent] = []
        self._max_event_history = 100
    
    def register_observer(self, observer: IStewardAgentObserver) -> None:
        """Register an observer."""
        observer_id = observer.get_observer_id()
        self._observers[observer_id] = observer
        
        # Log registration if logger is available
        if hasattr(self, 'logger'):
            self.logger.info(f"Registered observer: {observer_id}")
    
    def unregister_observer(self, observer_id: str) -> bool:
        """Unregister an observer."""
        if observer_id in self._observers:
            del self._observers[observer_id]
            
            # Log unregistration if logger is available
            if hasattr(self, 'logger'):
                self.logger.info(f"Unregistered observer: {observer_id}")
            
            return True
        return False
    
    def notify_observers(self, event: StewardEvent) -> None:
        """Notify all registered observers."""
        # Store event in history
        self._event_queue.append(event)
        if len(self._event_queue) > self._max_event_history:
            self._event_queue = self._event_queue[-self._max_event_history:]
        
        # Notify interested observers
        for observer_id, observer in list(self._observers.items()):
            try:
                if observer.is_interested_in_event(event.event_type, event.agent_tag):
                    observer.on_agent_event(event)
            except Exception as e:
                # Log error if logger available, but don't break other observers
                if hasattr(self, 'logger'):
                    self.logger.error(f"Error notifying observer {observer_id}: {str(e)}")
    
    def get_registered_observers(self) -> List[str]:
        """Get list of registered observer IDs."""
        return list(self._observers.keys())
    
    def create_event(
        self,
        event_type: StewardEventType,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StewardEvent:
        """
        Create an event for this agent.
        
        Args:
            event_type: Type of event
            data: Event data
            metadata: Additional metadata
            
        Returns:
            Created event
        """
        return StewardEvent(
            event_type=event_type,
            agent_type=getattr(self, 'agent_type', 'unknown'),
            agent_tag=getattr(self, 'agent_tag', 'unknown'),
            data=data,
            metadata=metadata
        )
    
    def get_recent_events(self, limit: int = 10) -> List[StewardEvent]:
        """Get recent events for debugging/monitoring."""
        return self._event_queue[-limit:] if self._event_queue else []