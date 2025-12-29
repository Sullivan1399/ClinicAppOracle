import uvicorn
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.config.database import init_db_pool, close_db_pool
from app.routers import authRouter, patientRouter, departmentRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool(app)
    print("Application startup complete. Ready to serve requests.")

    yield

    await close_db_pool(app)
    print("Shutting down application...")
    

app = FastAPI(
    title="Clinic Management Application",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")

app.include_router(authRouter.router, prefix="/auth", tags=["Auth"])
app.include_router(patientRouter.router, prefix="/patient", tags=["Patient"])
app.include_router(departmentRouter.router, prefix="/department", tags=["Department"])

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    index_path = "./frontend/pages/login.html"
    if not os.path.exists(index_path):
        return HTMLResponse(content="<h1>Login file not found</h1>", status_code=404)
    with open(index_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True, workers=1)