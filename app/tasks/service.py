import uuid
from typing import Dict, List, Optional
from datetime import datetime
from app.models import (
    TaskCreate, TaskResponse, TaskUpdate, TaskStatus,
    ServiceOffer, ProjectResponse, ProjectResponseCreate, ResponseStatus,
    ServiceCategory, Notification
)

tasks_db: Dict[str, dict] = {}
service_offers_db: Dict[str, dict] = {}
project_responses_db: Dict[str, dict] = {}
notifications_db: Dict[str, dict] = {}

def create_task(task_data: TaskCreate, customer_phone: str) -> dict:
    task_id = str(uuid.uuid4())
    
    task = {
        "id": task_id,
        "service_category": task_data.service_category,
        "description": task_data.description,
        "address": task_data.address,
        "date": task_data.date,
        "price": task_data.price,
        "photos": task_data.photos,
        "status": TaskStatus.OPEN,
        "customer_phone": customer_phone,
        "created_at": datetime.now(),
        "responses_count": 0
    }
    
    tasks_db[task_id] = task
    
    return {"success": True, "task_id": task_id, "message": "Task created successfully"}

def get_tasks(phone: str = None, category: ServiceCategory = None, status: TaskStatus = None) -> List[TaskResponse]:
    tasks = []
    
    for task in tasks_db.values():
        if phone and task["customer_phone"] != phone:
            continue
        if category and task["service_category"] != category:
            continue
        if status and task["status"] != status:
            continue
            
        tasks.append(TaskResponse(**task))
    
    return sorted(tasks, key=lambda x: x.created_at, reverse=True)

def get_task(task_id: str) -> Optional[dict]:
    return tasks_db.get(task_id)

def update_task(task_id: str, task_data: TaskUpdate) -> dict:
    if task_id not in tasks_db:
        raise ValueError("Task not found")
    
    task = tasks_db[task_id]
    update_data = task_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        task[key] = value
    
    return {"success": True, "message": "Task updated successfully"}

def delete_task(task_id: str, customer_phone: str) -> dict:
    if task_id not in tasks_db:
        raise ValueError("Task not found")
    
    task = tasks_db[task_id]
    if task["customer_phone"] != customer_phone:
        raise ValueError("Not authorized to delete this task")
    
    del tasks_db[task_id]
    
    return {"success": True, "message": "Task deleted successfully"}

def create_service_offer(phone: str, service_categories: List[ServiceCategory], description: str = None, hourly_rate: float = None) -> dict:
    offer_id = str(uuid.uuid4())
    
    offer = {
        "id": offer_id,
        "performer_phone": phone,
        "service_categories": service_categories,
        "description": description,
        "hourly_rate": hourly_rate,
        "created_at": datetime.now()
    }
    
    service_offers_db[offer_id] = offer
    
    return {"success": True, "offer_id": offer_id, "message": "Service offer created successfully"}

def get_service_offer(phone: str) -> Optional[dict]:
    for offer in service_offers_db.values():
        if offer["performer_phone"] == phone:
            return offer
    return None

def update_service_offer(phone: str, service_categories: List[ServiceCategory], description: str = None, hourly_rate: float = None) -> dict:
    offer = get_service_offer(phone)
    
    if not offer:
        return create_service_offer(phone, service_categories, description, hourly_rate)
    
    offer["service_categories"] = service_categories
    offer["description"] = description
    offer["hourly_rate"] = hourly_rate
    
    return {"success": True, "message": "Service offer updated successfully"}

def create_project_response(task_id: str, performer_phone: str, response_data: ProjectResponseCreate) -> dict:
    if task_id not in tasks_db:
        raise ValueError("Task not found")
    
    response_id = str(uuid.uuid4())
    
    response = {
        "id": response_id,
        "task_id": task_id,
        "performer_phone": performer_phone,
        "offer_price": response_data.offer_price,
        "message": response_data.message,
        "status": ResponseStatus.PENDING,
        "created_at": datetime.now()
    }
    
    project_responses_db[response_id] = response
    
    task = tasks_db[task_id]
    task["responses_count"] += 1
    
    create_notification(
        task["customer_phone"],
        "Новый отклик",
        f"Новый отклик по заказу \"{task['description'][:30]}...\"",
        "new_response"
    )
    
    return {"success": True, "response_id": response_id, "message": "Response submitted successfully"}

def get_task_responses(task_id: str) -> List[ProjectResponse]:
    responses = []
    
    for response in project_responses_db.values():
        if response["task_id"] == task_id:
            responses.append(ProjectResponse(**response))
    
    return sorted(responses, key=lambda x: x.created_at, reverse=True)

def update_response_status(response_id: str, status: ResponseStatus, customer_phone: str) -> dict:
    if response_id not in project_responses_db:
        raise ValueError("Response not found")
    
    response = project_responses_db[response_id]
    task = tasks_db.get(response["task_id"])
    
    if not task or task["customer_phone"] != customer_phone:
        raise ValueError("Not authorized to update this response")
    
    response["status"] = status
    
    if status == ResponseStatus.ACCEPTED:
        task["status"] = TaskStatus.IN_PROGRESS
        create_notification(
            response["performer_phone"],
            "Отклик принят",
            f"Ваш отклик по заказу \"{task['description'][:30]}...\" принят!",
            "response_accepted"
        )
    elif status == ResponseStatus.REJECTED:
        create_notification(
            response["performer_phone"],
            "Отклик отклонен",
            f"Ваш отклик по заказу \"{task['description'][:30]}...\" отклонен.",
            "response_rejected"
        )
    
    return {"success": True, "message": "Response status updated successfully"}

def create_notification(phone: str, title: str, message: str, notification_type: str) -> dict:
    notification_id = str(uuid.uuid4())
    
    notification = {
        "id": notification_id,
        "phone": phone,
        "title": title,
        "message": message,
        "type": notification_type,
        "created_at": datetime.now(),
        "read": False
    }
    
    notifications_db[notification_id] = notification
    
    return {"success": True, "notification_id": notification_id}

def get_notifications(phone: str) -> List[Notification]:
    notifications = []
    
    for notification in notifications_db.values():
        if notification["phone"] == phone:
            notifications.append(Notification(**notification))
    
    return sorted(notifications, key=lambda x: x.created_at, reverse=True)

def mark_notification_read(notification_id: str, phone: str) -> dict:
    if notification_id not in notifications_db:
        raise ValueError("Notification not found")
    
    notification = notifications_db[notification_id]
    if notification["phone"] != phone:
        raise ValueError("Not authorized to read this notification")
    
    notification["read"] = True
    
    return {"success": True, "message": "Notification marked as read"}
