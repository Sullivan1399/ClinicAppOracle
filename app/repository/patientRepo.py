from typing import List, Optional
from app.repository.baseRepo import BaseRepo
from app.models.patient import PatientCreate, PatientUpdate

class PatientRepository(BaseRepo):
    async def get_all(self) -> List[tuple]:
        sql = """
            SELECT patient_id, full_name, dob, gender, phone, address, insurance_number
            FROM PATIENT
            ORDER BY patient_id DESC
        """
        return await self.handle_execution(sql)

    async def get_by_id(self, pat_id: int) -> Optional[tuple]:
        sql = """
            SELECT patient_id, full_name, dob, gender, phone, address, insurance_number
            FROM PATIENT
            WHERE patient_id = :id
        """
        rows = await self.handle_execution(sql, {"id": pat_id})
        return rows[0] if rows else None

    async def create(self, data: PatientCreate) -> bool:
        # Lưu ý: Đặt tên biến bind an toàn tránh từ khóa Oracle (p_*)
        sql = """
            INSERT INTO PATIENT (full_name, dob, gender, phone, address, insurance_number)
            VALUES (:p_name, :p_dob, :p_gender, :p_phone, :p_addr, :p_ins)
        """
        params = {
            "p_name": data.full_name,
            "p_dob": data.dob,
            "p_gender": data.gender,
            "p_phone": data.phone,
            "p_addr": data.address,
            "p_ins": data.insurance_number
        }
        await self.handle_execution(sql, params, commit=True)
        return True

    async def update(self, pat_id: int, data: PatientUpdate) -> bool:
        # Xây dựng câu query động
        fields = []
        params = {"id": pat_id}

        if data.full_name is not None:
            fields.append("full_name = :p_name")
            params["p_name"] = data.full_name
        
        if data.dob is not None:
            fields.append("dob = :p_dob")
            params["p_dob"] = data.dob
            
        if data.gender is not None:
            fields.append("gender = :p_gender")
            params["p_gender"] = data.gender
            
        if data.phone is not None:
            fields.append("phone = :p_phone")
            params["p_phone"] = data.phone
            
        if data.address is not None:
            fields.append("address = :p_addr")
            params["p_addr"] = data.address
            
        if data.insurance_number is not None:
            fields.append("insurance_number = :p_ins")
            params["p_ins"] = data.insurance_number

        if not fields:
            return False # Không có gì để update

        sql = f"UPDATE PATIENT SET {', '.join(fields)} WHERE patient_id = :id"
        
        await self.handle_execution(sql, params, commit=True)
        return True

    async def delete(self, pat_id: int) -> bool:
        sql = "DELETE FROM PATIENT WHERE patient_id = :id"
        await self.handle_execution(sql, {"id": pat_id}, commit=True)
        return True
    
    async def get_by_id(self, pid: int):
        sql = "SELECT * FROM PATIENT WHERE patient_id = :id"
        rows = await self.handle_execution(sql, {"id": pid})
        return rows[0] if rows else None