"""Repository interfaces (following Interface Segregation Principle)."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from domain.entities.patient import Patient
from domain.entities.appointment import Appointment
from domain.value_objects.time_slot import TimeSlot


class PatientRepository(ABC):
    """Patient repository interface."""
    
    @abstractmethod
    async def create(self, patient: Patient) -> Patient:
        """Create a new patient."""
        pass
    
    @abstractmethod
    async def get_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID."""
        pass
    
    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[Patient]:
        """Get patient by phone number."""
        pass
    
    @abstractmethod
    async def update(self, patient: Patient) -> Patient:
        """Update patient."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Patient]:
        """List all patients."""
        pass


class AppointmentRepository(ABC):
    """Appointment repository interface."""
    
    @abstractmethod
    async def create(self, appointment: Appointment) -> Appointment:
        """Create a new appointment."""
        pass
    
    @abstractmethod
    async def get_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        pass
    
    @abstractmethod
    async def get_by_patient_id(self, patient_id: str) -> List[Appointment]:
        """Get appointments for a patient."""
        pass
    
    @abstractmethod
    async def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 30
    ) -> List[TimeSlot]:
        """Get available time slots."""
        pass
    
    @abstractmethod
    async def update(self, appointment: Appointment) -> Appointment:
        """Update appointment."""
        pass
    
    @abstractmethod
    async def cancel(self, appointment_id: str) -> bool:
        """Cancel an appointment."""
        pass

