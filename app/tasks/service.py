import uuid
import json
from typing import Dict, List, Optional
from datetime import datetime
from app.database import get_db
from app.models import (
    TaskCreate, TaskResponse, TaskUpdate, TaskStatus,
    ServiceOffer as ServiceOfferModel, ProjectResponse as ProjectResponseModel, 
    ProjectResponseCreate, Notification as NotificationModel
)

def create_task(task_data: TaskCreate, customer_id: int) -> dict:
    """Создать новую задачу"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Обрабатываем фотографии - сериализуем список в JSON строку
        photos_str = json.dumps(task_data.photos) if task_data.photos else None
        
        # Если цена не указана, устанавливаем 0
        price = task_data.price if task_data.price is not None else 0.0
        
        # Создаем заголовок из описания
        title = task_data.description[:50] + "..." if len(task_data.description) > 50 else task_data.description
        
        cursor.execute("""
            INSERT INTO tasks (title, description, category, address, date, price, photos, status, customer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)
        """, (
            title,
            task_data.description,
            task_data.service_category.value,  # Используем .value для enum
            task_data.address,
            task_data.date,
            price,
            photos_str,
            customer_id
        ))
        
        task_id = cursor.lastrowid
        conn.commit()
        
        return {"success": True, "task_id": task_id, "message": "Task created successfully"}

def get_tasks(customer_id: int = None, category: str = None, status: str = None) -> List[TaskResponse]:
    """Получить список задач"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT t.id, t.title, t.description, t.category, t.address, t.date, t.price, t.photos, t.status, u.phone as customer_phone, t.created_at FROM tasks t JOIN users u ON t.customer_id = u.id WHERE 1=1"
        params = []
        
        if customer_id:
            query += " AND t.customer_id = ?"
            params.append(customer_id)
        if category:
            query += " AND t.category = ?"
            params.append(category)
        if status:
            query += " AND t.status = ?"
            params.append(status)
        
        query += " ORDER BY t.created_at DESC"
        
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        
        result = []
        for task in tasks:
            # Получаем количество откликов
            cursor.execute("SELECT COUNT(*) FROM project_responses WHERE task_id = ?", (task[0],))  # id находится в первом элементе
            responses_count = cursor.fetchone()[0]
            
            # Обрабатываем фотографии - десериализуем JSON строку в список
            photos = []
            if task[7]:  # photos
                try:
                    photos = json.loads(task[7])
                except (json.JSONDecodeError, TypeError):
                    photos = []
            else:
                photos = []
            
            result.append(TaskResponse(
                id=str(task[0]),  # id как строка
                service_category=task[3],  # category
                description=task[2],  # description
                address=task[4],  # address
                date=task[5],  # date
                price=task[6],  # price
                photos=photos,  # обработанный список фотографий
                status=task[8],  # status
                customer_phone=task[9],  # customer_phone (из JOIN)
                created_at=datetime.fromisoformat(task[10]) if isinstance(task[10], str) else task[10],  # created_at
                responses_count=responses_count
            ))
        
        return result

def get_task(task_id: int) -> Optional[TaskResponse]:
    """Получить задачу по ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.title, t.description, t.category, t.address, t.date, t.price, t.photos, t.status, u.phone as customer_phone, t.created_at
            FROM tasks t 
            JOIN users u ON t.customer_id = u.id 
            WHERE t.id = ?
        """, (task_id,))
        
        task = cursor.fetchone()
        if not task:
            return None
        
        # Получаем количество откликов
        cursor.execute("SELECT COUNT(*) FROM project_responses WHERE task_id = ?", (task_id,))
        responses_count = cursor.fetchone()[0]
        
        # Обрабатываем фотографии - десериализуем JSON строку в список
        photos = []
        if task[7]:  # photos
            try:
                photos = json.loads(task[7])
            except (json.JSONDecodeError, TypeError):
                photos = []
        else:
            photos = []
        
        return TaskResponse(
            id=str(task[0]),  # id как строка
            service_category=task[3],  # category
            description=task[2],  # description
            address=task[4],  # address
            date=task[5],  # date
            price=task[6],  # price
            photos=photos,  # обработанный список фотографий
            status=task[8],  # status
            customer_phone=task[9],  # customer_phone (из JOIN)
            created_at=datetime.fromisoformat(task[10]) if isinstance(task[10], str) else task[10],  # created_at
            responses_count=responses_count
        )

