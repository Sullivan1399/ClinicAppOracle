from typing import List
from oracledb import AsyncConnection
from fastapi import HTTPException

from app.repository.medicineRepo import MedicineRepository
from app.models.medicine import MedicineResponse, MedicineCreate, MedicineUpdate

class MedicineService:
    def __init__(self, db_conn: AsyncConnection):
        self.repo = MedicineRepository(db_conn)

    async def get_all(self) -> List[MedicineResponse]:
        rows = await self.repo.get_all()
        return [MedicineResponse(medicine_id=row[0], medicine_name=row[1], unit=row[2], price=row[3]) for row in rows]

    async def create(self, data: MedicineCreate):
        return await self.repo.create(data)

    async def update(self, med_id: int, data: MedicineUpdate):
        return await self.repo.update(med_id, data)

    async def delete(self, med_id: int):
        # Có thể thêm logic check xem thuốc có đang trong đơn thuốc nào không trước khi xóa
        return await self.repo.delete(med_id)