from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/create-task", response_class=HTMLResponse)
async def create_task_page(request: Request):
    return templates.TemplateResponse("create_task.html", {"request": request})

@router.get("/my-skills", response_class=HTMLResponse)
async def my_skills_page(request: Request):
    return templates.TemplateResponse("my_skills.html", {"request": request})

@router.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request):
    return templates.TemplateResponse("notifications.html", {"request": request})

@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@router.get("/my-responses", response_class=HTMLResponse)
async def my_responses_page(request: Request):
    return templates.TemplateResponse("my_responses.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse)  
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/respond/{task_id}", response_class=HTMLResponse)
async def respond_page(request: Request, task_id: str):
    return templates.TemplateResponse("respond.html", {"request": request})

@router.get("/task/{task_id}", response_class=HTMLResponse)
async def task_page(request: Request, task_id: str):
    return templates.TemplateResponse("task.html", {"request": request})

@router.get("/my-projects", response_class=HTMLResponse)
async def my_projects_page(request: Request):
    return templates.TemplateResponse("my_projects.html", {"request": request})

@router.get("/performer-settings", response_class=HTMLResponse)
async def performer_settings_page(request: Request):
    return templates.TemplateResponse("performer_settings.html", {"request": request})

@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})
