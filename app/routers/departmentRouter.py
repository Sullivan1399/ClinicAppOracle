from fastapi import APIRouter, Depends, HTTPException
from typing import List
from oracledb import AsyncConnection

from app.utils.dependencies import get_service
from app.services.departmentService import DepartmentService
from app.models.department import DepartmentResponse, DepartmentCreate, DepartmentUpdate

router = APIRouter()

@router.get("/", response_model=List[DepartmentResponse])
async def read_departments(service: DepartmentService = Depends(get_service)):
    return await service.get_all_departments()

@router.post("/", status_code=201)
async def create_department(department: DepartmentCreate, service: DepartmentService = Depends(get_service)):
    await service.create_department(department)
    return {"message": "Create Department successfully."}

@router.put("/{dept_id}")
async def update_department(dept_id: int, department: DepartmentUpdate, service: DepartmentService = Depends(get_service)):
    await service.update_department(dept_id, department)
    return {"message": "Update Department successfully."}

# @router.delete("/{dept_id}")
# async def delete_department(dept_id: int, service: DepartmentService = Depends(get_service)):
#     await service.delete_department(dept_id)
#     return {"message": "Delete Department successfully."}