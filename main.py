from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.auth.api import router as auth_router
from app.tasks.api import router as tasks_router
from app.web.routes import router as web_router
from app.database import create_tables

app = FastAPI(title="ULE Platform API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    print("🗄️ Инициализация базы данных...")
    create_tables()
    print("✅ База данных готова!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://ylebb.ru", "https://ylebb.ru", "http://www.ylebb.ru", "https://www.ylebb.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks & Services"])
app.include_router(web_router, tags=["Web Interface"])

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "domain": "ylebb.ru"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    