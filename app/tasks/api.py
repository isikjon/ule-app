from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List
from app.database import get_db
from app.auth.service import get_user_by_phone, get_current_user_from_token
from app.models import (
    TaskCreate, TaskResponse, TaskUpdate, TaskStatus,
    ServiceOffer, ServiceOfferCreate, ProjectResponse, ProjectResponseCreate, ResponseStatus,
    ServiceCategory, ProfileUpdate, Notification
)
from app.tasks.service import (
    create_task, get_tasks, get_task, update_task, delete_task,
    create_service_offer, get_service_offer, update_service_offer,
    create_project_response, get_task_responses, update_response_status,
    get_notifications, mark_notification_read
)

router = APIRouter()

# Удалили неиспользуемую функцию get_current_user_id

@router.post("/tasks", response_model=dict)
async def create_new_task(
    task_data: TaskCreate,
    authorization: str = Header(None)
):
    try:
        print(f"POST /tasks - Received task_data: {task_data}")
        print(f"POST /tasks - Authorization header: {authorization}")
        
        if not authorization:
            print("POST /tasks - No authorization header")
            raise HTTPException(status_code=401, detail="No authorization header")
        
        if not authorization.startswith("Bearer "):
            print("POST /tasks - Invalid authorization format")
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization.replace("Bearer ", "")
        print(f"POST /tasks - Extracted token: {token[:20]}...")
        
        user = get_current_user_from_token(token)
        if not user:
            print("POST /tasks - Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"POST /tasks - User found: {user}")
        user_id = user['id']
        
        result = create_task(task_data, user_id)
        print(f"POST /tasks - Task created: {result}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_new_task: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/tasks", response_model=List[TaskResponse])
async def get_all_tasks(
    category: ServiceCategory = None,
    status: TaskStatus = None,
    authorization: str = Header(None)
):
    try:
        user_id = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            user = get_current_user_from_token(token)
            if user:
                user_id = user['id']
        
        tasks = get_tasks(customer_id=user_id, category=category, status=status)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/available", response_model=List[TaskResponse])
async def get_available_tasks(
    category: ServiceCategory = None
):
    try:
        tasks = get_tasks(category=category, status=TaskStatus.OPEN)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/my", response_model=List[TaskResponse])
async def get_my_tasks(
    authorization: str = Header(None)
):
    """Получить все задачи текущего пользователя"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        
        # Получаем задачи пользователя из базы данных
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, customer_id, category, description, address, date, 
                       price, photos, status, created_at, updated_at
                FROM tasks 
                WHERE customer_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            tasks = cursor.fetchall()
            
            result = []
            for task in tasks:
                # Получаем количество откликов
                cursor.execute("SELECT COUNT(*) FROM project_responses WHERE task_id = ?", (task[0],))
                responses_count = cursor.fetchone()[0]
                
                # Десериализуем фотографии
                import json
                photos = json.loads(task[8]) if task[8] else []
                
                task_dict = {
                    "id": str(task[0]),
                    "title": task[1],
                    "customer_id": task[2],
                    "category": task[3],
                    "description": task[4],
                    "address": task[5],
                    "date": task[6],
                    "price": task[7],
                    "photos": photos,
                    "status": task[9],
                    "created_at": task[10],
                    "updated_at": task[11],
                    "responses_count": responses_count
                }
                result.append(task_dict)
            
            print(f"Found {len(result)} tasks for user {user_id}")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user tasks: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: str  # Принимаем строку и преобразуем в int
):
    try:
        print(f"GET /tasks/{task_id} - Getting task with ID: {task_id}")
        
        # Преобразуем строку в int
        try:
            task_id_int = int(task_id)
        except ValueError:
            print(f"Invalid task ID format: {task_id}")
            raise HTTPException(status_code=400, detail="Invalid task ID format")
        
        task = get_task(task_id_int)
        print(f"Task found: {task}")
        
        if not task:
            print(f"Task not found with ID: {task_id_int}")
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting task {task_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}", response_model=dict)
async def update_task_by_id(
    task_id: str,
    task_data: TaskUpdate,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Преобразуем строку в int
        try:
            task_id_int = int(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task ID format")
        
        user_id = user['id']
        result = update_task(task_id_int, task_data, user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task_by_id(
    task_id: str,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Преобразуем строку в int
        try:
            task_id_int = int(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task ID format")
        
        user_id = user['id']
        result = delete_task(task_id_int, user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/service-offer", response_model=dict)
async def create_or_update_service_offer(
    service_data: ServiceOfferCreate,
    authorization: str = Header(None)
):
    try:
        print(f"POST /service-offer - Received service_data: {service_data}")
        print(f"POST /service-offer - Authorization header: {authorization}")
        
        if not authorization:
            print("POST /service-offer - No authorization header")
            raise HTTPException(status_code=401, detail="No authorization header")
        
        if not authorization.startswith("Bearer "):
            print("POST /service-offer - Invalid authorization format")
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization.replace("Bearer ", "")
        print(f"POST /service-offer - Extracted token: {token[:20]}...")
        
        user = get_current_user_from_token(token)
        if not user:
            print("POST /service-offer - Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"POST /service-offer - User found: {user}")
        user_id = user['id']
        
        # Сначала удаляем все существующие предложения для этого пользователя
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM service_offers WHERE performer_id = ?", (user_id,))
            deleted_count = cursor.rowcount
            print(f"Deleted {deleted_count} existing offers for user {user_id}")
            conn.commit()
        
        # Создаем предложения для каждой категории
        results = []
        for category in service_data.service_categories:
            result = create_service_offer(user_id, category, service_data.description, service_data.hourly_rate)
            results.append(result)
        
        # Проверяем, сколько предложений создалось
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM service_offers WHERE performer_id = ?", (user_id,))
            final_count = cursor.fetchone()[0]
            print(f"Final offers count for user {user_id}: {final_count}")
        
        print(f"Total offers created: {len(results)}")
        return {"success": True, "message": f"Created {len(results)} service offers", "results": results}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_or_update_service_offer: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/service-offer", response_model=dict)
async def get_user_service_offers(
    authorization: str = Header(None)
):
    try:
        print(f"GET /service-offer - Authorization header: {authorization}")
        
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        print(f"GET /service-offer - Extracted token: {token[:20]}...")
        
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"GET /service-offer - User found: {user}")
        user_id = user['id']
        offers = get_service_offer(user_id)
        print(f"GET /service-offer - Offers: {offers}")
        return offers
    except Exception as e:
        print(f"Error in get_user_service_offers: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.put("/service-offer/{offer_id}", response_model=dict)
async def update_user_service_offer(
    offer_id: int,
    description: str = None,
    hourly_rate: float = None,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        
        kwargs = {}
        if description is not None:
            kwargs['description'] = description
        if hourly_rate is not None:
            kwargs['hourly_rate'] = hourly_rate
        
        result = update_service_offer(offer_id, user_id, **kwargs)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tasks/{task_id}/respond", response_model=dict)
async def respond_to_task(
    task_id: str,
    response_data: ProjectResponseCreate,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Преобразуем строку в int
        try:
            task_id_int = int(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task ID format")
        
        user_id = user['id']
        result = create_project_response(task_id_int, user_id, response_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{task_id}/responses", response_model=List[ProjectResponse])
async def get_task_responses_api(
    task_id: str,  # Принимаем строку и преобразуем в int
    authorization: str = Header(None)
):
    try:
        print(f"GET /tasks/{task_id}/responses - Getting responses for task: {task_id}")
        
        if not authorization or not authorization.startswith("Bearer "):
            print("Invalid authorization header")
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            print("Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Преобразуем строку в int
        try:
            task_id_int = int(task_id)
        except ValueError:
            print(f"Invalid task ID format: {task_id}")
            raise HTTPException(status_code=400, detail="Invalid task ID format")
        
        user_id = user['id']
        print(f"Getting responses for task {task_id_int} by user {user_id}")
        
        responses = get_task_responses(task_id_int, user_id)
        print(f"Found {len(responses)} responses")
        
        return responses
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting task responses: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/responses/{response_id}/status", response_model=dict)
async def update_response_status_api(
    response_id: int,
    status: ResponseStatus,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        result = update_response_status(response_id, status, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/notifications", response_model=List[Notification])
async def get_user_notifications(
    authorization: str = Header(None),
    limit: int = 50
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        notifications = get_notifications(user_id, limit)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.put("/notifications/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: int,
    authorization: str = Header(None)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user['id']
        result = mark_notification_read(notification_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
