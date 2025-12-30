from pydantic import BaseModel
from typing import Optional

class MedicineBase(BaseModel):
    medicine_name: str
    unit: Optional[str] = None
    price: Optional[float] = 0

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(MedicineBase):
    pass

class MedicineResponse(MedicineBase):
    medicine_id: int