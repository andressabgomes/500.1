from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from models import MonitoringMetric, MonitoringMetricCreate, ApiResponse, PaginatedResponse
from services import MonitoringService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from datetime import datetime

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ.get('MONGO_URL', os.environ.get('DATABASE_URL', 'mongodb://localhost:27017'))
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', os.environ.get('DATABASE_NAME', 'starprint_crm'))
    db = client[db_name]
    return db

@router.post("/", response_model=ApiResponse)
async def create_metric(metric_data: MonitoringMetricCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new monitoring metric"""
    try:
        monitoring_service = MonitoringService(db)
        
        metric_dict = metric_data.dict()
        metric = await monitoring_service.create(metric_dict)
        
        return ApiResponse(
            success=True,
            message="Monitoring metric created successfully",
            data=metric
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{metric_id}", response_model=ApiResponse)
async def get_metric(metric_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get metric by ID"""
    try:
        monitoring_service = MonitoringService(db)
        metric = await monitoring_service.get_by_id(metric_id)
        
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        return ApiResponse(
            success=True,
            message="Metric retrieved successfully",
            data=metric
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedResponse)
async def get_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all metrics with pagination and filters"""
    try:
        monitoring_service = MonitoringService(db)
        
        # Build filters
        filters = {}
        if category:
            filters["category"] = category
        if user_id:
            filters["user_id"] = user_id
        
        metrics = await monitoring_service.get_all(skip=skip, limit=limit, filters=filters)
        total = await monitoring_service.count(filters)
        
        return PaginatedResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=metrics,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{metric_id}", response_model=ApiResponse)
async def delete_metric(metric_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete metric"""
    try:
        monitoring_service = MonitoringService(db)
        
        # Check if metric exists
        existing_metric = await monitoring_service.get_by_id(metric_id)
        if not existing_metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        # Delete metric
        deleted = await monitoring_service.delete(metric_id)
        
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete metric")
        
        return ApiResponse(
            success=True,
            message="Metric deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category/{category}", response_model=ApiResponse)
async def get_metrics_by_category(category: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get metrics by category"""
    try:
        monitoring_service = MonitoringService(db)
        metrics = await monitoring_service.get_by_category(category)
        
        return ApiResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_metrics_by_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get metrics by user"""
    try:
        monitoring_service = MonitoringService(db)
        metrics = await monitoring_service.get_by_user(user_id)
        
        return ApiResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest/{limit}", response_model=ApiResponse)
async def get_latest_metrics(limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get latest metrics"""
    try:
        monitoring_service = MonitoringService(db)
        metrics = await monitoring_service.get_latest_metrics(limit)
        
        return ApiResponse(
            success=True,
            message="Latest metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timerange/{start_date}/{end_date}", response_model=ApiResponse)
async def get_metrics_by_timerange(
    start_date: str,  # Format: YYYY-MM-DD
    end_date: str,    # Format: YYYY-MM-DD
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get metrics within time range"""
    try:
        monitoring_service = MonitoringService(db)
        
        # Parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        metrics = await monitoring_service.get_by_timerange(start_date_obj, end_date_obj)
        
        return ApiResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=metrics
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/data", response_model=ApiResponse)
async def get_dashboard_data(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get dashboard data with aggregated metrics"""
    try:
        monitoring_service = MonitoringService(db)
        
        # Get latest metrics
        latest_metrics = await monitoring_service.get_latest_metrics(50)
        
        # Get metrics by category
        performance_metrics = await monitoring_service.get_by_category("performance")
        quality_metrics = await monitoring_service.get_by_category("quality")
        volume_metrics = await monitoring_service.get_by_category("volume")
        
        dashboard_data = {
            "latest_metrics": latest_metrics,
            "performance_metrics": performance_metrics[:10],  # Last 10
            "quality_metrics": quality_metrics[:10],
            "volume_metrics": volume_metrics[:10],
            "total_metrics": len(latest_metrics)
        }
        
        return ApiResponse(
            success=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))