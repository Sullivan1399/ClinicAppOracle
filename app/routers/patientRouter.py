from fastapi import APIRouter, Depends, HTTPException
from app.utils.dependencies import get_db
from app.services.authService import get_current_user
from typing import List
from oracledb import AsyncConnection

from app.services.patientService import PatientService
from app.models.patient import PatientResponse, PatientCreate, PatientUpdate
from app.utils.dependencies import get_patient_service

router = APIRouter()

    
@router.get("/", response_model=List[PatientResponse])
async def read_patients(service: PatientService = Depends(get_patient_service)):
    return await service.get_all_patients()

@router.post("/", status_code=201)
async def create_patient(patient: PatientCreate, service: PatientService = Depends(get_patient_service)):
    await service.create_patient(patient)
    return {"message": "Patient created successfully"}

@router.put("/{pat_id}")
async def update_patient(pat_id: int, patient: PatientUpdate, service: PatientService = Depends(get_patient_service)):
    await service.update_patient(pat_id, patient)
    return {"message": "Patient updated successfully"}

@router.delete("/{pat_id}")
async def delete_patient(pat_id: int, service: PatientService = Depends(get_patient_service)):
    await service.delete_patient(pat_id)
    return {"message": "Patient deleted successfully"}

@router.get("/{patient_id}", response_model=PatientResponse) # Quan trọng: phải là @router.get
async def read_patient(
    patient_id: int, 
    service: PatientService = Depends(get_patient_service)
):
    patient = await service.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient