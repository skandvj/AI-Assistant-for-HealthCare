"""JSON-based repository implementation."""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path
import aiofiles

from domain.entities.patient import Patient
from domain.entities.appointment import Appointment, AppointmentStatus
from domain.value_objects.time_slot import TimeSlot
from .repository import PatientRepository, AppointmentRepository


class JSONPatientRepository(PatientRepository):
    """JSON-based patient repository."""
    
    def __init__(self, db_path: str = "./data/database.json"):
        """Initialize repository with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def _load_data(self) -> dict:
        """Load data from JSON file."""
        if not self.db_path.exists():
            return {"patients": [], "appointments": []}
        
        async with aiofiles.open(self.db_path, "r") as f:
            content = await f.read()
            return json.loads(content) if content else {"patients": [], "appointments": []}
    
    async def _save_data(self, data: dict) -> None:
        """Save data to JSON file."""
        async with aiofiles.open(self.db_path, "w") as f:
            await f.write(json.dumps(data, indent=2, default=str))
    
    async def create(self, patient: Patient) -> Patient:
        """Create a new patient."""
        if not patient.id:
            patient.id = f"pat_{uuid.uuid4().hex[:8]}"
        
        if not patient.created_at:
            patient.created_at = datetime.now().date()
        
        data = await self._load_data()
        patient_dict = patient.model_dump(mode="json")
        patient_dict["date_of_birth"] = str(patient.date_of_birth)
        patient_dict["created_at"] = str(patient.created_at) if patient.created_at else None
        
        data["patients"].append(patient_dict)
        await self._save_data(data)
        
        return patient
    
    async def get_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID."""
        data = await self._load_data()
        for patient_dict in data.get("patients", []):
            if patient_dict.get("id") == patient_id:
                return Patient(**patient_dict)
        return None
    
    async def get_by_phone(self, phone: str) -> Optional[Patient]:
        """Get patient by phone number."""
        data = await self._load_data()
        for patient_dict in data.get("patients", []):
            if patient_dict.get("phone") == phone:
                return Patient(**patient_dict)
        return None
    
    async def update(self, patient: Patient) -> Patient:
        """Update patient."""
        data = await self._load_data()
        for i, patient_dict in enumerate(data.get("patients", [])):
            if patient_dict.get("id") == patient.id:
                patient_dict = patient.model_dump(mode="json")
                patient_dict["date_of_birth"] = str(patient.date_of_birth)
                patient_dict["created_at"] = str(patient.created_at) if patient.created_at else None
                data["patients"][i] = patient_dict
                await self._save_data(data)
                return patient
        raise ValueError(f"Patient {patient.id} not found")
    
    async def list_all(self) -> List[Patient]:
        """List all patients."""
        data = await self._load_data()
        return [Patient(**p) for p in data.get("patients", [])]


