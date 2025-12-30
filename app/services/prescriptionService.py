from typing import List
from oracledb import AsyncConnection

from app.repository.prescriptionRepo import PrescriptionRepository
from app.models.prescription import PrescriptionResponse, PrescriptionCreate
from app.models.prescription_detail import PrescriptionDetailResponse

class PrescriptionService:
    def __init__(self, db_conn: AsyncConnection):
        self.repo = PrescriptionRepository(db_conn)

    async def get_all(self) -> List[PrescriptionResponse]:
        headers = await self.repo.get_all_headers()
        results = []
        for row in headers:
            pres_id = row[0]
            detail_rows = await self.repo.get_details_by_prescription_id(pres_id)
            
            # Map chi tiết từ tuple sang Pydantic model
            details_models = [
                PrescriptionDetailResponse(
                    detail_id=d[0], medicine_id=d[1], medicine_name=d[2], 
                    quantity=d[3], dosage=d[4], price_at_moment=d[5]
                ) for d in detail_rows
            ]
            
            results.append(PrescriptionResponse(
                prescription_id=pres_id, visit_id=row[1], staff_id=row[2], 
                created_date=row[3], notes=row[4], details=details_models
            ))
        return results

    async def create(self, data: PrescriptionCreate):
        new_id = await self.repo.create_aggregate(data)
        return {"prescription_id": new_id, "message": "Prescription created successfully"}

    async def delete(self, pres_id: int):
        await self.repo.delete_aggregate(pres_id)
        return {"message": "Prescription deleted"}