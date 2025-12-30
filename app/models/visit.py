from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VisitBase(BaseModel):
    patient_id: int
    department_id: int          # Y tá bắt buộc chọn khoa
    staff_id: Optional[int] = None # SỬA: Cho phép null (để trống khi mới tạo)
    notes: Optional[str] = None
    diagnosis: Optional[str] = None

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    diagnosis: Optional[str] = None
    notes: Optional[str] = None

class VisitResponse(VisitBase):
    visit_id: int
    visit_date: datetime
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    department_name: Optional[str] = None