def update_task(task_id: int, task_data: TaskUpdate, customer_id: int) -> dict:
    """Обновить задачу"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что задача существует и принадлежит пользователю
        cursor.execute("SELECT id FROM tasks WHERE id = ? AND customer_id = ?", (task_id, customer_id))
        if not cursor.fetchone():
            raise ValueError("Task not found or access denied")
        
        # Формируем SQL для обновления
        update_fields = []
        values = []
        
        if task_data.service_category is not None:
            update_fields.append("category = ?")
            values.append(task_data.service_category.value)  # Используем .value для enum
        if task_data.description is not None:
            update_fields.append("description = ?")
            update_fields.append("title = ?")
            values.append(task_data.description)
            values.append(task_data.description[:50] + "..." if len(task_data.description) > 50 else task_data.description)
        if task_data.address is not None:
            update_fields.append("address = ?")
            values.append(task_data.address)
        if task_data.date is not None:
            update_fields.append("date = ?")
            values.append(task_data.date)
        if task_data.price is not None:
            update_fields.append("price = ?")
            values.append(task_data.price)
        if task_data.photos is not None:
            update_fields.append("photos = ?")
            photos_str = json.dumps(task_data.photos) if task_data.photos else None
            values.append(photos_str)
        if task_data.status is not None:
            update_fields.append("status = ?")
            values.append(task_data.status.value)  # Используем .value для enum
        
        if not update_fields:
            return {"success": True, "message": "No fields to update"}
        
        # Добавляем updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(task_id)
        
        # Выполняем обновление
        sql = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        
        return {"success": True, "message": "Task updated successfully"}

def delete_task(task_id: int, customer_id: int) -> dict:
    """Удалить задачу"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что задача существует и принадлежит пользователю
        cursor.execute("SELECT id FROM tasks WHERE id = ? AND customer_id = ?", (task_id, customer_id))
        if not cursor.fetchone():
            raise ValueError("Task not found or access denied")
        
        # Удаляем связанные отклики
        cursor.execute("DELETE FROM project_responses WHERE task_id = ?", (task_id,))
        
        # Удаляем задачу
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        
        return {"success": True, "message": "Task deleted successfully"}

