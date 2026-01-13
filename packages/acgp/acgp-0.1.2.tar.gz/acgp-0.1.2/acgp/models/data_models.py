"""
Data Models for Steward Agent System

Pydantic data models for structured data exchange between components
and integration with Streamlit dashboard.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

try:
    from ..core.config.ctq_thresholds import OversightModeType
except (ImportError, ValueError):
    # Fallback for different execution contexts (client_examples/, direct execution, etc.)
    try:
        from core.config.ctq_thresholds import OversightModeType
    except ImportError:
        # Last resort: add src to path and try again
        import sys
        import os
        src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from core.config.ctq_thresholds import OversightModeType


class AgentReasoningTrace(BaseModel):
    """
    Represents a reasoning trace from an agent (Planner A or Executor B).
    
    This model captures both internal reasoning and final output for CTQ calculation
    and oversight mode determination. CTQ components evaluate the final_output field
    to measure the quality of what users actually receive.
    """
    step_id: str = Field(..., description="Unique identifier for this reasoning step")
    agent_type: str = Field(..., description="Type of agent: 'planner' or 'executor'")
    agent_tag: str = Field(..., description="Agent tag: 'A' for planner, 'B' for executor")
    user_query: str = Field(..., description="Original user query/request that initiated this agent task - enables Steward Agent to assess if query itself has sufficient information for blueprint compliance")
    goal: str = Field(..., description="The goal the agent is working towards (may be refined/clarified from user_query)")
    reasoning_text: str = Field(..., description="The agent's reasoning for this step")
    context_information: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional context and information"
    )
    step_number: int = Field(..., description="Sequential step number in the task")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this step occurred")
    
    # Final output fields for CTQ evaluation and user delivery
    final_output: Optional[str] = Field(None, description="The agent's final output/deliverable sent to users - used for CTQ calculation")
    output_type: Optional[str] = Field(None, description="Type of output: 'plan', 'execution_result', 'analysis', 'recommendation'")
    output_quality_metrics: Optional[Dict[str, Any]] = Field(
        None, 
        description="Structured metrics for output quality assessment"
    )
    
    # Document context fields
    documents_used: Optional[List[str]] = Field(None, description="List of document filenames used for context")
    document_context_quality: Optional[str] = Field(None, description="Quality assessment of document context")
    similarity_scores: Optional[List[float]] = Field(None, description="Similarity scores for retrieved document chunks")
    context_source_count: Optional[int] = Field(None, description="Number of document sources used")
    context_chunk_count: Optional[int] = Field(None, description="Number of document chunks retrieved")
    avg_similarity_score: Optional[float] = Field(None, description="Average similarity score across all chunks")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_dashboard_display_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        return {
            "step_id": self.step_id,
            "agent": f"{self.agent_type.title()} ({self.agent_tag})",
            "goal_preview": self.goal[:100] + "..." if len(self.goal) > 100 else self.goal,
            "reasoning_preview": self.reasoning_text[:150] + "..." if len(self.reasoning_text) > 150 else self.reasoning_text,
            "step_number": self.step_number,
            "timestamp": self.timestamp.strftime("%H:%M:%S")
        }


class CTQScore(BaseModel):
    """
    Represents a calculated Reasoning Quality Score with component breakdown.
    
    Unified 3-component specification:
    CTQ = (Goal_Coherence * weight) + (Context_Consistency * weight) + (Information_Completeness * weight)
    
    Component weights are configurable per agent type and must sum to 1.0.
    Both planner and executor agents use the same 3 components for consistency.
    """
    goal_coherence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Goal coherence component score (0-1)"
    )
    context_consistency_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Context consistency component score (0-1)"
    )
    information_completeness_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Information completeness component score (0-1)"
    )
    total_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Calculated total CTQ score"
    )
    component_weights: Dict[str, float] = Field(
        ..., 
        description="Weights used for component calculation"
    )
    calculation_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional calculation details and metadata"
    )
    calculation_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this score was calculated"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_quality_assessment(self) -> str:
        """Get human-readable quality assessment."""
        if self.total_score > 0.7:
            return "High Quality"
        elif self.total_score >= 0.5:
            return "Medium Quality"
        else:
            return "Low Quality"
    
    def get_dashboard_display_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        return {
            "total_score": round(self.total_score, 3),
            "quality_level": self.get_quality_assessment(),
            "components": {
                "goal_coherence": {
                    "score": round(self.goal_coherence_score, 3),
                    "weight": self.component_weights.get("goal_coherence", 0.33),
                    "contribution": round(self.goal_coherence_score * self.component_weights.get("goal_coherence", 0.33), 3)
                },
                "context_consistency": {
                    "score": round(self.context_consistency_score, 3),
                    "weight": self.component_weights.get("context_consistency", 0.33),
                    "contribution": round(self.context_consistency_score * self.component_weights.get("context_consistency", 0.33), 3)
                },
                "information_completeness": {
                    "score": round(self.information_completeness_score, 3),
                    "weight": self.component_weights.get("information_completeness", 0.34),
                    "contribution": round(self.information_completeness_score * self.component_weights.get("information_completeness", 0.34), 3)
                }
            },
            "timestamp": self.calculation_timestamp.strftime("%H:%M:%S")
        }


class OversightModeState(BaseModel):
    """
    Represents the current state of the oversight mode system.
    """
    current_mode: OversightModeType = Field(..., description="Currently active oversight mode")
    ctq_score: CTQScore = Field(..., description="CTQ score that determined this mode")
    mode_switched: bool = Field(..., description="Whether mode was switched in this update")
    previous_mode: Optional[OversightModeType] = Field(
        None, 
        description="Previous mode if a switch occurred"
    )
    processing_time_seconds: float = Field(
        ..., 
        description="Time taken to process this mode update"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="When this state was created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_dashboard_display_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        return {
            "current_mode": self.current_mode.value,
            "mode_display_name": self.current_mode.value.replace("_", " ").title(),
            "ctq_score": self.ctq_score.total_score,
            "mode_switched": self.mode_switched,
            "switch_info": f"Switched from {self.previous_mode.value}" if self.mode_switched and self.previous_mode else None,
            "processing_time_ms": round(self.processing_time_seconds * 1000, 2),
            "timestamp": self.timestamp.strftime("%H:%M:%S")
        }


class SocraticNudge(BaseModel):
    """
    Represents a Socratic nudge generated by the Steward Agent.
    """
    question: str = Field(..., description="The Socratic question to pose")
    context_summary: str = Field(..., description="Summary of relevant context")
    step_id: str = Field(..., description="ID of the step being nudged about")
    agent_type: str = Field(..., description="Type of agent receiving the nudge")
    suggested_reflection_areas: List[str] = Field(
        default_factory=list,
        description="Areas the agent should reflect on"
    )
    urgency_level: str = Field(default="medium", description="Urgency level: low, medium, high")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this nudge was generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_dashboard_display_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        return {
            "type": "Socratic Nudge",
            "question": self.question,
            "context": self.context_summary,
            "target_agent": f"{self.agent_type.title()}",
            "step_id": self.step_id,
            "urgency": self.urgency_level,
            "reflection_areas": self.suggested_reflection_areas,
            "timestamp": self.timestamp.strftime("%H:%M:%S")
        }


class HITLAlert(BaseModel):
    """
    Represents a Human-in-the-Loop alert for intervention.
    """
    alert_message: str = Field(..., description="Main alert message")
    ctq_score: float = Field(..., ge=0.0, le=1.0, description="CTQ score that triggered this alert")
    reasoning_issues: List[str] = Field(..., description="Identified issues with reasoning")
    recommended_action: str = Field(..., description="Recommended human action")
    step_id: str = Field(..., description="ID of the step requiring intervention")
    agent_type: str = Field(..., description="Type of agent that triggered the alert")
    step_reasoning: str = Field(default="", description="The actual reasoning text that triggered this alert")
    step_summary: str = Field(default="", description="Brief summary of the problematic step")
    context_information: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for human reviewer"
    )
    priority: str = Field(default="medium", description="Alert priority: low, medium, high, critical")
    requires_immediate_attention: bool = Field(
        default=False,
        description="Whether this alert requires immediate attention"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="When this alert was generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_dashboard_display_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        display_data = {
            "type": "HITL Alert",
            "message": self.alert_message,
            "ctq_score": round(self.ctq_score, 3),
            "issues": self.reasoning_issues,
            "recommended_action": self.recommended_action,
            "target_agent": f"{self.agent_type.title()}",
            "step_id": self.step_id,
            "step_summary": self.step_summary,
            "step_reasoning": self.step_reasoning[:500] + "..." if len(self.step_reasoning) > 500 else self.step_reasoning,
            "step_reasoning_full": self.step_reasoning,  # Full reasoning for detailed view
            "priority": self.priority,
            "urgent": self.requires_immediate_attention,
            "timestamp": self.timestamp.strftime("%H:%M:%S")
        }
        
        # Enhanced display for healthcare alerts with rich context
        if self.context_information.get("healthcare_context"):
            display_data.update({
                "healthcare_enhanced": True,
                "intervention_type": self.context_information.get("intervention_trigger", "unknown"),
                "quality_analysis": self.context_information.get("quality_analysis", {}),
                "review_guidance": self.context_information.get("review_guidance", {}),
                "agent_details": self.context_information.get("agent_details", {}),
                "ctq_breakdown": self.context_information.get("ctq_breakdown", {}),
                "ctq_threshold": self.context_information.get("ctq_threshold", 0.8)
            })
        
        return display_data
    
    def get_human_readable_summary(self) -> str:
        """Get a concise, human-readable summary of the alert (no emojis in JSON)."""
        if self.context_information.get("healthcare_context"):
            quality_analysis = self.context_information.get("quality_analysis", {})
            severity = quality_analysis.get("severity_level", "unknown")
            gap = quality_analysis.get("threshold_gap", 0)
            
            return (
                f"Medical Quality Alert - {self.agent_type.title()} agent reasoning "
                f"quality dropped {gap:.3f} points below safety threshold. "
                f"Severity: {severity.upper()}. Click to review agent's reasoning and provide guidance."
            )
        else:
            return f"{self.alert_message} - CTQ: {self.ctq_score:.3f}"


@dataclass
class DashboardState:
    """
    Aggregated state information for Streamlit dashboard display.
    """
    current_oversight_mode: str
    current_ctq_score: float
    active_agent_count: int
    recent_activity: List[Dict[str, Any]]
    session_statistics: Dict[str, Any]
    recent_feedback: List[Dict[str, Any]]
    system_health: Dict[str, Any]
    last_update_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "oversight_mode": self.current_oversight_mode,
            "ctq_score": self.current_ctq_score,
            "active_agents": self.active_agent_count,
            "recent_activity": self.recent_activity,
            "statistics": self.session_statistics,
            "feedback": self.recent_feedback,
            "health": self.system_health,
            "timestamp": self.last_update_timestamp.isoformat()
        }


class AgentInteractionEvent(BaseModel):
    """
    Represents an interaction event between Steward Agent and monitored agents.
    """
    event_type: str = Field(..., description="Type of interaction: nudge, alert, mode_switch")
    source_agent: str = Field(..., description="Agent that triggered the event")
    target_agent: Optional[str] = Field(None, description="Agent receiving the interaction")
    event_data: Dict[str, Any] = Field(..., description="Event-specific data")
    processing_time_ms: float = Field(..., description="Time taken to process this event")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this event occurred")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_dashboard_display_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        return {
            "type": self.event_type,
            "source": self.source_agent,
            "target": self.target_agent,
            "data": self.event_data,
            "processing_time": self.processing_time_ms,
            "timestamp": self.timestamp.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        }


class ConversationEntry(BaseModel):
    """
    Represents a single entry in the conversation history between Agent A, Agent B, and Steward Agent.
    
    This model captures individual interactions and communications during pipeline execution.
    """
    timestamp: datetime = Field(default_factory=datetime.now, description="When this conversation entry occurred")
    participant: str = Field(..., description="Who generated this entry: 'Agent_A', 'Agent_B', or 'Steward_Agent'")
    message_type: str = Field(..., description="Type of message: 'reasoning_trace', 'ctq_calculation', 'feedback_delivery', 'enhanced_execution', 'mode_switch', 'nudge', 'alert'")
    content: str = Field(..., description="Main content of the conversation entry")
    phase: Optional[str] = Field(None, description="Execution phase: 'goal_analysis', 'task_breakdown', 'execution', 'validation'")
    
    # Additional context fields
    context_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context data specific to this conversation entry"
    )
    
    # Agent-specific fields
    agent_tag: Optional[str] = Field(None, description="Agent tag if participant is an agent: 'A' or 'B'")
    step_id: Optional[str] = Field(None, description="Associated reasoning step ID if applicable")
    
    # Steward Agent specific fields
    ctq_score: Optional[float] = Field(None, description="CTQ score if this is a Steward Agent calculation")
    oversight_mode: Optional[str] = Field(None, description="Oversight mode if this is Steward Agent feedback")
    mode_switched: Optional[bool] = Field(None, description="Whether mode was switched in this entry")
    
    # Feedback fields
    received_guidance: Optional[bool] = Field(None, description="Whether this entry involved receiving guidance")
    feedback_type: Optional[str] = Field(None, description="Type of feedback: 'socratic_nudge', 'wise_critic_suggestion', 'guardian_alert'")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_display_summary(self) -> str:
        """Get a concise summary for display purposes."""
        participant_display = {
            "Agent_A": "🤖 Agent A (Planner)",
            "Agent_B": "⚡ Agent B (Executor)", 
            "Steward_Agent": "👁️ Steward Agent"
        }.get(self.participant, self.participant)
        
        return f"{participant_display}: {self.content[:100]}{'...' if len(self.content) > 100 else ''}"


class ConversationHistory(BaseModel):
    """
    Represents the complete conversation history for a pipeline execution.
    
    This model aggregates all interactions between Agent A, Agent B, and Steward Agent
    in chronological order to provide complete visibility into the execution flow.
    """
    pipeline_id: str = Field(..., description="Unique identifier for the pipeline execution")
    start_time: datetime = Field(default_factory=datetime.now, description="When the conversation started")
    end_time: Optional[datetime] = Field(None, description="When the conversation ended")
    
    entries: List[ConversationEntry] = Field(
        default_factory=list,
        description="Chronologically ordered conversation entries"
    )
    
    # Summary statistics
    total_entries: int = Field(default=0, description="Total number of conversation entries")
    agent_a_entries: int = Field(default=0, description="Number of entries from Agent A")
    agent_b_entries: int = Field(default=0, description="Number of entries from Agent B") 
    steward_agent_entries: int = Field(default=0, description="Number of entries from Steward Agent")
    
    # Interaction summary
    ctq_calculations: int = Field(default=0, description="Number of CTQ calculations performed")
    feedback_deliveries: int = Field(default=0, description="Number of feedback deliveries")
    mode_switches: int = Field(default=0, description="Number of oversight mode switches")
    nudges_generated: int = Field(default=0, description="Number of socratic nudges generated")
    alerts_generated: int = Field(default=0, description="Number of HITL alerts generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_entry(self, entry: ConversationEntry) -> None:
        """Add a conversation entry and update statistics."""
        self.entries.append(entry)
        self.total_entries += 1
        
        # Update participant counts
        if entry.participant == "Agent_A":
            self.agent_a_entries += 1
        elif entry.participant == "Agent_B":
            self.agent_b_entries += 1
        elif entry.participant == "Steward_Agent":
            self.steward_agent_entries += 1
        
        # Update interaction counts
        if entry.message_type == "ctq_calculation":
            self.ctq_calculations += 1
        elif entry.message_type == "feedback_delivery":
            self.feedback_deliveries += 1
        elif entry.message_type == "mode_switch":
            self.mode_switches += 1
        elif entry.feedback_type == "socratic_nudge":
            self.nudges_generated += 1
        elif entry.feedback_type == "guardian_alert":
            self.alerts_generated += 1
    
    def finalize(self) -> None:
        """Mark the conversation as complete."""
        self.end_time = datetime.now()
        
        # Sort entries by timestamp to ensure chronological order
        self.entries.sort(key=lambda x: x.timestamp)
    
    def get_entries_by_participant(self, participant: str) -> List[ConversationEntry]:
        """Get all entries from a specific participant.""" 
        return [entry for entry in self.entries if entry.participant == participant]
    
    def get_entries_by_type(self, message_type: str) -> List[ConversationEntry]:
        """Get all entries of a specific message type."""
        return [entry for entry in self.entries if entry.message_type == message_type]
    
    def get_timeline_summary(self) -> List[Dict[str, Any]]:
        """Get a timeline summary of key events."""
        timeline = []
        
        for entry in self.entries:
            if entry.message_type in ["ctq_calculation", "mode_switch", "feedback_delivery"]:
                timeline.append({
                    "timestamp": entry.timestamp,
                    "participant": entry.participant,
                    "event": entry.message_type,
                    "summary": entry.get_display_summary(),
                    "ctq_score": entry.ctq_score,
                    "oversight_mode": entry.oversight_mode
                })
        
        return timeline
    
    def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive conversation statistics."""
        duration_seconds = 0
        if self.end_time and self.start_time:
            duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        return {
            "pipeline_id": self.pipeline_id,
            "duration_seconds": duration_seconds,
            "total_entries": self.total_entries,
            "participant_breakdown": {
                "Agent_A": self.agent_a_entries,
                "Agent_B": self.agent_b_entries,
                "Steward_Agent": self.steward_agent_entries
            },
            "interaction_summary": {
                "ctq_calculations": self.ctq_calculations,
                "feedback_deliveries": self.feedback_deliveries,
                "mode_switches": self.mode_switches,
                "nudges_generated": self.nudges_generated,
                "alerts_generated": self.alerts_generated
            },
            "conversation_flow": {
                "bidirectional_exchanges": self.feedback_deliveries,
                "steward_interventions": self.nudges_generated + self.alerts_generated,
                "average_entries_per_minute": round(self.total_entries / (duration_seconds / 60), 2) if duration_seconds > 0 else 0
            }
        }