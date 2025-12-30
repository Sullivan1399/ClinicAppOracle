from typing import List, Optional
from oracledb import AsyncConnection
from fastapi import HTTPException
from passlib.context import CryptContext # Cần cài passlib

from app.repository.staffRepo import StaffRepository
from app.models.staff import StaffResponse, StaffCreate, StaffUpdate, StaffInfo

# Cấu hình hash password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class StaffService:
    def __init__(self, db_conn: AsyncConnection):
        self.repo = StaffRepository(db_conn)

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    async def get_all_staff(self) -> List[StaffResponse]:
        rows = await self.repo.get_all()
        return [
            StaffResponse(
                staff_id=row[0], 
                full_name=row[1], 
                username=row[2], 
                role=row[3], 
                phone=row[4], 
                email=row[5],
                department_id=row[6],
                salary=row[7],
                department_name=row[8] # Field này nullable nếu staff chưa gán khoa
            ) for row in rows
        ]

    async def create_staff(self, data: StaffCreate):
        # 1. Check trùng username
        existing = await self.repo.get_by_username(data.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        # 2. Hash password
        hashed_pwd = self.get_password_hash(data.password)

        # 3. Create
        return await self.repo.create(data, hashed_pwd)

    async def update_staff(self, staff_id: int, data: StaffUpdate):
        # Có thể thêm check logic: Ví dụ không cho phép đổi username
        return await self.repo.update(staff_id, data)

    async def delete_staff(self, staff_id: int):
        try:
            return await self.repo.delete(staff_id)
        except Exception as e:
            # Bắt lỗi ràng buộc khóa ngoại (ví dụ Bác sĩ đã khám bệnh -> có record trong VISIT)
            raise HTTPException(status_code=400, detail="Cannot delete staff. This staff may have related records (Visits/Prescriptions).")
        
    async def get_staff_identity(self, username: str):
        """Lấy thông tin định danh nhân viên để phân quyền"""
        row = await self.repo.get_identity_by_username(username)
        if not row:
            return None
        
        # Trả về dict hoặc object tùy ý, ở đây trả về dict cho tiện
        return {
            "staff_id": row[0],
            "role": row[1],
            "department_id": row[2],
            "full_name": row[3]
        }
    async def get_staff_identity(self, username: str) -> Optional[StaffInfo]:
        """
        Lấy thông tin định danh nhân viên và map sang Pydantic Model
        """
        row = await self.repo.get_identity_by_username(username)
        if not row:
            return None
        
        # Row format từ Repo: (staff_id, role, department_id, full_name)
        return StaffInfo(
            staff_id=row[0],
            role=row[1],
            department_id=row[2],
            full_name=row[3]
        )