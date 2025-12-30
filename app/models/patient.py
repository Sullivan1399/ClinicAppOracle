from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class PatientBase(BaseModel):
    full_name: str
    dob: Optional[date] = None
    gender: Optional[Literal['M', 'F']] = None # Chỉ chấp nhận M hoặc F
    phone: Optional[str] = None
    address: Optional[str] = None
    insurance_number: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    # Cho phép update từng phần
    full_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Literal['M', 'F']] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    insurance_number: Optional[str] = None

class PatientResponse(PatientBase):
    patient_id: int