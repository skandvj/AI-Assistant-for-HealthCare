"""Time slot value object."""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field


class TimeSlot(BaseModel):
    """Time slot value object."""
    
    start_time: datetime = Field(..., description="Slot start time")
    end_time: datetime = Field(..., description="Slot end time")
    is_available: bool = Field(default=True, description="Whether slot is available")
    appointment_id: Optional[str] = Field(None, description="Associated appointment ID if booked")
    
    def duration_minutes(self) -> int:
        """Get duration in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    def overlaps_with(self, other: "TimeSlot") -> bool:
        """Check if this slot overlaps with another."""
        return (
            self.start_time < other.end_time and
            self.end_time > other.start_time
        )
    
    def is_business_hours(self, open_hour: int = 8, close_hour: int = 18) -> bool:
        """Check if slot is within business hours."""
        start_hour = self.start_time.hour
        end_hour = self.end_time.hour
        return open_hour <= start_hour < close_hour and open_hour < end_hour <= close_hour
    
    def is_weekday(self) -> bool:
        """Check if slot is on a weekday (Mon-Sat)."""
        weekday = self.start_time.weekday()
        return weekday < 6  # Monday=0, Saturday=5
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "start_time": "2024-01-15T10:00:00",
                "end_time": "2024-01-15T10:30:00",
                "is_available": True
            }
        }

