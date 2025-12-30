from fastapi import Request, HTTPException, status, Depends
from typing import AsyncGenerator
from oracledb import AsyncConnection

from app.utils.helper import await_if_needed
from app.services.authService import get_current_user
from app.services.departmentService import DepartmentService
from app.services.staffService import StaffService
from app.services.patientService import PatientService
from app.services.medicineService import MedicineService
from app.services.prescriptionService import PrescriptionService
from app.services.visitService import VisitService

from app.models.staff import StaffInfo
# Dependency: Acquire connection from global pool AS PROXY
async def get_db(request: Request, current_user: str = Depends(get_current_user)) -> AsyncGenerator:
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise HTTPException(status_code=500, detail="DB pool has not been initialized.")
    
    try:
        if current_user:
            maybe_cm = pool.acquire(user=current_user)
        else:
            maybe_cm = pool.acquire()
        cm = await await_if_needed(maybe_cm)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"DB acquire failed: {e}")

    try:
        # Use async with to ensure the connection remains open for the handler code
        async with cm as conn:
            yield conn
    finally:
        pass

# Dependency to init Service with DB connection
def get_service(conn: AsyncConnection = Depends(get_db)) -> DepartmentService:
    return DepartmentService(conn)

def get_staff_service(conn: AsyncConnection = Depends(get_db)) -> StaffService:
    return StaffService(conn)

def get_patient_service(conn: AsyncConnection = Depends(get_db)) -> PatientService:
    return PatientService(conn)

def get_medicine_service(conn: AsyncConnection = Depends(get_db)) -> MedicineService:
    return MedicineService(conn)

def get_prescription_service(conn: AsyncConnection = Depends(get_db)) -> PrescriptionService:
    return PrescriptionService(conn)

def get_visit_service(conn: AsyncConnection = Depends(get_db)) -> VisitService:
    return VisitService(conn)

async def get_current_staff_details(
    username: str = Depends(get_current_user),
    staff_service: StaffService = Depends(get_staff_service)
) -> StaffInfo:
    """
    Dependency này trả về model StaffInfo lấy từ Service
    """
    staff_info = await staff_service.get_staff_identity(username)
    
    if not staff_info:
        raise HTTPException(status_code=401, detail="User profile not found or inactive.")
    
    return staff_info