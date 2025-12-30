from typing import List, Optional
from app.repository.baseRepo import BaseRepo

class AuditRepository(BaseRepo):
    
    async def get_audit_logs(self, limit: int = 100) -> List[tuple]:
        """
        Lấy nhật ký giám sát, sửa tên cột POLICY_NAME thành UNIFIED_AUDIT_POLICIES
        """
        sql = """
            SELECT event_timestamp, 
                   dbusername, 
                   action_name, 
                   object_name, 
                   sql_text
            FROM AUDSYS.UNIFIED_AUDIT_TRAIL
            WHERE (
                object_name IN ('PATIENT', 'STAFF', 'MEDICINE', 'PRESCRIPTION_DETAIL')
                -- SỬA: Dùng UNIFIED_AUDIT_POLICIES thay cho POLICY_NAME
                OR UNIFIED_AUDIT_POLICIES LIKE '%FGA_HIGH_QTY_ALERT%'
            )
            AND dbusername != 'SYS'
            AND NOT (
                object_name = 'STAFF' 
                AND action_name = 'SELECT' 
                AND (
                    LOWER(sql_text) LIKE '%upper(username)%' OR 
                    LOWER(sql_text) LIKE '%upper(trim(username))%' OR
                    LOWER(sql_text) LIKE '%select role from hospital_admin.staff%' OR
                    LOWER(sql_text) LIKE '%select department_id from hospital_admin.staff%' OR
                    LOWER(sql_text) LIKE '%select staff_id, role, department_id, full_name%'
                )
            )
            ORDER BY event_timestamp DESC
            FETCH FIRST :limit_rows ROWS ONLY
        """
        return await self.handle_execution(sql, {"limit_rows": limit})

    async def get_job_status(self) -> Optional[tuple]:
        """Kiểm tra trạng thái Job dọn dẹp logs (Sửa lỗi DPY-3022)"""
        sql = """
            SELECT job_name, 
                   state, 
                   TO_CHAR(last_start_date, 'YYYY-MM-DD HH24:MI:SS') as last_start_date, 
                   TO_CHAR(next_run_date, 'YYYY-MM-DD HH24:MI:SS') as next_run_date
            FROM DBA_SCHEDULER_JOBS
            WHERE job_name = 'JOB_PURGE_AUDIT_LOGS'
        """
        rows = await self.handle_execution(sql)
        return rows[0] if rows else None

    async def get_active_policies(self) -> List[tuple]:
        """Xem các policy đang bật, thêm try-except để tránh lỗi Forbidden"""
        try:
            sql_unified = """
                SELECT policy_name, enabled_option, success, failure
                FROM AUDIT_UNIFIED_ENABLED_POLICIES
                WHERE policy_name IN (
                    'AUDIT_PATIENT_INTEGRITY', 
                    'AUDIT_STAFF_PRIVACY', 
                    'AUDIT_MEDICINE_PRICE',
                    'AUDIT_MEDICINE_DELETE_LOG'
                )
            """
            
            sql_fga = """
                SELECT policy_name, 'BY USER' as enabled_option, 'YES' as success, 'YES' as failure
                FROM DBA_AUDIT_POLICIES
                WHERE object_name = 'PRESCRIPTION_DETAIL' 
                  AND policy_name = 'FGA_HIGH_QTY_ALERT'
            """
            
            unified_rows = await self.handle_execution(sql_unified)
            fga_rows = await self.handle_execution(sql_fga)
            
            return unified_rows + fga_rows
        except Exception as e:
            print(f"Lỗi quyền truy cập Policy: {e}")
            # Trả về danh sách trống hoặc dữ liệu mẫu nếu thiếu quyền SELECT DICTIONARY
            return []