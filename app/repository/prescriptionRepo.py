from typing import List
from app.repository.baseRepo import BaseRepo
from app.models.prescription import PrescriptionCreate

class PrescriptionRepository(BaseRepo):
    
    async def get_all_headers(self) -> List[tuple]:
        """Lấy danh sách đơn thuốc (chưa bao gồm chi tiết)"""
        sql = "SELECT prescription_id, visit_id, staff_id, created_date, notes FROM PRESCRIPTION ORDER BY created_date DESC"
        return await self.handle_execution(sql)

    async def get_details_by_prescription_id(self, pres_id: int) -> List[tuple]:
        """Lấy chi tiết thuốc, JOIN với MEDICINE để lấy tên thuốc"""
        sql = """
            SELECT pd.detail_id, pd.medicine_id, m.medicine_name, pd.quantity, pd.dosage, m.price
            FROM PRESCRIPTION_DETAIL pd
            JOIN MEDICINE m ON pd.medicine_id = m.medicine_id
            WHERE pd.prescription_id = :pid
        """
        return await self.handle_execution(sql, {"pid": pres_id})

    async def create_aggregate(self, data: PrescriptionCreate) -> int:
        """Transaction: Tạo Header -> Lấy ID -> Tạo Details -> Commit"""
        sql_head = "INSERT INTO PRESCRIPTION (visit_id, staff_id, notes) VALUES (:vid, :sid, :note) RETURNING prescription_id INTO :out_id"
        
        cursor = self.db.cursor()
        out_id = cursor.var(int)
        
        try:
            # 1. Insert Header
            await cursor.execute(sql_head, {"vid": data.visit_id, "sid": data.staff_id, "note": data.notes, "out_id": out_id})
            new_pres_id = out_id.getvalue()[0]

            # 2. Insert Details (Batch)
            if data.details:
                sql_detail = "INSERT INTO PRESCRIPTION_DETAIL (prescription_id, medicine_id, quantity, dosage) VALUES (:pid, :mid, :qty, :dos)"
                detail_data = [{"pid": new_pres_id, "mid": d.medicine_id, "qty": d.quantity, "dos": d.dosage} for d in data.details]
                await cursor.executemany(sql_detail, detail_data)
            
            await self.db.commit()
            return new_pres_id
        except Exception as e:
            await self.db.rollback()
            raise e
        finally:
            await cursor.close()

    async def delete_aggregate(self, pres_id: int) -> bool:
        cursor = self.db.cursor()
        try:
            await cursor.execute("DELETE FROM PRESCRIPTION_DETAIL WHERE prescription_id = :id", {"id": pres_id})
            await cursor.execute("DELETE FROM PRESCRIPTION WHERE prescription_id = :id", {"id": pres_id})
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise e
        finally:
            await cursor.close()