from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    PERFORMER = "performer"

class ServiceCategory(str, Enum):
    MOVERS = "movers"
    COMPUTER_HELP = "computer_help"
    BEAUTY_HEALTH = "beauty_health"
    HANDYMAN = "handyman"
    HOUSEHOLD_HELP = "household_help"
    LABORERS = "laborers"
    APPLIANCE_REPAIR = "appliance_repair"
    CONSTRUCTION = "construction"
    TUTORING = "tutoring"
    PLUMBING = "plumbing"
    FURNITURE = "furniture"
    CLEANING = "cleaning"
    ELECTRICAL = "electrical"
    LEGAL = "legal"
    OTHER = "other"

class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ResponseStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    city: Optional[str] = None

class TaskCreate(BaseModel):
    service_category: ServiceCategory
    description: str = Field(..., min_length=10)
    address: str
    date: str
    price: Optional[float] = None
    photos: Optional[List[str]] = []

class TaskResponse(BaseModel):
    id: str  # Оставляем str для совместимости с фронтендом
    service_category: ServiceCategory
    description: str
    address: str
    date: str
    price: Optional[float]
    photos: List[str]
    status: TaskStatus
    customer_phone: str
    created_at: datetime
    responses_count: int

class TaskUpdate(BaseModel):
    service_category: Optional[ServiceCategory] = None
    description: Optional[str] = None
    address: Optional[str] = None
    date: Optional[str] = None
    price: Optional[float] = None
    photos: Optional[List[str]] = None

class ServiceOffer(BaseModel):
    id: Optional[int] = None
    performer_id: int
    service_categories: List[ServiceCategory]
    description: Optional[str] = None
    hourly_rate: Optional[float] = None
    created_at: Optional[datetime] = None

class ServiceOfferCreate(BaseModel):
    service_categories: List[ServiceCategory]
    description: Optional[str] = None
    hourly_rate: Optional[float] = None

class ProjectResponse(BaseModel):
    id: int
    task_id: str  # Оставляем str для совместимости
    performer_phone: str
    offer_price: float
    message: Optional[str] = None
    status: ResponseStatus = ResponseStatus.PENDING
    created_at: datetime

class ProjectResponseCreate(BaseModel):
    offer_price: float
    message: Optional[str] = None

class Notification(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool = False
    created_at: datetime
