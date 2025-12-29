from fastapi import APIRouter, Depends
from app.utils.dependencies import get_db
from app.services.authService import get_current_user

router = APIRouter()

@router.get("/patients")
async def list_patients(db = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute("SELECT patient_id, full_name FROM hospital_admin.patient FETCH FIRST 20 ROWS ONLY")
        rows = await cur.fetchall()
        return [{"patient_id": r[0], "full_name": r[1]} for r in rows]