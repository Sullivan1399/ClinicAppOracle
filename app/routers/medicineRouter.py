from fastapi import APIRouter, Depends
from typing import List
from app.utils.dependencies import get_medicine_service
from app.services.medicineService import MedicineService
from app.models.medicine import MedicineResponse, MedicineCreate, MedicineUpdate

router = APIRouter()

@router.get("/", response_model=List[MedicineResponse])
async def read_medicines(service: MedicineService = Depends(get_medicine_service)):
    return await service.get_all()

@router.post("/", status_code=201)
async def create_medicine(data: MedicineCreate, service: MedicineService = Depends(get_medicine_service)):
    await service.create(data)
    return {"message": "Medicine created"}

@router.put("/{med_id}")
async def update_medicine(med_id: int, data: MedicineUpdate, service: MedicineService = Depends(get_medicine_service)):
    await service.update(med_id, data)
    return {"message": "Medicine updated"}

@router.delete("/{med_id}")
async def delete_medicine(med_id: int, service: MedicineService = Depends(get_medicine_service)):
    await service.delete(med_id)
    return {"message": "Medicine deleted"}