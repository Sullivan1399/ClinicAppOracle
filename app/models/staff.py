from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

# Các role hợp lệ theo DB Check Constraint
RoleType = Literal['DOCTOR', 'NURSE', 'ADMIN']

class StaffBase(BaseModel):
    full_name: str
    username: str
    role: RoleType
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    salary: Optional[float] = None

class StaffCreate(StaffBase):
    password: str = Field(..., description="Raw password for DB user creation")
    role: str = Field(..., pattern="^(DOCTOR|NURSE|ADMIN)$")

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[RoleType] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    salary: Optional[float] = None

class StaffResponse(StaffBase):
    staff_id: int
    department_name: Optional[str] = None

# === THÊM MỚI: Model dùng cho Auth/Dependency ===
class StaffInfo(BaseModel):
    staff_id: int
    role: RoleType
    department_id: Optional[int] = None # Admin có thể không thuộc khoa nào
    full_name: str