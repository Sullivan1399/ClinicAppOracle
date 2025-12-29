import oracledb, jwt, datetime, asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.config.settings import settings
from app.models.auth import LoginRequest, TokenResponse
from app.services.authService import validate_db_credentials
from app.utils.helper import await_if_needed

router = APIRouter()

# Use OAuth2PasswordRequestForm for form data
@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    valid = await validate_db_credentials(form_data.username, form_data.password)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid username or pasword.")
    
    # Get db_pool created at start_up
    try:
        pool = oracledb.get_pool(settings.DB_POOL_ALIAS)
    except Exception:
        pool = None

    if pool:
        try:
            maybe_cm = pool.acquire(user=form_data.username)
            cm = await await_if_needed(maybe_cm)
            async with cm as conn:
                try:
                    async with conn.cursor() as cur:
                        await cur.execute("SELECT role FROM hospital_admin.staff WHERE username = :u", [form_data.username])
                        row = await cur.fetchone()
                        role = row[0] if row else ""
                except Exception:
                    role = ""
        except Exception as e:
            print(str(e))
            role = ""
    else:
        role = ""

    if not role and form_data.username != settings.ORACLE_SERVICE_USERNAME.lower():
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    exp = datetime.datetime.now() + datetime.timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": form_data.username, "role": role, "exp": exp}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role
    }

# Use Pydantic model for request body
# @router.post("/login", response_model=TokenResponse)
# async def login(request: LoginRequest):
#     valid = await validate_db_credentials(request.username, request.password)
#     if not valid:
#         raise HTTPException(status_code=401, detail="Invalid username or pasword.")
    
#     # Get db_pool created at start_up
#     try:
#         pool = oracledb.get_pool(settings.DB_POOL_ALIAS)
#     except Exception:
#         pool = None

#     if pool:
#         try:
#             maybe_cm = pool.acquire(user=request.username)
#             cm = await await_if_needed(maybe_cm)
#             async with cm as conn:
#                 try:
#                     async with conn.cursor() as cur:
#                         await cur.execute("SELECT role FROM staff WHERE username = :u", [request.username])
#                         row = await cur.fetchone()
#                         role = row[0] if row else ""
#                 except Exception:
#                     role = ""
#         except Exception as e:
#             print(str(e))
#             role = ""
#     else:
#         role = ""

#     if not role and request.username != settings.ORACLE_SERVICE_USERNAME:
#         raise HTTPException(status_code=401, detail="Invalid username or password.")
    
#     exp = datetime.datetime.now() + datetime.timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
#     payload = {"sub": request.username, "role": role, "exp": exp}
#     token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return {
#         "access_token": token,
#         "token_type": "bearer",
#         "role": role
#     }