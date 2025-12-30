from typing import List, Optional
from app.repository.baseRepo import BaseRepo
from app.models.visit import VisitCreate, VisitUpdate

class VisitRepository(BaseRepo):
    async def get_waiting_by_department(self, department_id: int) -> List[tuple]:
        """
        Lấy danh sách chờ khám của một Khoa.
        Điều kiện: Cùng department_id VÀ staff_id IS NULL (chưa có bác sĩ nhận)
        """
        # Thêm tiền tố hospital_admin.
        sql = """
            SELECT v.visit_id, v.patient_id, v.staff_id, v.department_id, 
                   v.visit_date, 
                   TO_CHAR(v.diagnosis) as diagnosis, 
                   TO_CHAR(v.notes) as notes,
                   p.full_name AS patient_name,
                   'Chưa chỉ định' AS doctor_name,
                   d.department_name
            FROM hospital_admin.VISIT v
            JOIN hospital_admin.PATIENT p ON v.patient_id = p.patient_id
            LEFT JOIN hospital_admin.DEPARTMENT d ON v.department_id = d.department_id
            WHERE v.department_id = :did 
              AND v.staff_id IS NULL
            ORDER BY v.visit_date ASC
        """
        return await self.handle_execution(sql, {"did": department_id})

    async def create(self, data: VisitCreate) -> bool:
        """Y tá tạo: staff_id sẽ là NULL"""
        # Thêm tiền tố hospital_admin.
        sql = """
            INSERT INTO hospital_admin.VISIT (patient_id, department_id, notes, staff_id)
            VALUES (:pid, :did, :note, NULL) 
        """
        params = {
            "pid": data.patient_id,
            "did": data.department_id,
            "note": data.notes
        }
        await self.handle_execution(sql, params, commit=True)
        return True

    async def claim_and_update(self, visit_id: int, doctor_id: int, data: VisitUpdate) -> bool:
        # Thêm tiền tố hospital_admin.
        sql = """
            UPDATE hospital_admin.VISIT 
            SET staff_id = :sid, 
                diagnosis = :diag, 
                notes = :note,
                visit_date = SYSDATE 
            WHERE visit_id = :vid 
              AND staff_id IS NULL
        """
        params = {
            "sid": doctor_id,
            "diag": data.diagnosis,
            "note": data.notes,
            "vid": visit_id
        }
        
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(sql, params)
                row_count = cursor.rowcount
                await self.conn.commit()
                return row_count > 0
        except Exception as e:
            await self.conn.rollback()
            raise e
    
    async def get_all(self, staff_id: int = None, patient_id: int = None) -> List[tuple]:
        """
        Lấy danh sách Visit để tra cứu lịch sử.
        """
        # Thêm tiền tố hospital_admin.
        sql = """
            SELECT v.visit_id, v.patient_id, v.staff_id, v.department_id, 
                   v.visit_date, 
                   TO_CHAR(v.diagnosis) as diagnosis, 
                   TO_CHAR(v.notes) as notes,
                   p.full_name AS patient_name,
                   s.full_name AS doctor_name,
                   d.department_name
            FROM hospital_admin.VISIT v
            JOIN hospital_admin.PATIENT p ON v.patient_id = p.patient_id
            LEFT JOIN hospital_admin.STAFF s ON v.staff_id = s.staff_id 
            LEFT JOIN hospital_admin.DEPARTMENT d ON v.department_id = d.department_id
            WHERE 1=1
        """
        params = {}
        
        if staff_id:
            sql += " AND v.staff_id = :sid"
            params["sid"] = staff_id
        
        if patient_id:
            sql += " AND v.patient_id = :pid"
            params["pid"] = patient_id
            
        sql += " ORDER BY v.visit_date DESC"
        
        return await self.handle_execution(sql, params)
    
    async def get_by_id(self, visit_id: int) -> Optional[tuple]:
        """
        Lấy chi tiết lượt khám theo ID.
        """
        # Thêm tiền tố hospital_admin.
        sql = """
            SELECT v.visit_id, v.patient_id, v.staff_id, v.department_id, 
                   v.visit_date, 
                   TO_CHAR(v.diagnosis) as diagnosis, 
                   TO_CHAR(v.notes) as notes,
                   p.full_name, 
                   s.full_name, 
                   d.department_name
            FROM hospital_admin.VISIT v
            JOIN hospital_admin.PATIENT p ON v.patient_id = p.patient_id
            LEFT JOIN hospital_admin.STAFF s ON v.staff_id = s.staff_id
            LEFT JOIN hospital_admin.DEPARTMENT d ON v.department_id = d.department_id
            WHERE v.visit_id = :id
        """
        rows = await self.handle_execution(sql, {"id": visit_id})
        return rows[0] if rows else None
    
    async def delete(self, visit_id: int) -> bool:
        """
        Xóa lượt khám theo ID.
        """
        # Thêm tiền tố hospital_admin.
        sql = "DELETE FROM hospital_admin.VISIT WHERE visit_id = :id"
        
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(sql, {"id": visit_id})
                await self.conn.commit()
                return True
        except Exception as e:
            await self.conn.rollback()
            raise e