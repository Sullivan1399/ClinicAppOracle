from pydantic import BaseModel
from typing import Optional

# Model dùng để nhận dữ liệu từ Client (khi tạo đơn thuốc)
class PrescriptionDetailCreate(BaseModel):
    medicine_id: int
    quantity: int
    dosage: Optional[str] = None

# Model dùng để trả về dữ liệu (kèm tên thuốc cho dễ đọc)
class PrescriptionDetailResponse(BaseModel):
    detail_id: int
    medicine_id: int
    medicine_name: str  # Field này sẽ được map từ JOIN query
    quantity: int
    dosage: Optional[str]
    price_at_moment: Optional[float] = None