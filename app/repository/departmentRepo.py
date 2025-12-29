from typing import List, Optional

from app.repository.baseRepo import BaseRepo
from app.models.department import DepartmentCreate, DepartmentUpdate

class DepartmentRepository(BaseRepo):
    async def get_all(self) -> List[tuple]:
        sql = "SELECT department_id, department_name FROM hospital_admin.department ORDER BY department_id"
        return await self.handle_execution(sql)

    async def get_by_id(self, dept_id: int) -> Optional[tuple]:
        sql = "SELECT department_id, department_name FROM hospital_admin.department WHERE department_id = :id"
        rows = await self.handle_execution(sql, {"id": dept_id})
        return rows[0] if rows else None

    async def create(self, department: DepartmentCreate) -> bool:
        # DEPARTMENT has id column auto increment
        sql = "INSERT INTO hospital_admin.department (department_name) VALUES (:name)"
        await self.handle_execution(sql, {"name": department.department_name}, commit=True)
        return True

    async def update(self, dept_id: int, department: DepartmentUpdate) -> bool:
        sql = "UPDATE hospital_admin.department SET department_name = :name WHERE department_id = :id"
        await self.handle_execution(sql, {"name": department.department_name, "id": dept_id}, commit=True)
        return True

    async def delete(self, dept_id: int) -> bool:
        sql = "DELETE FROM hospital_admin.department WHERE department_id = :id"
        await self.handle_execution(sql, {"id": dept_id}, commit=True)
        return True