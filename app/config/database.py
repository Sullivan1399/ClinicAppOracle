import oracledb
import asyncio
from fastapi import FastAPI

from app.config.settings import settings

async def init_db_pool(app: FastAPI):
    dsn = f'{settings.ORACLE_SERVICE_USERNAME}/{settings.ORACLE_SERVICE_PASSWORD}@{settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.SERVICE_NAME}'
    maybe_pool = oracledb.create_pool_async(
        dsn = dsn,
        pool_alias = settings.DB_POOL_ALIAS,
        min = settings.DB_POOL_MIN,
        max = settings.DB_POOL_MAX,
        increment = settings.DB_POOL_INCREMENT,
        homogeneous = settings.DB_POOL_HOMOGENEOUS
    )
    pool = maybe_pool
    if asyncio.iscoroutine(maybe_pool):
        pool = await maybe_pool

    app.state.db_pool = pool

async def close_db_pool(app:FastAPI):
    pool = getattr(app.state, "db_pool", None)
    if pool:
        maybe_close = pool.close()
        if asyncio.iscoroutine(maybe_close):
            await maybe_close
            
        app.state.db_pool = None