def create_service_offer(performer_id: int, category: str, description: str = None, hourly_rate: float = None) -> dict:
    """Создать предложение услуг"""
    print(f"Creating service offer: performer_id={performer_id}, category={category}, description={description}, hourly_rate={hourly_rate}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Создаем новое предложение (не удаляем существующие здесь)
        cursor.execute("""
            INSERT INTO service_offers (performer_id, category, description, hourly_rate, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (performer_id, category, description, hourly_rate))
        
        offer_id = cursor.lastrowid
        conn.commit()
        print(f"Created service offer with ID: {offer_id}")
        
        return {"success": True, "offer_id": offer_id, "message": "Service offer created successfully"}

def get_service_offer(performer_id: int) -> dict:
    """Получить предложения услуг исполнителя"""
    print(f"Getting service offers for performer_id: {performer_id}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, сколько всего записей в таблице
        cursor.execute("SELECT COUNT(*) FROM service_offers")
        total_count = cursor.fetchone()[0]
        print(f"Total records in service_offers table: {total_count}")
        
        cursor.execute("""
            SELECT category, description, hourly_rate FROM service_offers 
            WHERE performer_id = ?
        """, (performer_id,))
        
        offers = cursor.fetchall()
        print(f"Database offers for performer {performer_id}: {offers}")
        print(f"Number of offers found: {len(offers)}")
        
        if not offers:
            print("No offers found, returning empty categories")
            return {"service_categories": []}
        
        # Группируем все категории в один объект
        categories = [offer[0] for offer in offers]
        print(f"Extracted categories: {categories}")
        description = offers[0][1] if offers else None
        hourly_rate = offers[0][2] if offers else None
        
        result = {
            "service_categories": categories,
            "description": description,
            "hourly_rate": hourly_rate
        }
        print(f"Returning result: {result}")
        return result

def update_service_offer(offer_id: int, performer_id: int, **kwargs) -> dict:
    """Обновить предложение услуг"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что предложение существует и принадлежит пользователю
        cursor.execute("SELECT id FROM service_offers WHERE id = ? AND performer_id = ?", (offer_id, performer_id))
        if not cursor.fetchone():
            raise ValueError("Service offer not found or access denied")
        
        # Формируем SQL для обновления
        update_fields = []
        values = []
        
        for key, value in kwargs.items():
            if value is not None and key in ['description', 'hourly_rate']:
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        if not update_fields:
            return {"success": True, "message": "No fields to update"}
        
        # Добавляем updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(offer_id)
        
        # Выполняем обновление
        sql = f"UPDATE service_offers SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        
        return {"success": True, "message": "Service offer updated successfully"}

def create_project_response(task_id: int, performer_id: int, response_data: ProjectResponseCreate) -> dict:
    """Создать отклик на проект"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что задача существует
        cursor.execute("SELECT customer_id FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            raise ValueError("Task not found")
        
        # Проверяем, что исполнитель не является заказчиком
        if task[0] == performer_id:  # customer_id находится в первом элементе
            raise ValueError("Cannot respond to your own task")
        
        # Проверяем, что отклик еще не существует
        cursor.execute("SELECT id FROM project_responses WHERE task_id = ? AND performer_id = ?", (task_id, performer_id))
        if cursor.fetchone():
            raise ValueError("Response already exists")
        
        # Создаем отклик
        cursor.execute("""
            INSERT INTO project_responses (task_id, performer_id, offer_price, message, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (task_id, performer_id, response_data.offer_price, response_data.message))
        
        response_id = cursor.lastrowid
        conn.commit()
        
        # Создаем уведомление для заказчика
        create_notification(
            user_id=task[0],  # customer_id находится в первом элементе
            title="Новый отклик на задачу",
            message=f"Получен новый отклик на вашу задачу от исполнителя"
        )
        
        return {"success": True, "response_id": response_id, "message": "Response created successfully"}

def get_task_responses(task_id: int, customer_id: int) -> List[ProjectResponseModel]:
    """Получить отклики на задачу"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что заказчик является владельцем задачи
        cursor.execute("SELECT id FROM tasks WHERE id = ? AND customer_id = ?", (task_id, customer_id))
        if not cursor.fetchone():
            raise ValueError("Task not found or access denied")
        
        cursor.execute("""
            SELECT pr.id, pr.task_id, u.phone as performer_phone, pr.offer_price, pr.message, pr.status, pr.created_at
            FROM project_responses pr 
            JOIN users u ON pr.performer_id = u.id 
            WHERE pr.task_id = ?
        """, (task_id,))
        
        responses = cursor.fetchall()
        
        result = []
        for response in responses:
            result.append(ProjectResponseModel(
                id=response[0],  # id
                task_id=str(response[1]),  # task_id как строка
                performer_phone=response[2],  # performer_phone (из JOIN)
                offer_price=response[3],  # offer_price
                message=response[4],  # message
                status=response[5],  # status
                created_at=datetime.fromisoformat(response[6]) if isinstance(response[6], str) else response[6]  # created_at
            ))
        
        return result

def update_response_status(response_id: int, status: str, customer_id: int) -> dict:
    """Обновить статус отклика"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что отклик существует и заказчик является владельцем задачи
        cursor.execute("""
            SELECT pr.id FROM project_responses pr 
            JOIN tasks t ON pr.task_id = t.id 
            WHERE pr.id = ? AND t.customer_id = ?
        """, (response_id, customer_id))
        
        if not cursor.fetchone():
            raise ValueError("Response not found or access denied")
        
        # Обновляем статус
        cursor.execute("""
            UPDATE project_responses 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (status, response_id))
        
        conn.commit()
        
        # Создаем уведомление для исполнителя
        cursor.execute("SELECT performer_id FROM project_responses WHERE id = ?", (response_id,))
        performer_result = cursor.fetchone()
        performer_id = performer_result[0]  # performer_id находится в первом элементе
        
        create_notification(
            user_id=performer_id,
            title="Статус отклика изменен",
            message=f"Статус вашего отклика изменен на: {status}"
        )
        
        return {"success": True, "message": "Response status updated successfully"}

def create_notification(user_id: int, title: str, message: str) -> dict:
    """Создать уведомление"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, is_read, created_at)
            VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP)
        """, (user_id, title, message))
        
        notification_id = cursor.lastrowid
        conn.commit()
        
        return {"success": True, "notification_id": notification_id, "message": "Notification created successfully"}

def get_notifications(user_id: int, limit: int = 50) -> List[NotificationModel]:
    """Получить уведомления пользователя"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT n.id, n.title, n.message, n.is_read, n.created_at FROM notifications n 
            WHERE n.user_id = ? 
            ORDER BY n.created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        
        notifications = cursor.fetchall()
        
        result = []
        for notification in notifications:
            result.append(NotificationModel(
                id=notification[0],  # id
                title=notification[1],  # title
                message=notification[2],  # message
                is_read=bool(notification[3]),  # is_read как boolean
                created_at=datetime.fromisoformat(notification[4]) if isinstance(notification[4], str) else notification[4]  # created_at
            ))
        
        return result

def mark_notification_read(notification_id: int, user_id: int) -> dict:
    """Отметить уведомление как прочитанное"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем, что уведомление существует и принадлежит пользователю
        cursor.execute("SELECT id FROM notifications WHERE id = ? AND user_id = ?", (notification_id, user_id))
        if not cursor.fetchone():
            raise ValueError("Notification not found or access denied")
        
        # Отмечаем как прочитанное
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        
        return {"success": True, "message": "Notification marked as read"}