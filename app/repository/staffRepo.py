from typing import List, Optional
from app.repository.baseRepo import BaseRepo
from app.models.staff import StaffCreate, StaffUpdate

class StaffRepository(BaseRepo):
    async def get_all(self) -> List[tuple]:
        # JOIN để lấy tên khoa
        sql = """
            SELECT s.staff_id, s.full_name, s.username, s.role, s.phone, s.email, 
                   s.department_id, s.salary, d.department_name
            FROM hospital_admin.STAFF s
            LEFT JOIN hospital_admin.DEPARTMENT d ON s.department_id = d.department_id
            ORDER BY s.staff_id
        """
        return await self.handle_execution(sql)

    async def get_by_id(self, staff_id: int) -> Optional[tuple]:
        sql = """
            SELECT s.staff_id, s.full_name, s.username, s.role, s.phone, s.email, 
                   s.department_id, s.salary, d.department_name
            FROM hospital_admin.STAFF s
            LEFT JOIN hospital_admin.DEPARTMENT d ON s.department_id = d.department_id
            WHERE s.staff_id = :id
        """
        rows = await self.handle_execution(sql, {"id": staff_id})
        return rows[0] if rows else None

    async def get_by_username(self, username: str) -> Optional[tuple]:
        """Dùng để check duplicate username hoặc dùng cho login"""
        # Đã thêm hospital_admin. vào trước STAFF
        sql = "SELECT staff_id FROM hospital_admin.STAFF WHERE username = :u"
        rows = await self.handle_execution(sql, {"u": username})
        return rows[0] if rows else None

    async def create(self, data: StaffCreate, hashed_password: str) -> bool:
        sql = """
            INSERT INTO hospital_admin.STAFF (full_name, username, password_hash, role, phone, email, department_id, salary)
            VALUES (:name, :u_name, :pwd, :s_role, :phone, :email, :dept, :sal)
        """
        params = {
            "name": data.full_name,
            "u_name": data.username,        
            "pwd": hashed_password,         
            "s_role": data.role,            
            "phone": data.phone,
            "email": data.email,
            "dept": data.department_id,
            "sal": data.salary
        }
        await self.handle_execution(sql, params, commit=True)
        return True

    async def update(self, staff_id: int, data: StaffUpdate) -> bool:
        fields = []
        params = {"id": staff_id}

        if data.full_name is not None:
            fields.append("full_name = :name")
            params["name"] = data.full_name
            
        if data.role is not None:
            fields.append("role = :s_role")
            params["s_role"] = data.role
            
        if data.phone is not None:
            fields.append("phone = :phone")
            params["phone"] = data.phone
            
        if data.email is not None:
            fields.append("email = :email")
            params["email"] = data.email
            
        if data.department_id is not None:
            fields.append("department_id = :dept")
            params["dept"] = data.department_id
            
        if data.salary is not None:
            fields.append("salary = :sal")
            params["sal"] = data.salary

        if not fields:
            return False 

        # Đã đảm bảo có hospital_admin.
        sql = f"UPDATE hospital_admin.STAFF SET {', '.join(fields)} WHERE staff_id = :id"
        
        await self.handle_execution(sql, params, commit=True)
        return True

    async def delete(self, staff_id: int) -> bool:
        # Đã đảm bảo có hospital_admin.
        sql = "DELETE FROM hospital_admin.STAFF WHERE staff_id = :id"
        await self.handle_execution(sql, {"id": staff_id}, commit=True)
        return True
    
    async def get_identity_by_username(self, username: str) -> Optional[tuple]:
        """
        Hàm này chuyên dùng cho Auth/Dependency để lấy thông tin phân quyền
        """
        sql = """
            SELECT staff_id, role, department_id, full_name 
            FROM hospital_admin.STAFF 
            WHERE username = :u
        """
        rows = await self.handle_execution(sql, {"u": username})
        return rows[0] if rows else None