from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AuditLogResponse(BaseModel):
    event_timestamp: datetime
    db_username: str
    action_name: str
    object_name: str
    sql_text: Optional[str] = None

class AuditJobStatus(BaseModel):
    job_name: str
    state: str
    # SỬA: Đổi datetime thành str để khớp với TO_CHAR bên trên
    last_start_date: Optional[str] 
    next_run_date: Optional[str]

class AuditPolicyStatus(BaseModel):
    policy_name: str
    enabled_option: str
    success: str
    failure: str