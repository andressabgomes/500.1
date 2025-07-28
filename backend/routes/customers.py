from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ..models import Customer, CustomerCreate, CustomerUpdate, ApiResponse, PaginatedResponse
from ..services import CustomerService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

router = APIRouter(prefix="/customers", tags=["customers"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    return db

@router.post("/", response_model=ApiResponse)
async def create_customer(customer_data: CustomerCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new customer"""
    try:
        customer_service = CustomerService(db)
        
        # Check if email already exists
        if customer_data.email:
            existing_customer = await customer_service.get_by_email(customer_data.email)
            if existing_customer:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        customer_dict = customer_data.dict()
        customer = await customer_service.create(customer_dict)
        
        return ApiResponse(
            success=True,
            message="Customer created successfully",
            data=customer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}", response_model=ApiResponse)
async def get_customer(customer_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get customer by ID"""
    try:
        customer_service = CustomerService(db)
        customer = await customer_service.get_by_id(customer_id)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return ApiResponse(
            success=True,
            message="Customer retrieved successfully",
            data=customer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedResponse)
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all customers with pagination and filters"""
    try:
        customer_service = CustomerService(db)
        
        # If search query provided, use search
        if search:
            customers = await customer_service.search(search)
            total = len(customers)
            # Apply pagination to search results
            customers = customers[skip:skip + limit]
        else:
            # Build filters
            filters = {}
            if is_active is not None:
                filters["is_active"] = is_active
            
            customers = await customer_service.get_all(skip=skip, limit=limit, filters=filters)
            total = await customer_service.count(filters)
        
        return PaginatedResponse(
            success=True,
            message="Customers retrieved successfully",
            data=customers,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{customer_id}", response_model=ApiResponse)
async def update_customer(
    customer_id: str, 
    customer_data: CustomerUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update customer"""
    try:
        customer_service = CustomerService(db)
        
        # Check if customer exists
        existing_customer = await customer_service.get_by_id(customer_id)
        if not existing_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Check if email already exists for another customer
        if customer_data.email:
            email_customer = await customer_service.get_by_email(customer_data.email)
            if email_customer and email_customer['id'] != customer_id:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Update customer
        update_dict = customer_data.dict(exclude_unset=True)
        customer = await customer_service.update(customer_id, update_dict)
        
        return ApiResponse(
            success=True,
            message="Customer updated successfully",
            data=customer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{customer_id}", response_model=ApiResponse)
async def delete_customer(customer_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete customer"""
    try:
        customer_service = CustomerService(db)
        
        # Check if customer exists
        existing_customer = await customer_service.get_by_id(customer_id)
        if not existing_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Delete customer
        deleted = await customer_service.delete(customer_id)
        
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete customer")
        
        return ApiResponse(
            success=True,
            message="Customer deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/{email}", response_model=ApiResponse)
async def get_customer_by_email(email: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get customer by email"""
    try:
        customer_service = CustomerService(db)
        customer = await customer_service.get_by_email(email)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return ApiResponse(
            success=True,
            message="Customer retrieved successfully",
            data=customer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phone/{phone}", response_model=ApiResponse)
async def get_customer_by_phone(phone: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get customer by phone"""
    try:
        customer_service = CustomerService(db)
        customer = await customer_service.get_by_phone(phone)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return ApiResponse(
            success=True,
            message="Customer retrieved successfully",
            data=customer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{query}", response_model=ApiResponse)
async def search_customers(query: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Search customers by name, email, or company"""
    try:
        customer_service = CustomerService(db)
        customers = await customer_service.search(query)
        
        return ApiResponse(
            success=True,
            message="Customers retrieved successfully",
            data=customers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))