class JSONAppointmentRepository(AppointmentRepository):
    """JSON-based appointment repository."""
    
    def __init__(self, db_path: str = "./data/database.json"):
        """Initialize repository with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def _load_data(self) -> dict:
        """Load data from JSON file."""
        if not self.db_path.exists():
            return {"patients": [], "appointments": []}
        
        async with aiofiles.open(self.db_path, "r") as f:
            content = await f.read()
            return json.loads(content) if content else {"patients": [], "appointments": []}
    
    async def _save_data(self, data: dict) -> None:
        """Save data to JSON file."""
        async with aiofiles.open(self.db_path, "w") as f:
            await f.write(json.dumps(data, indent=2, default=str))
    
    async def create(self, appointment: Appointment) -> Appointment:
        """Create a new appointment."""
        if not appointment.id:
            appointment.id = f"apt_{uuid.uuid4().hex[:8]}"
        
        if not appointment.created_at:
            appointment.created_at = datetime.now()
        
        appointment.updated_at = datetime.now()
        
        data = await self._load_data()
        appointment_dict = appointment.model_dump(mode="json")
        appointment_dict["scheduled_time"] = appointment.scheduled_time.isoformat()
        appointment_dict["created_at"] = appointment.created_at.isoformat()
        appointment_dict["updated_at"] = appointment.updated_at.isoformat()
        
        data["appointments"].append(appointment_dict)
        await self._save_data(data)
        
        return appointment
    
    async def get_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        data = await self._load_data()
        for apt_dict in data.get("appointments", []):
            if apt_dict.get("id") == appointment_id:
                apt_dict["scheduled_time"] = datetime.fromisoformat(apt_dict["scheduled_time"])
                if apt_dict.get("created_at"):
                    apt_dict["created_at"] = datetime.fromisoformat(apt_dict["created_at"])
                if apt_dict.get("updated_at"):
                    apt_dict["updated_at"] = datetime.fromisoformat(apt_dict["updated_at"])
                return Appointment(**apt_dict)
        return None
    
    async def get_by_patient_id(self, patient_id: str) -> List[Appointment]:
        """Get appointments for a patient."""
        data = await self._load_data()
        appointments = []
        for apt_dict in data.get("appointments", []):
            if apt_dict.get("patient_id") == patient_id:
                apt_dict["scheduled_time"] = datetime.fromisoformat(apt_dict["scheduled_time"])
                if apt_dict.get("created_at"):
                    apt_dict["created_at"] = datetime.fromisoformat(apt_dict["created_at"])
                if apt_dict.get("updated_at"):
                    apt_dict["updated_at"] = datetime.fromisoformat(apt_dict["updated_at"])
                appointments.append(Appointment(**apt_dict))
        return appointments
    
    async def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 30
    ) -> List[TimeSlot]:
        """Get available time slots."""
        data = await self._load_data()
        
        # Get all booked appointments in the range
        booked_appointments = []
        for apt_dict in data.get("appointments", []):
            scheduled_time = datetime.fromisoformat(apt_dict["scheduled_time"])
            if start_date <= scheduled_time <= end_date:
                status = apt_dict.get("status", "scheduled")
                if status in ["scheduled", "confirmed"]:
                    booked_appointments.append(scheduled_time)
        
        # Generate available slots
        slots = []
        current = start_date.replace(hour=8, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=18, minute=0, second=0, microsecond=0)
        
        while current < end:
            # Skip weekends (Sunday = 6)
            if current.weekday() < 6:  # Mon-Sat
                slot_end = current + timedelta(minutes=duration_minutes)
                
                # Check if slot is available
                is_available = True
                for booked_time in booked_appointments:
                    if current <= booked_time < slot_end:
                        is_available = False
                        break
                
                if is_available and slot_end.hour <= 18:
                    slots.append(TimeSlot(
                        start_time=current,
                        end_time=slot_end,
                        is_available=True
                    ))
            
            current += timedelta(minutes=30)  # 30-minute intervals
        
        return slots
    
    async def update(self, appointment: Appointment) -> Appointment:
        """Update appointment."""
        data = await self._load_data()
        appointment.updated_at = datetime.now()
        
        for i, apt_dict in enumerate(data.get("appointments", [])):
            if apt_dict.get("id") == appointment.id:
                apt_dict = appointment.model_dump(mode="json")
                apt_dict["scheduled_time"] = appointment.scheduled_time.isoformat()
                apt_dict["created_at"] = appointment.created_at.isoformat() if appointment.created_at else None
                apt_dict["updated_at"] = appointment.updated_at.isoformat()
                data["appointments"][i] = apt_dict
                await self._save_data(data)
                return appointment
        raise ValueError(f"Appointment {appointment.id} not found")
    
    async def cancel(self, appointment_id: str) -> bool:
        """Cancel an appointment."""
        appointment = await self.get_by_id(appointment_id)
        if appointment and appointment.can_be_cancelled():
            appointment.status = AppointmentStatus.CANCELLED
            await self.update(appointment)
            return True
        return False

