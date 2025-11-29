"""Initialize database with sample data."""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta, date
import aiofiles

from infrastructure.database import JSONPatientRepository, JSONAppointmentRepository
from domain.entities.patient import Patient
from domain.entities.appointment import Appointment, AppointmentType, AppointmentStatus


async def init_database():
    """Initialize database with sample data."""
    print("Initializing database...")
    
    # Create data directory
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize repositories
    patient_repo = JSONPatientRepository()
    appointment_repo = JSONAppointmentRepository()
    
    # Create sample patients
    sample_patients = [
        {
            "full_name": "John Smith",
            "phone": "+1-555-010-1234",
            "date_of_birth": date(1985, 5, 15),
            "insurance_name": "Blue Cross",
            "has_insurance": True
        },
        {
            "full_name": "Sarah Johnson",
            "phone": "+1-555-010-2345",
            "date_of_birth": date(1990, 8, 22),
            "insurance_name": "Aetna",
            "has_insurance": True
        },
        {
            "full_name": "Michael Chen",
            "phone": "+1-555-010-3456",
            "date_of_birth": date(1978, 3, 10),
            "insurance_name": None,
            "has_insurance": False
        },
    ]
    
    created_patients = []
    for patient_data in sample_patients:
        patient = Patient(**patient_data)
        created_patient = await patient_repo.create(patient)
        created_patients.append(created_patient)
        print(f"Created patient: {created_patient.full_name} (ID: {created_patient.id})")
    
    # Create sample appointments (some in the future)
    tomorrow = datetime.now() + timedelta(days=1)
    next_week = datetime.now() + timedelta(days=7)
    
    sample_appointments = [
        {
            "patient_id": created_patients[0].id,
            "appointment_type": AppointmentType.CLEANING,
            "scheduled_time": tomorrow.replace(hour=10, minute=0),
            "status": AppointmentStatus.SCHEDULED
        },
        {
            "patient_id": created_patients[1].id,
            "appointment_type": AppointmentType.CHECKUP,
            "scheduled_time": tomorrow.replace(hour=14, minute=0),
            "status": AppointmentStatus.CONFIRMED
        },
        {
            "patient_id": created_patients[0].id,
            "appointment_type": AppointmentType.CLEANING,
            "scheduled_time": next_week.replace(hour=11, minute=0),
            "status": AppointmentStatus.SCHEDULED
        },
    ]
    
    for apt_data in sample_appointments:
        appointment = Appointment(**apt_data)
        created_apt = await appointment_repo.create(appointment)
        print(f"Created appointment: {created_apt.id} for patient {created_apt.patient_id}")
    
    print("\nDatabase initialized successfully!")
    print(f"Created {len(created_patients)} patients and {len(sample_appointments)} appointments")


if __name__ == "__main__":
    asyncio.run(init_database())

