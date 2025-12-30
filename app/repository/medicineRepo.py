from typing import List, Optional
from app.repository.baseRepo import BaseRepo
from app.models.medicine import MedicineCreate, MedicineUpdate

class MedicineRepository(BaseRepo):
    async def get_all(self) -> List[tuple]:
        # Thêm tiền tố hospital_admin.
        sql = "SELECT medicine_id, medicine_name, unit, price FROM hospital_admin.MEDICINE ORDER BY medicine_name"
        return await self.handle_execution(sql)

    async def get_by_id(self, med_id: int) -> Optional[tuple]:
        sql = "SELECT medicine_id, medicine_name, unit, price FROM hospital_admin.MEDICINE WHERE medicine_id = :id"
        rows = await self.handle_execution(sql, {"id": med_id})
        return rows[0] if rows else None

    async def create(self, data: MedicineCreate) -> bool:
        sql = "INSERT INTO hospital_admin.MEDICINE (medicine_name, unit, price) VALUES (:name, :unit, :price)"
        params = {
            "name": data.medicine_name, 
            "unit": data.unit, 
            "price": data.price
        }
        await self.handle_execution(sql, params, commit=True)
        return True

    async def update(self, med_id: int, data: MedicineUpdate) -> bool:
        # Nâng cấp logic update động: Chỉ update những trường có gửi dữ liệu lên
        fields = []
        params = {"id": med_id}

        if data.medicine_name is not None:
            fields.append("medicine_name = :name")
            params["name"] = data.medicine_name
        
        if data.unit is not None:
            fields.append("unit = :unit")
            params["unit"] = data.unit
            
        if data.price is not None:
            fields.append("price = :price")
            params["price"] = data.price

        if not fields:
            return False

        # Đã thêm tiền tố hospital_admin.
        sql = f"UPDATE hospital_admin.MEDICINE SET {', '.join(fields)} WHERE medicine_id = :id"
        
        await self.handle_execution(sql, params, commit=True)
        return True

    async def delete(self, med_id: int) -> bool:
        sql = "DELETE FROM hospital_admin.MEDICINE WHERE medicine_id = :id"
        await self.handle_execution(sql, {"id": med_id}, commit=True)
        return True