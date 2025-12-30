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
        sql = "SELECT staff_id FROM hospital_admin.STAFF WHERE username = :u"
        rows = await self.handle_execution(sql, {"u": username})
        return rows[0] if rows else None

    async def create_full_staff(self, data: StaffCreate, hashed_password: str) -> bool:
        # Gọi Stored Procedure để tạo Staff + DB User + Gán quyền + OLS Label
        sql = """
            BEGIN
                hospital_admin.create_hospital_staff_user(
                    p_full_name   => :full_name,
                    p_username    => :username,
                    p_password    => :raw_password,
                    p_role        => :role,
                    p_phone       => :phone,
                    p_email       => :email,
                    p_dept_id     => :dept_id,
                    p_salary      => :salary,
                    p_hashed_pass => :hashed_pass
                );
            END;
        """
        params = {
            "full_name": data.full_name,
            "username": data.username,
            "raw_password": data.password, # Mật khẩu thô để tạo user Oracle
            "role": data.role,
            "phone": data.phone,
            "email": data.email,
            "dept_id": data.department_id,
            "salary": data.salary,
            "hashed_pass": hashed_password # Mật khẩu băm để lưu vào bảng STAFF
        }

        try:
            await self.handle_execution(sql, params, commit=True)
            return True
        except Exception as e:
            print(f"Error creating staff user: {e}")
            raise e
        
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