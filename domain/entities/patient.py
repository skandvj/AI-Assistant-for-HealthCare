"""Patient entity."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Patient(BaseModel):
    """Patient domain entity."""
    
    id: Optional[str] = None
    full_name: str = Field(..., min_length=1, description="Patient's full name")
    phone: str = Field(..., description="Phone number")
    date_of_birth: date = Field(..., description="Date of birth")
    insurance_name: Optional[str] = Field(None, description="Insurance provider name")
    has_insurance: bool = Field(default=True, description="Whether patient has insurance")
    family_members: list[str] = Field(default_factory=list, description="IDs of family members")
    created_at: Optional[date] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Normalize phone number."""
        # Remove common formatting
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        # Return original format, validation passed
        return v
    
    def age(self) -> int:
        """Calculate patient age."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def is_new_patient(self) -> bool:
        """Check if patient is new (no appointments yet)."""
        return self.created_at is not None
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "pat_123",
                "full_name": "John Doe",
                "phone": "+1-555-0123",
                "date_of_birth": "1990-01-15",
                "insurance_name": "Blue Cross",
                "has_insurance": True,
                "family_members": []
            }
        }

