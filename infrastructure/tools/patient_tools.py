"""Patient-related LangChain tools."""

from datetime import date
from typing import Optional
from langchain_core.tools import tool
from dateutil import parser

from application.services.patient_service import PatientService


def create_patient_tool(patient_service: PatientService):
    """Create patient tool."""
    
    async def create_patient(
        full_name: str,
        phone: str,
        date_of_birth: str,
        insurance_name: Optional[str] = None,
        has_insurance: bool = True
    ) -> str:
        """
        Create a new patient record.
        
        Args:
            full_name: Patient's full name
            phone: Phone number
            date_of_birth: Date of birth in YYYY-MM-DD format
            insurance_name: Insurance provider name (optional)
            has_insurance: Whether patient has insurance (default: True)
        
        Returns:
            Patient ID if successful, error message otherwise
        """
        try:
            dob = parser.parse(date_of_birth).date()
            patient = await patient_service.create_patient(
                full_name=full_name,
                phone=phone,
                date_of_birth=dob,
                insurance_name=insurance_name,
                has_insurance=has_insurance
            )
            return f"Patient created successfully! Patient ID: {patient.id}"
        except Exception as e:
            return f"Error creating patient: {str(e)}"
    
    return tool(create_patient)


def get_patient_tool(patient_service: PatientService):
    """Get patient tool."""
    
    async def get_patient(patient_id: str) -> str:
        """
        Get patient information by ID.
        
        Args:
            patient_id: The patient's ID
        
        Returns:
            Patient information as JSON string
        """
        try:
            patient = await patient_service.get_patient_by_id(patient_id)
            if patient:
                import json
                return json.dumps({
                    "id": patient.id,
                    "full_name": patient.full_name,
                    "phone": patient.phone,
                    "date_of_birth": str(patient.date_of_birth),
                    "insurance_name": patient.insurance_name,
                    "has_insurance": patient.has_insurance
                }, indent=2)
            else:
                return f"Patient {patient_id} not found."
        except Exception as e:
            return f"Error getting patient: {str(e)}"
    
    return tool(get_patient)


def verify_patient_tool(patient_service: PatientService):
    """Verify patient tool."""
    
    async def verify_patient(phone: str) -> str:
        """
        Verify if a patient exists by phone number.
        
        Args:
            phone: Phone number to verify
        
        Returns:
            Patient ID if found, "not_found" otherwise
        """
        try:
            patient = await patient_service.get_patient_by_phone(phone)
            if patient:
                import json
                return json.dumps({
                    "found": True,
                    "patient_id": patient.id,
                    "full_name": patient.full_name
                }, indent=2)
            else:
                import json
                return json.dumps({"found": False}, indent=2)
        except Exception as e:
            return f"Error verifying patient: {str(e)}"
    
    return tool(verify_patient)

