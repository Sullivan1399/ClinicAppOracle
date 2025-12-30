import oracledb, jwt, datetime, asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.config.settings import settings
from app.models.auth import LoginRequest, TokenResponse
from app.services.authService import validate_db_credentials
from app.utils.helper import await_if_needed
from app.utils.security import encrypt_db_password

router = APIRouter()

# Use OAuth2PasswordRequestForm for form data
@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    dsn = f'{settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.SERVICE_NAME}'

    try:
        with oracledb.connect(user=username, password=password, dsn=dsn) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("SELECT role FROM hospital_admin.staff WHERE username = :u", [username])
                    row = cur.fetchone()
                    role = row[0] if row else ""
                except Exception:
                    raise HTTPException(status_code=401, detail="User cannot access staff data.")
                
        if not role:
            raise HTTPException(status_code=401, detail="Invalid username or password.")

    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"Login failed: {error.message}")
        raise HTTPException(status_code=401, detail="Invalid username or password (DB Connection failed).")

    # Encrypt the password to store in token
    encrypted_pass = encrypt_db_password(password)
    
    exp = datetime.datetime.now() + datetime.timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    
    payload = {
        "sub": username,
        "role": role,
        "db_pass": encrypted_pass,
    }
    
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