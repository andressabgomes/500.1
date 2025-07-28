from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, date
from models import Attendance, AttendanceCreate, AttendanceUpdate, ApiResponse, PaginatedResponse
from services import AttendanceService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

router = APIRouter(prefix="/attendance", tags=["attendance"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    return db

@router.post("/", response_model=ApiResponse)
async def create_attendance(attendance_data: AttendanceCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new attendance record"""
    try:
        attendance_service = AttendanceService(db)
        
        attendance_dict = attendance_data.dict()
        attendance = await attendance_service.create(attendance_dict)
        
        return ApiResponse(
            success=True,
            message="Attendance created successfully",
            data=attendance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{attendance_id}", response_model=ApiResponse)
async def get_attendance(attendance_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get attendance by ID"""
    try:
        attendance_service = AttendanceService(db)
        attendance = await attendance_service.get_by_id(attendance_id)
        
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")
        
        return ApiResponse(
            success=True,
            message="Attendance retrieved successfully",
            data=attendance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedResponse)
async def get_attendance_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all attendance records with pagination and filters"""
    try:
        attendance_service = AttendanceService(db)
        
        # Build filters
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if status:
            filters["status"] = status
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.combine(date_from, datetime.min.time())
            if date_to:
                date_filter["$lte"] = datetime.combine(date_to, datetime.max.time())
            filters["date"] = date_filter
        
        attendance_records = await attendance_service.get_all(skip=skip, limit=limit, filters=filters)
        total = await attendance_service.count(filters)
        
        return PaginatedResponse(
            success=True,
            message="Attendance records retrieved successfully",
            data=attendance_records,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{attendance_id}", response_model=ApiResponse)
async def update_attendance(
    attendance_id: str, 
    attendance_data: AttendanceUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update attendance record"""
    try:
        attendance_service = AttendanceService(db)
        
        # Check if attendance exists
        existing_attendance = await attendance_service.get_by_id(attendance_id)
        if not existing_attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")
        
        # Update attendance
        update_dict = attendance_data.dict(exclude_unset=True)
        attendance = await attendance_service.update(attendance_id, update_dict)
        
        return ApiResponse(
            success=True,
            message="Attendance updated successfully",
            data=attendance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{attendance_id}", response_model=ApiResponse)
async def delete_attendance(attendance_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete attendance record"""
    try:
        attendance_service = AttendanceService(db)
        
        # Check if attendance exists
        existing_attendance = await attendance_service.get_by_id(attendance_id)
        if not existing_attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")
        
        # Delete attendance
        deleted = await attendance_service.delete(attendance_id)
        
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete attendance")
        
        return ApiResponse(
            success=True,
            message="Attendance deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_attendance_by_user(
    user_id: str, 
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get attendance by user and date range"""
    try:
        attendance_service = AttendanceService(db)
        
        if date_from and date_to:
            start_date = datetime.combine(date_from, datetime.min.time())
            end_date = datetime.combine(date_to, datetime.max.time())
            attendance_records = await attendance_service.get_by_user_range(user_id, start_date, end_date)
        else:
            attendance_records = await attendance_service.get_all(filters={"user_id": user_id})
        
        return ApiResponse(
            success=True,
            message="Attendance records retrieved successfully",
            data=attendance_records
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/date/{date}", response_model=ApiResponse)
async def get_attendance_by_user_date(
    user_id: str, 
    date: date, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get attendance by user and specific date"""
    try:
        attendance_service = AttendanceService(db)
        
        date_time = datetime.combine(date, datetime.min.time())
        attendance = await attendance_service.get_by_user_and_date(user_id, date_time)
        
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance not found")
        
        return ApiResponse(
            success=True,
            message="Attendance retrieved successfully",
            data=attendance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkin", response_model=ApiResponse)
async def check_in(
    user_id: str, 
    timestamp: Optional[datetime] = None, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Check in user"""
    try:
        attendance_service = AttendanceService(db)
        
        attendance = await attendance_service.check_in(user_id, timestamp)
        
        return ApiResponse(
            success=True,
            message="Check-in successful",
            data=attendance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout", response_model=ApiResponse)
async def check_out(
    user_id: str, 
    timestamp: Optional[datetime] = None, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Check out user"""
    try:
        attendance_service = AttendanceService(db)
        
        attendance = await attendance_service.check_out(user_id, timestamp)
        
        if not attendance:
            raise HTTPException(status_code=404, detail="No check-in found for today")
        
        return ApiResponse(
            success=True,
            message="Check-out successful",
            data=attendance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))