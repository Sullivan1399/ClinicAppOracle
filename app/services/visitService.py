from typing import List, Optional
from oracledb import AsyncConnection
from fastapi import HTTPException

from app.repository.visitRepo import VisitRepository
from app.models.visit import VisitResponse, VisitCreate, VisitUpdate

class VisitService:
    def __init__(self, db_conn: AsyncConnection):
        self.repo = VisitRepository(db_conn)

    async def get_visits(self, staff_id: Optional[int] = None, patient_id: Optional[int] = None) -> List[VisitResponse]:
        rows = await self.repo.get_all(staff_id, patient_id)
        
        # Mapping tuple từ DB sang Pydantic Model
        # Thứ tự trong SQL: 
        # 0:id, 1:pat_id, 2:stf_id, 3:dept_id, 4:date, 5:diag, 6:notes, 
        # 7:pat_name, 8:doc_name, 9:dept_name
        return [
            VisitResponse(
                visit_id=row[0],
                patient_id=row[1],
                staff_id=row[2],
                department_id=row[3],
                visit_date=row[4],
                diagnosis=row[5] if row[5] else None, # CLOB có thể trả về None hoặc LOB object
                notes=row[6] if row[6] else None,
                patient_name=row[7],
                doctor_name=row[8],
                department_name=row[9]
            ) for row in rows
        ]

    async def get_visit_by_id(self, visit_id: int) -> VisitResponse:
        row = await self.repo.get_by_id(visit_id)
        if not row:
            raise HTTPException(status_code=404, detail="Visit not found")
            
        return VisitResponse(
            visit_id=row[0],
            patient_id=row[1],
            staff_id=row[2],
            department_id=row[3],
            visit_date=row[4],
            diagnosis=str(row[5]) if row[5] else None, # Convert CLOB to str safe
            notes=str(row[6]) if row[6] else None,
            patient_name=row[7],
            doctor_name=row[8],
            department_name=row[9]
        )

    async def create_visit(self, data: VisitCreate):
        return await self.repo.create(data)

    async def update_visit(self, visit_id: int, data: VisitUpdate):
        return await self.repo.update(visit_id, data)

    async def delete_visit(self, visit_id: int):
        # Có thể thêm check logic: Nếu đã kê đơn thuốc (có record bên PRESCRIPTION) thì không cho xóa
        return await self.repo.delete(visit_id)
    async def get_waiting_visits(self, department_id: int) -> List[VisitResponse]:
        rows = await self.repo.get_waiting_by_department(department_id)
        # Map tuple to model (tương tự code cũ)
        return [
            VisitResponse(
                visit_id=row[0], patient_id=row[1], staff_id=0, # Staff ID 0 hoặc None
                department_id=row[3], visit_date=row[4],
                diagnosis=row[5], notes=row[6],
                patient_name=row[7], doctor_name=row[8], department_name=row[9]
            ) for row in rows
        ]

    async def doctor_submit_exam(self, visit_id: int, doctor_id: int, data: VisitUpdate):
        """Bác sĩ nộp kết quả khám"""
        success = await self.repo.claim_and_update(visit_id, doctor_id, data)
        if not success:
            raise HTTPException(status_code=400, detail="Không thể lưu: Ca khám này đã được bác sĩ khác xử lý hoặc không tồn tại.")
        return True