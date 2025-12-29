from fastapi import APIRouter, Depends
from typing import List
from app.utils.dependencies import get_prescription_service
from app.services.prescriptionService import PrescriptionService
from app.models.prescription import PrescriptionResponse, PrescriptionCreate

router = APIRouter()

@router.get("/", response_model=List[PrescriptionResponse])
async def read_prescriptions(service: PrescriptionService = Depends(get_prescription_service)):
    return await service.get_all()

@router.post("/", status_code=201)
async def create_prescription(data: PrescriptionCreate, service: PrescriptionService = Depends(get_prescription_service)):
    return await service.create(data)

@router.delete("/{pres_id}")
async def delete_prescription(pres_id: int, service: PrescriptionService = Depends(get_prescription_service)):
    return await service.delete(pres_id)