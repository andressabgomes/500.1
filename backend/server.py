from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime

# Import route modules
from routes.users import router as users_router
from routes.customers import router as customers_router
from routes.tickets import router as tickets_router
from routes.goals import router as goals_router
from routes.attendance import router as attendance_router
from routes.monitoring import router as monitoring_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection - with fallback for Railway
mongo_url = os.environ.get('MONGO_URL', os.environ.get('DATABASE_URL', 'mongodb://localhost:27017'))
client = AsyncIOMotorClient(mongo_url)
db_name = os.environ.get('DB_NAME', os.environ.get('DATABASE_NAME', 'starprint_crm'))
db = client[db_name]

# Create the main app without a prefix
app = FastAPI(
    title="StarPrint CRM API",
    description="Comprehensive CRM API for StarPrint Etiquetas e Rótulos",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(users_router)
api_router.include_router(customers_router)
api_router.include_router(tickets_router)
api_router.include_router(goals_router)
api_router.include_router(attendance_router)
api_router.include_router(monitoring_router)

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "StarPrint CRM API v1.0.0"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

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
