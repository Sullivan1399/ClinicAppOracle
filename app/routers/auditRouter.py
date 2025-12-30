from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.auditService import AuditService
from app.services.authService import get_current_user
from app.repository.staffRepo import StaffRepository
from app.utils.dependencies import get_audit_service, get_db # <--- Import get_db

router = APIRouter()

# --- SỬA LẠI DEPENDENCY NÀY ---
async def check_audit_permission(
    username: str = Depends(get_current_user),
    conn = Depends(get_db) # <--- Inject Connection vào đây
):
    """
    Sử dụng kết nối của chính user đang đăng nhập (admin01) để kiểm tra quyền.
    """
    try:
        # Truyền conn vào StaffRepository để không phải tạo kết nối mới
        repo = StaffRepository(conn) 
        
        user_info = await repo.get_identity_by_username(username)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Không tìm thấy thông tin nhân viên")
        
        role = user_info[1] 
        if role != 'ADMIN' and username != 'audit_mgr':
            raise HTTPException(status_code=403, detail="Bạn không có quyền xem Nhật ký hệ thống")
        
        return username
    except Exception as e:
        # Log lỗi để dễ debug nếu có vấn đề khác
        print(f"Error checking permission: {e}")
        raise e

# --- CÁC API ENDPOINT ---
# (Code dưới đây giữ nguyên, chỉ đảm bảo AuditService đã được update ở Bước 1)

@router.get("/logs")
async def view_audit_logs(
    limit: int = Query(10), 
    user: str = Depends(check_audit_permission),
    service: AuditService = Depends(get_audit_service)
):
    return await service.get_logs(limit)

@router.get("/job-status")
async def check_purge_job(
    user: str = Depends(check_audit_permission),
    service: AuditService = Depends(get_audit_service)
):
    status = await service.get_purge_job_status()
    if not status:
        raise HTTPException(status_code=404, detail="Job dọn dẹp chưa được tạo")
    return status

@router.get("/policies")
async def check_active_policies(
    user: str = Depends(check_audit_permission),
    service: AuditService = Depends(get_audit_service)
):
    return await service.get_policies()