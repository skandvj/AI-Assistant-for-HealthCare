"""Conversation state value object."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ConversationIntent(str, Enum):
    """Conversation intent enumeration."""
    
    NEW_PATIENT_REGISTRATION = "new_patient_registration"
    EXISTING_PATIENT_APPOINTMENT = "existing_patient_appointment"
    FAMILY_SCHEDULING = "family_scheduling"
    GENERAL_INQUIRY = "general_inquiry"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"


class ConversationState(BaseModel):
    """Conversation state value object for LangGraph."""
    
    messages: list[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    intent: ConversationIntent = Field(default=ConversationIntent.UNKNOWN, description="Current intent")
    patient_id: Optional[str] = Field(None, description="Current patient ID")
    appointment_ids: list[str] = Field(default_factory=list, description="Appointment IDs in current session")
    collected_data: Dict[str, Any] = Field(default_factory=dict, description="Collected form data")
    current_step: Optional[str] = Field(None, description="Current conversation step")
    requires_human: bool = Field(default=False, description="Whether human intervention is needed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation."""
        self.messages.append({"role": role, "content": content})
    
    def update_collected_data(self, key: str, value: Any) -> None:
        """Update collected data."""
        self.collected_data[key] = value
    
    def get_collected_data(self, key: str, default: Any = None) -> Any:
        """Get collected data value."""
        return self.collected_data.get(key, default)
    
    def is_registration_complete(self) -> bool:
        """Check if patient registration is complete."""
        required_fields = ["full_name", "phone", "date_of_birth"]
        return all(field in self.collected_data for field in required_fields)
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "messages": [],
                "intent": "new_patient_registration",
                "patient_id": None,
                "appointment_ids": [],
                "collected_data": {},
                "current_step": "collecting_name"
            }
        }

