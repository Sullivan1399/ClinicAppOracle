from typing import List, Optional
from app.repository.baseRepo import BaseRepo
from app.models.medicine import MedicineCreate, MedicineUpdate

class MedicineRepository(BaseRepo):
    async def get_all(self) -> List[tuple]:
        sql = "SELECT medicine_id, medicine_name, unit, price FROM MEDICINE ORDER BY medicine_name"
        return await self.handle_execution(sql)

    async def get_by_id(self, med_id: int) -> Optional[tuple]:
        sql = "SELECT medicine_id, medicine_name, unit, price FROM MEDICINE WHERE medicine_id = :id"
        rows = await self.handle_execution(sql, {"id": med_id})
        return rows[0] if rows else None

    async def create(self, data: MedicineCreate) -> bool:
        sql = "INSERT INTO MEDICINE (medicine_name, unit, price) VALUES (:name, :unit, :price)"
        params = {"name": data.medicine_name, "unit": data.unit, "price": data.price}
        await self.handle_execution(sql, params, commit=True)
        return True

    async def update(self, med_id: int, data: MedicineUpdate) -> bool:
        sql = "UPDATE MEDICINE SET medicine_name = :name, unit = :unit, price = :price WHERE medicine_id = :id"
        params = {"name": data.medicine_name, "unit": data.unit, "price": data.price, "id": med_id}
        await self.handle_execution(sql, params, commit=True)
        return True

    async def delete(self, med_id: int) -> bool:
        sql = "DELETE FROM MEDICINE WHERE medicine_id = :id"
        await self.handle_execution(sql, {"id": med_id}, commit=True)
        return True