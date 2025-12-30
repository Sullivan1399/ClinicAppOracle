from typing import List
from app.repository.baseRepo import BaseRepo
from app.models.prescription import PrescriptionCreate

class PrescriptionRepository(BaseRepo):
    
    async def get_all_headers(self) -> List[tuple]:
        """Lấy danh sách đơn thuốc (chưa bao gồm chi tiết)"""
        # Thêm tiền tố hospital_admin.
        sql = """
            SELECT prescription_id, visit_id, staff_id, created_date, notes 
            FROM hospital_admin.PRESCRIPTION 
            ORDER BY created_date DESC
        """
        return await self.handle_execution(sql)

    async def get_details_by_prescription_id(self, pres_id: int) -> List[tuple]:
        """Lấy chi tiết thuốc, JOIN với MEDICINE để lấy tên thuốc"""
        # Thêm tiền tố hospital_admin.
        sql = """
            SELECT pd.detail_id, pd.medicine_id, m.medicine_name, pd.quantity, pd.dosage, m.price
            FROM hospital_admin.PRESCRIPTION_DETAIL pd
            JOIN hospital_admin.MEDICINE m ON pd.medicine_id = m.medicine_id
            WHERE pd.prescription_id = :pid
        """
        return await self.handle_execution(sql, {"pid": pres_id})

    async def create_aggregate(self, data: PrescriptionCreate) -> int:
        sql_head = """
            INSERT INTO hospital_admin.PRESCRIPTION (visit_id, staff_id, notes) 
            VALUES (:vid, :sid, :note) 
            RETURNING prescription_id INTO :out_id
        """
        try:
            async with self.conn.cursor() as cursor:
                out_id = cursor.var(int)
                # 1. Insert Header
                await cursor.execute(sql_head, {
                    "vid": data.visit_id, 
                    "sid": data.staff_id, 
                    "note": data.notes, 
                    "out_id": out_id
                })
                new_pres_id = out_id.getvalue()[0]

                # 2. Insert Details
                if data.details:
                    sql_detail = """
                        INSERT INTO hospital_admin.PRESCRIPTION_DETAIL 
                        (prescription_id, medicine_id, quantity, dosage) 
                        VALUES (:pid, :mid, :qty, :dos)
                    """
                    detail_data = [
                        {
                            "pid": new_pres_id, 
                            "mid": d.medicine_id, 
                            "qty": d.quantity, 
                            "dos": d.dosage
                        } for d in data.details
                    ]
                    await cursor.executemany(sql_detail, detail_data)
                
                await self.conn.commit()
                return new_pres_id
        except Exception as e:
            await self.conn.rollback()
            raise e

    async def delete_aggregate(self, pres_id: int) -> bool:
        """Xóa đơn thuốc (Xóa detail trước rồi xóa header)"""
        try:
            async with self.conn.cursor() as cursor:
                # 1. Xóa chi tiết (Do khóa ngoại) - Thêm tiền tố hospital_admin.
                await cursor.execute(
                    "DELETE FROM hospital_admin.PRESCRIPTION_DETAIL WHERE prescription_id = :id", 
                    {"id": pres_id}
                )
                
                # 2. Xóa header - Thêm tiền tố hospital_admin.
                await cursor.execute(
                    "DELETE FROM hospital_admin.PRESCRIPTION WHERE prescription_id = :id", 
                    {"id": pres_id}
                )
                
                await self.conn.commit()
                return True
        except Exception as e:
            await self.conn.rollback()
            raise e