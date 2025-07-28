from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, date
from ..models import MonitoringMetric, MonitoringMetricCreate, ApiResponse, PaginatedResponse
from ..services import MonitoringService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    return db

@router.post("/metrics", response_model=ApiResponse)
async def create_metric(metric_data: MonitoringMetricCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new monitoring metric"""
    try:
        monitoring_service = MonitoringService(db)
        
        metric_dict = metric_data.dict()
        metric = await monitoring_service.create(metric_dict)
        
        return ApiResponse(
            success=True,
            message="Metric created successfully",
            data=metric
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{metric_id}", response_model=ApiResponse)
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

@router.get("/metrics", response_model=PaginatedResponse)
async def get_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
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
        if name:
            filters["name"] = name
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.combine(date_from, datetime.min.time())
            if date_to:
                date_filter["$lte"] = datetime.combine(date_to, datetime.max.time())
            filters["timestamp"] = date_filter
        
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

@router.delete("/metrics/{metric_id}", response_model=ApiResponse)
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

@router.get("/metrics/category/{category}", response_model=ApiResponse)
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

@router.get("/metrics/user/{user_id}", response_model=ApiResponse)
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

@router.get("/metrics/timerange", response_model=ApiResponse)
async def get_metrics_by_timerange(
    start_date: datetime,
    end_date: datetime,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get metrics within time range"""
    try:
        monitoring_service = MonitoringService(db)
        metrics = await monitoring_service.get_by_timerange(start_date, end_date)
        
        return ApiResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/latest", response_model=ApiResponse)
async def get_latest_metrics(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
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

@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard_data(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get dashboard monitoring data"""
    try:
        monitoring_service = MonitoringService(db)
        
        # Get various metrics for dashboard
        performance_metrics = await monitoring_service.get_by_category("performance")
        quality_metrics = await monitoring_service.get_by_category("quality")
        volume_metrics = await monitoring_service.get_by_category("volume")
        
        dashboard_data = {
            "performance": performance_metrics[:10],  # Latest 10
            "quality": quality_metrics[:10],
            "volume": volume_metrics[:10],
            "last_updated": datetime.utcnow()
        }
        
        return ApiResponse(
            success=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))