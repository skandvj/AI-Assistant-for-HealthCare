"""Patient service (Service Layer Pattern)."""

from datetime import date
from typing import Optional

from domain.entities.patient import Patient
from infrastructure.database.repository import PatientRepository


class PatientService:
    """Patient service for business logic."""
    
    def __init__(self, patient_repository: PatientRepository):
        """Initialize service with repository (Dependency Injection)."""
        self.patient_repository = patient_repository
    
    async def create_patient(
        self,
        full_name: str,
        phone: str,
        date_of_birth: date,
        insurance_name: Optional[str] = None,
        has_insurance: bool = True
    ) -> Patient:
        """Create a new patient."""
        patient = Patient(
            full_name=full_name,
            phone=phone,
            date_of_birth=date_of_birth,
            insurance_name=insurance_name,
            has_insurance=has_insurance
        )
        return await self.patient_repository.create(patient)
    
    async def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID."""
        return await self.patient_repository.get_by_id(patient_id)
    
    async def get_patient_by_phone(self, phone: str) -> Optional[Patient]:
        """Get patient by phone number."""
        return await self.patient_repository.get_by_phone(phone)
    
    async def update_patient(self, patient: Patient) -> Patient:
        """Update patient information."""
        return await self.patient_repository.update(patient)
    
    async def link_family_members(self, patient_id: str, family_member_ids: list[str]) -> Patient:
        """Link family members to a patient."""
        patient = await self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        patient.family_members = list(set(patient.family_members + family_member_ids))
        return await self.update_patient(patient)

