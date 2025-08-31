from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import (
    TaskCreate, TaskResponse, TaskUpdate, TaskStatus,
    ServiceOffer, ProjectResponse, ProjectResponseCreate, ResponseStatus,
    ServiceCategory, ProfileUpdate, Notification
)
from app.tasks.service import (
    create_task, get_tasks, get_task, update_task, delete_task,
    create_service_offer, get_service_offer, update_service_offer,
    create_project_response, get_task_responses, update_response_status,
    get_notifications, mark_notification_read
)
from app.auth.service import users_db

router = APIRouter()

def get_current_user_phone(phone: str):
    if phone not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return phone

@router.post("/tasks", response_model=dict)
async def create_new_task(
    task_data: TaskCreate,
    phone: str = Depends(get_current_user_phone)
):
    try:
        result = create_task(task_data, phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks", response_model=List[TaskResponse])
async def get_all_tasks(
    category: ServiceCategory = None,
    status: TaskStatus = None,
    phone: str = Depends(get_current_user_phone)
):
    try:
        tasks = get_tasks(phone=phone, category=category, status=status)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/available", response_model=List[TaskResponse])
async def get_available_tasks(
    category: ServiceCategory = None,
    phone: str = Depends(get_current_user_phone)
):
    try:
        tasks = get_tasks(category=category, status=TaskStatus.OPEN)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: str,
    phone: str = Depends(get_current_user_phone)
):
    try:
        task = get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskResponse(**task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/tasks/{task_id}", response_model=dict)
async def update_task_by_id(
    task_id: str,
    task_data: TaskUpdate,
    phone: str = Depends(get_current_user_phone)
):
    try:
        result = update_task(task_id, task_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task_by_id(
    task_id: str,
    phone: str = Depends(get_current_user_phone)
):
    try:
        result = delete_task(task_id, phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/service-offer", response_model=dict)
async def create_or_update_service_offer(
    service_categories: List[ServiceCategory],
    description: str = None,
    hourly_rate: float = None,
    phone: str = Depends(get_current_user_phone)
):
    try:
        result = update_service_offer(phone, service_categories, description, hourly_rate)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/service-offer", response_model=ServiceOffer)
async def get_user_service_offer(
    phone: str = Depends(get_current_user_phone)
):
    try:
        offer = get_service_offer(phone)
        if not offer:
            raise HTTPException(status_code=404, detail="Service offer not found")
        return ServiceOffer(**offer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tasks/{task_id}/respond", response_model=dict)
async def respond_to_task(
    task_id: str,
    response_data: ProjectResponseCreate,
    phone: str = Depends(get_current_user_phone)
):
    try:
        result = create_project_response(task_id, phone, response_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{task_id}/responses", response_model=List[ProjectResponse])
async def get_task_responses_list(
    task_id: str,
    phone: str = Depends(get_current_user_phone)
):
    try:
        responses = get_task_responses(task_id)
        return responses
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/responses/{response_id}/status", response_model=dict)
async def update_response_status_endpoint(
    response_id: str,
    status: ResponseStatus,
    phone: str = Depends(get_current_user_phone)
):
    try:
        result = update_response_status(response_id, status, phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/notifications", response_model=List[Notification])
async def get_user_notifications(
    phone: str = Depends(get_current_user_phone)
):
    try:
        notifications = get_notifications(phone)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/notifications/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: str,
    phone: str = Depends(get_current_user_phone)
):
    try:
        result = mark_notification_read(notification_id, phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
