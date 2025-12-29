import oracledb
import asyncio
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.config.settings import settings
from app.models.auth import TokenResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Validate user credentials by attempting a direct ephemeral connection as the session user
async def validate_db_credentials(username: str, password: str) -> bool:
    dsn = f'{username}/{password}@{settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.SERVICE_NAME}'
    try:
        maybe_conn = oracledb.connect_async(dsn=dsn)
        conn = maybe_conn
        if asyncio.iscoroutine(maybe_conn):
            conn = await maybe_conn
        async with conn:
            pass
        return True
    except oracledb.DatabaseError:
        return False
    
def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")