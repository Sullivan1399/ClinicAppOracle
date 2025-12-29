from oracledb import AsyncConnection
from typing import List

from app.repository.departmentRepo import DepartmentRepository
from app.models.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse

class DepartmentService:
    def __init__(self, db_conn: AsyncConnection):
        self.repo = DepartmentRepository(db_conn)

    async def get_all_departments(self) -> List[DepartmentResponse]:
        rows = await self.repo.get_all()
        # Chuyển đổi list tuple [(1, 'Khoa Noi'), ...] sang list Pydantic Models
        return [DepartmentResponse(department_id=row[0], department_name=row[1]) for row in rows]

    async def create_department(self, data: DepartmentCreate):
        return await self.repo.create(data)

    async def update_department(self, dept_id: int, data: DepartmentUpdate):
        return await self.repo.update(dept_id, data)

    async def delete_department(self, dept_id: int):
        return await self.repo.delete(dept_id)