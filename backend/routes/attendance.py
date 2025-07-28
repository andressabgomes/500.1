from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from models import Attendance, AttendanceCreate, AttendanceUpdate, ApiResponse, PaginatedResponse
from services import AttendanceService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from datetime import datetime

router = APIRouter(prefix="/attendance", tags=["attendance"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ.get('MONGO_URL', os.environ.get('DATABASE_URL', 'mongodb://localhost:27017'))
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', os.environ.get('DATABASE_NAME', 'starprint_crm'))
    db = client[db_name]
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
            message="Attendance record created successfully",
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
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        return ApiResponse(
            success=True,
            message="Attendance record retrieved successfully",
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
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        # Update attendance
        update_dict = attendance_data.dict(exclude_unset=True)
        attendance = await attendance_service.update(attendance_id, update_dict)
        
        return ApiResponse(
            success=True,
            message="Attendance record updated successfully",
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
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        # Delete attendance
        deleted = await attendance_service.delete(attendance_id)
        
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete attendance record")
        
        return ApiResponse(
            success=True,
            message="Attendance record deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_attendance_by_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get attendance records by user"""
    try:
        attendance_service = AttendanceService(db)
        attendance_records = await attendance_service.get_all(filters={"user_id": user_id})
        
        return ApiResponse(
            success=True,
            message="Attendance records retrieved successfully",
            data=attendance_records
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/date/{date}", response_model=ApiResponse)
async def get_attendance_by_user_and_date(
    user_id: str, 
    date: str,  # Format: YYYY-MM-DD
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get attendance by user and date"""
    try:
        attendance_service = AttendanceService(db)
        
        # Parse date
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        attendance = await attendance_service.get_by_user_and_date(user_id, date_obj)
        
        if not attendance:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        return ApiResponse(
            success=True,
            message="Attendance record retrieved successfully",
            data=attendance
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
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
            message="Checked in successfully",
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
            raise HTTPException(status_code=404, detail="No check-in record found for today")
        
        return ApiResponse(
            success=True,
            message="Checked out successfully",
            data=attendance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/date-range/{start_date}/{end_date}", response_model=ApiResponse)
async def get_attendance_by_date_range(
    start_date: str,  # Format: YYYY-MM-DD
    end_date: str,    # Format: YYYY-MM-DD
    user_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get attendance records within date range"""
    try:
        attendance_service = AttendanceService(db)
        
        # Parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if user_id:
            attendance_records = await attendance_service.get_by_user_range(user_id, start_date_obj, end_date_obj)
        else:
            # Get all attendance records in range
            filters = {
                "date": {"$gte": start_date_obj, "$lte": end_date_obj}
            }
            attendance_records = await attendance_service.get_all(filters=filters)
        
        return ApiResponse(
            success=True,
            message="Attendance records retrieved successfully",
            data=attendance_records
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))