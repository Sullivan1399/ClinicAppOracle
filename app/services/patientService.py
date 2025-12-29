from typing import List
from oracledb import AsyncConnection
from fastapi import HTTPException

from app.repository.patientRepo import PatientRepository
from app.models.patient import PatientResponse, PatientCreate, PatientUpdate

class PatientService:
    def __init__(self, db_conn: AsyncConnection):
        self.repo = PatientRepository(db_conn)

    async def get_all_patients(self) -> List[PatientResponse]:
        rows = await self.repo.get_all()
        # Row mapping: 0=id, 1=name, 2=dob, 3=gender, 4=phone, 5=address, 6=insurance
        return [
            PatientResponse(
                patient_id=row[0],
                full_name=row[1],
                dob=row[2].date() if row[2] else None, # Convert datetime to date nếu cần
                gender=row[3],
                phone=row[4],
                address=row[5],
                insurance_number=row[6]
            ) for row in rows
        ]

    async def create_patient(self, data: PatientCreate):
        return await self.repo.create(data)

    async def update_patient(self, pat_id: int, data: PatientUpdate):
        return await self.repo.update(pat_id, data)

    async def delete_patient(self, pat_id: int):
        try:
            return await self.repo.delete(pat_id)
        except Exception as e:
            # Bắt lỗi FK nếu bệnh nhân đã có lịch sử khám (VISIT)
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete patient. Patient has medical records (Visits)."
            )
    
    async def get_patient_by_id(self, pid: int) -> PatientResponse:
        row = await self.repo.get_by_id(pid)
        if not row: return None
        # Map row -> PatientResponse (tương tự get_all)
        return PatientResponse(
            patient_id=row[0], full_name=row[1], dob=row[2], 
            gender=row[3], phone=row[4], insurance_number=row[5], address=row[6]
        )