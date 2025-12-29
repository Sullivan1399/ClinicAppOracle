from typing import List, Optional
from app.repository.baseRepo import BaseRepo
from app.models.staff import StaffCreate, StaffUpdate

class StaffRepository(BaseRepo):
    async def get_all(self) -> List[tuple]:
        # JOIN để lấy tên khoa
        sql = """
            SELECT s.staff_id, s.full_name, s.username, s.role, s.phone, s.email, 
                   s.department_id, s.salary, d.department_name
            FROM STAFF s
            LEFT JOIN DEPARTMENT d ON s.department_id = d.department_id
            ORDER BY s.staff_id
        """
        return await self.handle_execution(sql)

    async def get_by_id(self, staff_id: int) -> Optional[tuple]:
        sql = """
            SELECT s.staff_id, s.full_name, s.username, s.role, s.phone, s.email, 
                   s.department_id, s.salary, d.department_name
            FROM STAFF s
            LEFT JOIN DEPARTMENT d ON s.department_id = d.department_id
            WHERE s.staff_id = :id
        """
        rows = await self.handle_execution(sql, {"id": staff_id})
        return rows[0] if rows else None

    async def get_by_username(self, username: str) -> Optional[tuple]:
        """Dùng để check duplicate username hoặc dùng cho login"""
        sql = "SELECT staff_id FROM STAFF WHERE username = :u"
        rows = await self.handle_execution(sql, {"u": username})
        return rows[0] if rows else None

    async def create(self, data: StaffCreate, hashed_password: str) -> bool:
        # SỬA LẠI SQL: Đổi tên các bind variables tránh từ khóa (:user -> :u_name, :role -> :s_role)
        sql = """
            INSERT INTO STAFF (full_name, username, password_hash, role, phone, email, department_id, salary)
            VALUES (:name, :u_name, :pwd, :s_role, :phone, :email, :dept, :sal)
        """
        params = {
            "name": data.full_name,
            "u_name": data.username,        # Đã đổi key khớp với :u_name
            "pwd": hashed_password,         # Đã đổi key khớp với :pwd
            "s_role": data.role,            # Đã đổi key khớp với :s_role
            "phone": data.phone,
            "email": data.email,
            "dept": data.department_id,
            "sal": data.salary
        }
        await self.handle_execution(sql, params, commit=True)
        return True

    async def update(self, staff_id: int, data: StaffUpdate) -> bool:
        # Cũng cần sửa hàm update vì nó có dùng :role
        fields = []
        params = {"id": staff_id}

        if data.full_name is not None:
            fields.append("full_name = :name")
            params["name"] = data.full_name
            
        if data.role is not None:
            # SỬA: :role -> :s_role
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

        sql = f"UPDATE STAFF SET {', '.join(fields)} WHERE staff_id = :id"
        
        await self.handle_execution(sql, params, commit=True)
        return True

    async def delete(self, staff_id: int) -> bool:
        sql = "DELETE FROM STAFF WHERE staff_id = :id"
        await self.handle_execution(sql, {"id": staff_id}, commit=True)
        return True
    
    async def get_identity_by_username(self, username: str) -> Optional[tuple]:
        """
        Hàm này chuyên dùng cho Auth/Dependency để lấy thông tin phân quyền
        """
        sql = """
            SELECT staff_id, role, department_id, full_name 
            FROM STAFF 
            WHERE username = :u
        """
        rows = await self.handle_execution(sql, {"u": username})
        return rows[0] if rows else None