from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Import model detail vào để sử dụng như một list con
from app.models.prescription_detail import PrescriptionDetailCreate, PrescriptionDetailResponse

class PrescriptionBase(BaseModel):
    visit_id: int
    staff_id: int
    notes: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    # Một đơn thuốc khi tạo sẽ kèm theo danh sách chi tiết
    details: List[PrescriptionDetailCreate]

class PrescriptionUpdate(BaseModel):
    notes: Optional[str] = None

class PrescriptionResponse(PrescriptionBase):
    prescription_id: int
    created_date: datetime
    # Response trả về bao gồm danh sách chi tiết
    details: List[PrescriptionDetailResponse] = []