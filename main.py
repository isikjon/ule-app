from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.auth.api import router as auth_router
from app.tasks.api import router as tasks_router
from app.web.routes import router as web_router

app = FastAPI(title="Mobile App API", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks & Services"])
app.include_router(web_router, tags=["Web Interface"])

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 
