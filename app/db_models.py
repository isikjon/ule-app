from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PERFORMER = "performer"

class TaskStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ResponseStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class ServiceCategory(str, enum.Enum):
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

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    patronymic = Column(String, nullable=True)
    email = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    city = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    tasks = relationship("Task", back_populates="customer")
    responses = relationship("ProjectResponse", back_populates="performer")
    service_offers = relationship("ServiceOffer", back_populates="performer")
    notifications = relationship("Notification", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(ServiceCategory), nullable=False)
    address = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    photos = Column(Text, nullable=True)  # JSON строка с путями к фото
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    customer = relationship("User", back_populates="tasks")
    responses = relationship("ProjectResponse", back_populates="task")

class ServiceOffer(Base):
    __tablename__ = "service_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    performer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(ServiceCategory), nullable=False)
    description = Column(Text, nullable=True)
    hourly_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    performer = relationship("User", back_populates="service_offers")

class ProjectResponse(Base):
    __tablename__ = "project_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    performer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_price = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(Enum(ResponseStatus), default=ResponseStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    task = relationship("Task", back_populates="responses")
    performer = relationship("User", back_populates="responses")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="notifications")
