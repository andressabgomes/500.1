from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# Base Model
class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    SUPERVISOR = "supervisor"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    AVAILABLE = "available"
    BREAK = "break"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EARLY_LEAVE = "early_leave"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    PHONE = "phone"
    CHAT = "chat"


# User/Team Models
class User(BaseEntity):
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus = UserStatus.AVAILABLE
    phone: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: List[str] = []
    schedule_id: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    phone: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: List[str] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    is_active: Optional[bool] = None


# Schedule Models
class Schedule(BaseEntity):
    name: str
    user_id: str
    start_time: str  # "09:00"
    end_time: str    # "18:00"
    days_of_week: List[int]  # [0, 1, 2, 3, 4] (0=Monday)
    is_active: bool = True


class ScheduleCreate(BaseModel):
    name: str
    user_id: str
    start_time: str
    end_time: str
    days_of_week: List[int]


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    is_active: Optional[bool] = None


# Attendance Models
class Attendance(BaseEntity):
    user_id: str
    date: datetime
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    break_start: Optional[datetime] = None
    break_end: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: Optional[str] = None
    hours_worked: Optional[float] = None


class AttendanceCreate(BaseModel):
    user_id: str
    date: datetime
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    break_start: Optional[datetime] = None
    break_end: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: Optional[str] = None


class AttendanceUpdate(BaseModel):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    break_start: Optional[datetime] = None
    break_end: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None


# Goal Models
class Goal(BaseEntity):
    title: str
    description: Optional[str] = None
    target_value: float
    current_value: float = 0.0
    unit: str  # "tickets", "calls", "satisfaction", etc.
    user_id: Optional[str] = None  # Individual goal
    team_id: Optional[str] = None  # Team goal
    start_date: datetime
    end_date: datetime
    is_active: bool = True


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_value: float
    unit: str
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    start_date: datetime
    end_date: datetime


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


# Customer Models
class Customer(BaseEntity):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []
    is_active: bool = True


class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


# Support Ticket Models
class Ticket(BaseEntity):
    ticket_number: str = Field(default_factory=lambda: f"TK-{str(uuid.uuid4())[:8].upper()}")
    title: str
    description: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    channel: Channel
    customer_id: str
    assigned_to: Optional[str] = None  # User ID
    resolution: Optional[str] = None
    satisfaction_rating: Optional[int] = None  # 1-5
    satisfaction_comment: Optional[str] = None
    tags: List[str] = []
    attachments: List[str] = []  # URLs/paths to attachments
    estimated_resolution: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    channel: Channel
    customer_id: str
    assigned_to: Optional[str] = None
    tags: List[str] = []
    estimated_resolution: Optional[datetime] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    satisfaction_rating: Optional[int] = None
    satisfaction_comment: Optional[str] = None
    tags: Optional[List[str]] = None
    estimated_resolution: Optional[datetime] = None


# Monitoring Models
class MonitoringMetric(BaseEntity):
    name: str
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    category: str  # "performance", "quality", "volume", etc.
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class MonitoringMetricCreate(BaseModel):
    name: str
    value: float
    unit: str
    category: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


# Report Models
class Report(BaseEntity):
    title: str
    description: Optional[str] = None
    type: str  # "daily", "weekly", "monthly", "custom"
    parameters: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    generated_by: str  # User ID
    start_date: datetime
    end_date: datetime
    is_public: bool = False


class ReportCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str
    parameters: Dict[str, Any] = {}
    start_date: datetime
    end_date: datetime
    is_public: bool = False


# Settings Models
class Settings(BaseEntity):
    key: str
    value: Any
    description: Optional[str] = None
    category: str  # "system", "notification", "integration", etc.
    is_public: bool = False
    updated_by: str  # User ID


class SettingsCreate(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None
    category: str
    is_public: bool = False


class SettingsUpdate(BaseModel):
    value: Any
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None


# Response Models
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    success: bool
    message: str
    data: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int