from typing import List
from app.repository.auditRepo import AuditRepository
from app.models.audit import AuditLogResponse, AuditJobStatus, AuditPolicyStatus

class AuditService:
    def __init__(self, conn):
        self.repo = AuditRepository(conn)

    async def get_logs(self, limit: int) -> List[AuditLogResponse]:
        rows = await self.repo.get_audit_logs(limit)
        
        results = []
        for row in rows:
            # row[4] là cột sql_text (CLOB)
            lob_object = row[4]
            sql_content = None

            if lob_object:
                # Kiểm tra nếu là đối tượng LOB thì phải await read()
                if hasattr(lob_object, "read"):
                    try:
                        sql_content = await lob_object.read()
                    except Exception:
                        sql_content = "[Lỗi đọc nội dung SQL]"
                else:
                    # Nếu Oracle trả về string thường (với câu lệnh ngắn)
                    sql_content = str(lob_object)

            results.append(
                AuditLogResponse(
                    event_timestamp=row[0],
                    db_username=row[1],
                    action_name=row[2],
                    object_name=row[3],
                    sql_text=sql_content
                )
            )
        return results

    # ... (Các hàm get_purge_job_status, get_policies giữ nguyên)
    async def get_purge_job_status(self) -> AuditJobStatus:
        row = await self.repo.get_job_status()
        if not row:
            return None
        return AuditJobStatus(
            job_name=row[0],
            state=row[1],
            last_start_date=row[2],
            next_run_date=row[3]
        )

    async def get_policies(self) -> List[AuditPolicyStatus]:
        rows = await self.repo.get_active_policies()
        return [
            AuditPolicyStatus(
                policy_name=row[0],
                enabled_option=row[1],
                success=row[2],
                failure=row[3]
            ) for row in rows
        ]