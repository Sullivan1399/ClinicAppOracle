import oracledb
import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import AsyncGenerator

from app.config.settings import settings
from app.utils.helper import await_if_needed
from app.utils.security import decrypt_db_password
from app.services.authService import get_current_user
from app.services.departmentService import DepartmentService
from app.services.staffService import StaffService
from app.services.patientService import PatientService
from app.services.medicineService import MedicineService
from app.services.prescriptionService import PrescriptionService
from app.services.visitService import VisitService
from app.models.staff import StaffInfo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dependency to get DB credentials include current user and password from token
async def get_db_credentials(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        encrypted_pass = payload.get("db_pass")
        
        if not username or not encrypted_pass:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        password = decrypt_db_password(encrypted_pass)
        return username, password
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    
# Dependency: Open a new Standalone DB connection per request
async def get_db(creds: tuple = Depends(get_db_credentials)) -> AsyncGenerator:
    username, password = creds
    dsn = f'{settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.SERVICE_NAME}'
    
    print(f"DEBUG >> Opening Standalone Connection for: {username}")
    
    try:
        # Tạo kết nối Async mới
        conn = await oracledb.connect_async(user=username, password=password, dsn=dsn)
        
        try:
            yield conn
        finally:
            await conn.close()
            print(f"DEBUG >> Closed Connection for: {username}")
            
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=400, detail=f"DB Connection Error: {error.message}")

# Dependency to init Service with DB connection
def get_service(conn = Depends(get_db)) -> DepartmentService:
    return DepartmentService(conn)

def get_staff_service(conn = Depends(get_db)) -> StaffService:
    return StaffService(conn)

def get_patient_service(conn = Depends(get_db)) -> PatientService:
    return PatientService(conn)

def get_medicine_service(conn = Depends(get_db)) -> MedicineService:
    return MedicineService(conn)

def get_prescription_service(conn = Depends(get_db)) -> PrescriptionService:
    return PrescriptionService(conn)

def get_visit_service(conn = Depends(get_db)) -> VisitService:
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