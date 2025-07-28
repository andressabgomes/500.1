from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ..models import User, UserCreate, UserUpdate, ApiResponse, PaginatedResponse
from ..services import UserService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

router = APIRouter(prefix="/users", tags=["users"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    return db

@router.post("/", response_model=ApiResponse)
async def create_user(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new user"""
    try:
        user_service = UserService(db)
        
        # Check if email already exists
        existing_user = await user_service.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user_dict = user_data.dict()
        user = await user_service.create(user_dict)
        
        return ApiResponse(
            success=True,
            message="User created successfully",
            data=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get user by ID"""
    try:
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return ApiResponse(
            success=True,
            message="User retrieved successfully",
            data=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all users with pagination and filters"""
    try:
        user_service = UserService(db)
        
        # Build filters
        filters = {}
        if role:
            filters["role"] = role
        if is_active is not None:
            filters["is_active"] = is_active
        
        users = await user_service.get_all(skip=skip, limit=limit, filters=filters)
        total = await user_service.count(filters)
        
        return PaginatedResponse(
            success=True,
            message="Users retrieved successfully",
            data=users,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(
    user_id: str, 
    user_data: UserUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update user"""
    try:
        user_service = UserService(db)
        
        # Check if user exists
        existing_user = await user_service.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if email already exists for another user
        if user_data.email:
            email_user = await user_service.get_by_email(user_data.email)
            if email_user and email_user['id'] != user_id:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Update user
        update_dict = user_data.dict(exclude_unset=True)
        user = await user_service.update(user_id, update_dict)
        
        return ApiResponse(
            success=True,
            message="User updated successfully",
            data=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete user"""
    try:
        user_service = UserService(db)
        
        # Check if user exists
        existing_user = await user_service.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user
        deleted = await user_service.delete(user_id)
        
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete user")
        
        return ApiResponse(
            success=True,
            message="User deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/{email}", response_model=ApiResponse)
async def get_user_by_email(email: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get user by email"""
    try:
        user_service = UserService(db)
        user = await user_service.get_by_email(email)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return ApiResponse(
            success=True,
            message="User retrieved successfully",
            data=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{user_id}/status", response_model=ApiResponse)
async def update_user_status(
    user_id: str, 
    status: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update user status"""
    try:
        user_service = UserService(db)
        
        # Check if user exists
        existing_user = await user_service.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update status
        user = await user_service.update_status(user_id, status)
        
        return ApiResponse(
            success=True,
            message="User status updated successfully",
            data=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/role/{role}", response_model=ApiResponse)
async def get_users_by_role(role: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get users by role"""
    try:
        user_service = UserService(db)
        users = await user_service.get_by_role(role)
        
        return ApiResponse(
            success=True,
            message="Users retrieved successfully",
            data=users
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/all", response_model=ApiResponse)
async def get_active_users(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all active users"""
    try:
        user_service = UserService(db)
        users = await user_service.get_active_users()
        
        return ApiResponse(
            success=True,
            message="Active users retrieved successfully",
            data=users
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))