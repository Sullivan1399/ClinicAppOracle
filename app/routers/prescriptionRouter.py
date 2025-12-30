from fastapi import APIRouter, Depends
from typing import List
from app.utils.dependencies import get_prescription_service
from app.services.prescriptionService import PrescriptionService
from app.models.prescription import PrescriptionResponse, PrescriptionCreate
from app.utils.dependencies import get_prescription_service, get_current_staff_details
from app.models.staff import StaffInfo
router = APIRouter()

@router.get("/", response_model=List[PrescriptionResponse])
async def read_prescriptions(service: PrescriptionService = Depends(get_prescription_service)):
    return await service.get_all()

@router.post("/", status_code=201)
async def create_prescription(
    data: PrescriptionCreate, 
    service: PrescriptionService = Depends(get_prescription_service),
    current_staff: StaffInfo = Depends(get_current_staff_details) # Sử dụng hàm có sẵn
):
    # Gán staff_id lấy từ kết quả của hàm get_current_staff_details
    data.staff_id = current_staff.staff_id 
    return await service.create(data)

@router.delete("/{pres_id}")
async def delete_prescription(pres_id: int, service: PrescriptionService = Depends(get_prescription_service)):
    return await service.delete(pres_id)