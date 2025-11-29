"""Appointment service (Service Layer Pattern)."""

from datetime import datetime
from typing import List, Optional

from domain.entities.appointment import Appointment, AppointmentType, AppointmentStatus
from domain.value_objects.time_slot import TimeSlot
from infrastructure.database.repository import AppointmentRepository, PatientRepository


class AppointmentService:
    """Appointment service for business logic."""
    
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: PatientRepository
    ):
        """Initialize service with repositories (Dependency Injection)."""
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository
    
    async def create_appointment(
        self,
        patient_id: str,
        appointment_type: str,
        scheduled_time: datetime,
        emergency_details: Optional[str] = None
    ) -> Appointment:
        """Create a new appointment."""
        # Verify patient exists
        patient = await self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Validate appointment type
        try:
            apt_type = AppointmentType(appointment_type.lower())
        except ValueError:
            raise ValueError(f"Invalid appointment type: {appointment_type}")
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            appointment_type=apt_type,
            scheduled_time=scheduled_time,
            emergency_details=emergency_details,
            staff_notified=apt_type == AppointmentType.EMERGENCY
        )
        
        return await self.appointment_repository.create(appointment)
    
    async def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        return await self.appointment_repository.get_by_id(appointment_id)
    
    async def get_patient_appointments(self, patient_id: str) -> List[Appointment]:
        """Get all appointments for a patient."""
        return await self.appointment_repository.get_by_patient_id(patient_id)
    
    async def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 30
    ) -> List[TimeSlot]:
        """Get available appointment slots."""
        return await self.appointment_repository.get_available_slots(
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration_minutes
        )
    
    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment."""
        return await self.appointment_repository.cancel(appointment_id)
    
    async def reschedule_appointment(
        self,
        appointment_id: str,
        new_time: datetime
    ) -> Appointment:
        """Reschedule an appointment."""
        appointment = await self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        if not appointment.can_be_rescheduled():
            raise ValueError(f"Appointment {appointment_id} cannot be rescheduled")
        
        appointment.scheduled_time = new_time
        appointment.updated_at = datetime.now()
        
        return await self.appointment_repository.update(appointment)
    
    async def suggest_alternative_times(
        self,
        preferred_date: datetime,
        duration_minutes: int = 30,
        days_ahead: int = 14
    ) -> List[TimeSlot]:
        """Suggest alternative appointment times."""
        start_date = preferred_date.replace(hour=8, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(day=start_date.day + days_ahead)
        
        return await self.get_available_slots(
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration_minutes
        )

