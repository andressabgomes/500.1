from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from models import Goal, GoalCreate, GoalUpdate, ApiResponse, PaginatedResponse
from services import GoalService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

router = APIRouter(prefix="/goals", tags=["goals"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    return db

@router.post("/", response_model=ApiResponse)
async def create_goal(goal_data: GoalCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new goal"""
    try:
        goal_service = GoalService(db)
        
        goal_dict = goal_data.dict()
        goal = await goal_service.create(goal_dict)
        
        return ApiResponse(
            success=True,
            message="Goal created successfully",
            data=goal
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{goal_id}", response_model=ApiResponse)
async def get_goal(goal_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get goal by ID"""
    try:
        goal_service = GoalService(db)
        goal = await goal_service.get_by_id(goal_id)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return ApiResponse(
            success=True,
            message="Goal retrieved successfully",
            data=goal
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedResponse)
async def get_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    unit: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all goals with pagination and filters"""
    try:
        goal_service = GoalService(db)
        
        # Build filters
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if team_id:
            filters["team_id"] = team_id
        if is_active is not None:
            filters["is_active"] = is_active
        if unit:
            filters["unit"] = unit
        
        goals = await goal_service.get_all(skip=skip, limit=limit, filters=filters)
        total = await goal_service.count(filters)
        
        return PaginatedResponse(
            success=True,
            message="Goals retrieved successfully",
            data=goals,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{goal_id}", response_model=ApiResponse)
async def update_goal(
    goal_id: str, 
    goal_data: GoalUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update goal"""
    try:
        goal_service = GoalService(db)
        
        # Check if goal exists
        existing_goal = await goal_service.get_by_id(goal_id)
        if not existing_goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Update goal
        update_dict = goal_data.dict(exclude_unset=True)
        goal = await goal_service.update(goal_id, update_dict)
        
        return ApiResponse(
            success=True,
            message="Goal updated successfully",
            data=goal
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{goal_id}", response_model=ApiResponse)
async def delete_goal(goal_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete goal"""
    try:
        goal_service = GoalService(db)
        
        # Check if goal exists
        existing_goal = await goal_service.get_by_id(goal_id)
        if not existing_goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Delete goal
        deleted = await goal_service.delete(goal_id)
        
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete goal")
        
        return ApiResponse(
            success=True,
            message="Goal deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_goals_by_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get goals by user"""
    try:
        goal_service = GoalService(db)
        goals = await goal_service.get_by_user(user_id)
        
        return ApiResponse(
            success=True,
            message="Goals retrieved successfully",
            data=goals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/{team_id}", response_model=ApiResponse)
async def get_goals_by_team(team_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get goals by team"""
    try:
        goal_service = GoalService(db)
        goals = await goal_service.get_by_team(team_id)
        
        return ApiResponse(
            success=True,
            message="Goals retrieved successfully",
            data=goals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/all", response_model=ApiResponse)
async def get_active_goals(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all active goals"""
    try:
        goal_service = GoalService(db)
        goals = await goal_service.get_active_goals()
        
        return ApiResponse(
            success=True,
            message="Active goals retrieved successfully",
            data=goals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{goal_id}/progress", response_model=ApiResponse)
async def update_goal_progress(
    goal_id: str, 
    current_value: float, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update goal progress"""
    try:
        goal_service = GoalService(db)
        
        # Check if goal exists
        existing_goal = await goal_service.get_by_id(goal_id)
        if not existing_goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Update progress
        goal = await goal_service.update_progress(goal_id, current_value)
        
        return ApiResponse(
            success=True,
            message="Goal progress updated successfully",
            data=goal
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))