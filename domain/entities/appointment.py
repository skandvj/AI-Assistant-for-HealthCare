"""Appointment entity."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AppointmentType(str, Enum):
    """Appointment type enumeration."""
    
    CLEANING = "cleaning"
    CHECKUP = "checkup"
    EMERGENCY = "emergency"


class AppointmentStatus(str, Enum):
    """Appointment status enumeration."""
    
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(BaseModel):
    """Appointment domain entity."""
    
    id: Optional[str] = None
    patient_id: str = Field(..., description="Patient ID")
    appointment_type: AppointmentType = Field(..., description="Type of appointment")
    scheduled_time: datetime = Field(..., description="Scheduled appointment time")
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED, description="Appointment status")
    emergency_details: Optional[str] = Field(None, description="Emergency details if applicable")
    staff_notified: bool = Field(default=False, description="Whether staff was notified")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @field_validator('scheduled_time')
    @classmethod
    def validate_scheduled_time(cls, v: datetime) -> datetime:
        """Validate scheduled time is in the future."""
        if v < datetime.now():
            raise ValueError("Appointment time must be in the future")
        return v
    
    def is_emergency(self) -> bool:
        """Check if appointment is an emergency."""
        return self.appointment_type == AppointmentType.EMERGENCY
    
    def requires_staff_notification(self) -> bool:
        """Check if staff notification is required."""
        return self.is_emergency() and not self.staff_notified
    
    def can_be_cancelled(self) -> bool:
        """Check if appointment can be cancelled."""
        return self.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
    
    def can_be_rescheduled(self) -> bool:
        """Check if appointment can be rescheduled."""
        return self.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "apt_123",
                "patient_id": "pat_123",
                "appointment_type": "cleaning",
                "scheduled_time": "2024-01-15T10:00:00",
                "status": "scheduled",
                "emergency_details": None,
                "staff_notified": False
            }
        }

