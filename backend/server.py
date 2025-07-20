from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
SECRET_KEY = "starprint_crm_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    manager = "manager"
    agent = "agent"

class TeamMemberStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"

class ShiftStatus(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    missed = "missed"

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    role: UserRole
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: UserRole = UserRole.agent

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    created_at: datetime

class TeamMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    role: UserRole
    status: TeamMemberStatus
    phone: Optional[str] = None
    department: Optional[str] = None
    hire_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TeamMemberCreate(BaseModel):
    name: str
    email: str
    role: UserRole
    phone: Optional[str] = None
    department: Optional[str] = None
    hire_date: datetime

class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[TeamMemberStatus] = None
    phone: Optional[str] = None
    department: Optional[str] = None

class Shift(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_member_id: str
    team_member_name: str
    start_time: datetime
    end_time: datetime
    status: ShiftStatus
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ShiftCreate(BaseModel):
    team_member_id: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

class DashboardStats(BaseModel):
    total_team_members: int
    active_members: int
    members_on_shift: int
    completed_shifts_today: int
    upcoming_shifts: int
    missed_shifts: int

# Authentication functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)

# Authentication routes
@api_router.post("/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
        hashed_password=hashed_password
    )
    
    await db.users.insert_one(user.dict())
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.dict())
    }

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    # Find user by email
    user_data = await db.users.find_one({"email": login_data.email})
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    user = User(**user_data)
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.dict())
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Team Management routes
@api_router.get("/team-members", response_model=List[TeamMember])
async def get_team_members(current_user: User = Depends(get_current_user)):
    team_members = await db.team_members.find().to_list(1000)
    return [TeamMember(**member) for member in team_members]

@api_router.post("/team-members", response_model=TeamMember)
async def create_team_member(
    member_data: TeamMemberCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.manager:
        raise HTTPException(status_code=403, detail="Only managers can create team members")
    
    member = TeamMember(
        **member_data.dict(),
        status=TeamMemberStatus.active
    )
    
    await db.team_members.insert_one(member.dict())
    return member

@api_router.put("/team-members/{member_id}", response_model=TeamMember)
async def update_team_member(
    member_id: str,
    update_data: TeamMemberUpdate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.manager:
        raise HTTPException(status_code=403, detail="Only managers can update team members")
    
    existing_member = await db.team_members.find_one({"id": member_id})
    if not existing_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.team_members.update_one({"id": member_id}, {"$set": update_dict})
    
    updated_member = await db.team_members.find_one({"id": member_id})
    return TeamMember(**updated_member)

@api_router.delete("/team-members/{member_id}")
async def delete_team_member(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.manager:
        raise HTTPException(status_code=403, detail="Only managers can delete team members")
    
    result = await db.team_members.delete_one({"id": member_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    # Also delete associated shifts
    await db.shifts.delete_many({"team_member_id": member_id})
    
    return {"message": "Team member deleted successfully"}

# Shift Management routes
@api_router.get("/shifts", response_model=List[Shift])
async def get_shifts(current_user: User = Depends(get_current_user)):
    shifts = await db.shifts.find().sort("start_time", 1).to_list(1000)
    return [Shift(**shift) for shift in shifts]

@api_router.post("/shifts", response_model=Shift)
async def create_shift(
    shift_data: ShiftCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.manager:
        raise HTTPException(status_code=403, detail="Only managers can create shifts")
    
    # Get team member info
    team_member = await db.team_members.find_one({"id": shift_data.team_member_id})
    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    shift = Shift(
        **shift_data.dict(),
        team_member_name=team_member["name"],
        status=ShiftStatus.scheduled
    )
    
    await db.shifts.insert_one(shift.dict())
    return shift

@api_router.put("/shifts/{shift_id}/status")
async def update_shift_status(
    shift_id: str,
    status: ShiftStatus,
    current_user: User = Depends(get_current_user)
):
    existing_shift = await db.shifts.find_one({"id": shift_id})
    if not existing_shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    await db.shifts.update_one({"id": shift_id}, {"$set": {"status": status}})
    
    updated_shift = await db.shifts.find_one({"id": shift_id})
    return Shift(**updated_shift)

# Dashboard routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    # Get current time boundaries
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Count team members
    total_team_members = await db.team_members.count_documents({})
    active_members = await db.team_members.count_documents({"status": "active"})
    
    # Count shifts for today
    members_on_shift = await db.shifts.count_documents({
        "start_time": {"$lte": now},
        "end_time": {"$gte": now},
        "status": "in_progress"
    })
    
    completed_shifts_today = await db.shifts.count_documents({
        "start_time": {"$gte": today_start, "$lt": today_end},
        "status": "completed"
    })
    
    upcoming_shifts = await db.shifts.count_documents({
        "start_time": {"$gte": now},
        "status": "scheduled"
    })
    
    missed_shifts = await db.shifts.count_documents({
        "end_time": {"$lt": now},
        "status": "scheduled"
    })
    
    return DashboardStats(
        total_team_members=total_team_members,
        active_members=active_members,
        members_on_shift=members_on_shift,
        completed_shifts_today=completed_shifts_today,
        upcoming_shifts=upcoming_shifts,
        missed_shifts=missed_shifts
    )

@api_router.get("/dashboard/recent-shifts", response_model=List[Shift])
async def get_recent_shifts(current_user: User = Depends(get_current_user)):
    shifts = await db.shifts.find().sort("start_time", -1).limit(10).to_list(10)
    return [Shift(**shift) for shift in shifts]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()