from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional

# Import các dependency và model đã refactor ở bước trước
from app.utils.dependencies import get_visit_service, get_current_staff_details
from app.services.visitService import VisitService
from app.models.visit import VisitResponse, VisitCreate, VisitUpdate
from app.models.staff import StaffInfo

router = APIRouter()

# =================================================================
# 1. NHÓM API DÀNH CHO BÁC SĨ (DOCTOR)
# =================================================================

@router.get("/waiting", response_model=List[VisitResponse])
async def read_waiting_visits(
    service: VisitService = Depends(get_visit_service),
    current_staff: StaffInfo = Depends(get_current_staff_details)
):
    """
    Lấy danh sách chờ khám của Khoa mà bác sĩ đang thuộc về.
    Điều kiện: department_id trùng với bác sĩ VÀ staff_id IS NULL.
    """
    if current_staff.role != 'DOCTOR':
        raise HTTPException(status_code=403, detail="Chỉ bác sĩ mới được xem danh sách chờ khám.")
    
    if not current_staff.department_id:
        # Trường hợp bác sĩ chưa được gán vào khoa nào trong DB
        return [] 
        
    return await service.get_waiting_visits(current_staff.department_id)

@router.put("/{visit_id}/claim")
async def doctor_finish_exam(
    visit_id: int, 
    data: VisitUpdate,
    service: VisitService = Depends(get_visit_service),
    current_staff: StaffInfo = Depends(get_current_staff_details)
):
    """
    Bác sĩ nhận ca và lưu kết quả khám (Claim & Update).
    Hành động này sẽ gán staff_id = ID của bác sĩ đang thực hiện.
    """
    if current_staff.role != 'DOCTOR':
        raise HTTPException(status_code=403, detail="Chỉ bác sĩ mới được thực hiện khám bệnh.")

    # Gọi service để update (sẽ check staff_id is NULL trước khi update)
    await service.doctor_submit_exam(visit_id, current_staff.staff_id, data)
    
    return {"message": "Đã lưu kết quả khám và kết thúc phiên làm việc."}

# =================================================================
# 2. NHÓM API DÀNH CHO Y TÁ / TIẾP ĐÓN (NURSE)
# =================================================================

@router.post("/", status_code=201)
async def create_visit(
    data: VisitCreate, 
    service: VisitService = Depends(get_visit_service),
    current_staff: StaffInfo = Depends(get_current_staff_details)
):
    """
    Y tá tạo phiếu đăng ký khám.
    Lưu ý: Chỉ lưu patient_id, department_id, notes. Staff_id sẽ để NULL.
    """
    if current_staff.role not in ['NURSE', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Bác sĩ không được tạo phiếu tiếp đón.")
        
    await service.create_visit(data)
    return {"message": "Đăng ký khám thành công."}

# =================================================================
# 3. NHÓM API TRA CỨU CHUNG / QUẢN LÝ (COMMON / ADMIN)
# =================================================================
@router.get("/history", response_model=List[VisitResponse])
async def read_doctor_history(
    service: VisitService = Depends(get_visit_service),
    current_staff: StaffInfo = Depends(get_current_staff_details)
):
    """
    API riêng để bác sĩ xem lại danh sách bệnh nhân mình đã khám.
    Tự động lọc theo staff_id của người đang đăng nhập.
    """
    if current_staff.role != 'DOCTOR':
        raise HTTPException(status_code=403, detail="Chỉ bác sĩ mới có lịch sử khám bệnh.")
    return await service.get_visits(staff_id=current_staff.staff_id)

@router.get("/{visit_id}", response_model=VisitResponse)
async def read_visit_detail(
    visit_id: int, 
    service: VisitService = Depends(get_visit_service)
):
    return await service.get_visit_by_id(visit_id)

@router.get("/", response_model=List[VisitResponse])
async def read_visits(
    staff_id: Optional[int] = Query(None, description="Lọc theo Bác sĩ"),
    patient_id: Optional[int] = Query(None, description="Lọc theo Bệnh nhân"),
    service: VisitService = Depends(get_visit_service)
):
    """
    API dùng để xem lịch sử khám bệnh (cho cả Bác sĩ xem lại lịch sử BN hoặc Admin quản lý).
    """
    return await service.get_visits(staff_id, patient_id)


# Các API Update/Delete cơ bản (thường dành cho Admin sửa sai sót)
@router.put("/{visit_id}")
async def update_visit_admin(
    visit_id: int, 
    data: VisitUpdate, 
    service: VisitService = Depends(get_visit_service),
    current_staff: StaffInfo = Depends(get_current_staff_details)
):
    if current_staff.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Chỉ Admin mới được sửa thông tin gốc.")
    
    await service.update_visit(visit_id, data)
    return {"message": "Visit updated successfully"}

@router.delete("/{visit_id}")
async def delete_visit(
    visit_id: int, 
    service: VisitService = Depends(get_visit_service),
    current_staff: StaffInfo = Depends(get_current_staff_details)
):
    if current_staff.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Chỉ Admin mới được xóa lượt khám.")
        
    await service.delete_visit(visit_id)
    return {"message": "Visit deleted successfully"}
