from fastapi import APIRouter, Depends
from typing import List
from app.utils.dependencies import get_staff_service 
from app.services.staffService import StaffService
from app.models.staff import StaffResponse, StaffCreate, StaffUpdate

router = APIRouter()

@router.get("/", response_model=List[StaffResponse])
async def read_staffs(service: StaffService = Depends(get_staff_service)):
    return await service.get_all_staff()

@router.post("/", status_code=201)
async def create_staff(staff: StaffCreate, service: StaffService = Depends(get_staff_service)):
    await service.create_staff(staff)
    return {"message": "Staff created successfully"}

@router.put("/{staff_id}")
async def update_staff(staff_id: int, staff: StaffUpdate, service: StaffService = Depends(get_staff_service)):
    await service.update_staff(staff_id, staff)
    return {"message": "Staff updated successfully"}

@router.delete("/{staff_id}")
async def delete_staff(staff_id: int, service: StaffService = Depends(get_staff_service)):
    await service.delete_staff(staff_id)
    return {"message": "Staff deleted successfully"}