from fastapi import Request, HTTPException, status, Depends
from typing import AsyncGenerator
from oracledb import AsyncConnection

from app.utils.helper import await_if_needed
from app.services.authService import get_current_user
from app.services.departmentService import DepartmentService

# Dependency: Acquire connection from global pool AS PROXY
async def get_db(request: Request, current_user: str = Depends(get_current_user)) -> AsyncGenerator:
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise HTTPException(status_code=500, detail="DB pool has not been initialized.")
    
    try:
        if current_user:
            maybe_cm = pool.acquire(user=current_user)
        else:
            maybe_cm = pool.acquire()
        cm = await await_if_needed(maybe_cm)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"DB acquire failed: {e}")

    try:
        # Use async with to ensure the connection remains open for the handler code
        async with cm as conn:
            yield conn
    finally:
        pass

# Dependency to init Service with DB connection
def get_service(conn: AsyncConnection = Depends(get_db)) -> DepartmentService:
    return DepartmentService(conn)
    