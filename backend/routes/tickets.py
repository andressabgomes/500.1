from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from models import Ticket, TicketCreate, TicketUpdate, ApiResponse, PaginatedResponse
from services import TicketService, CustomerService
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Dependency to get database
async def get_database():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    return db

@router.post("/", response_model=ApiResponse)
async def create_ticket(ticket_data: TicketCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create a new ticket"""
    try:
        ticket_service = TicketService(db)
        customer_service = CustomerService(db)
        
        # Check if customer exists
        customer = await customer_service.get_by_id(ticket_data.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        ticket_dict = ticket_data.dict()
        ticket = await ticket_service.create(ticket_dict)
        
        return ApiResponse(
            success=True,
            message="Ticket created successfully",
            data=ticket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}", response_model=ApiResponse)
async def get_ticket(ticket_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get ticket by ID"""
    try:
        ticket_service = TicketService(db)
        ticket = await ticket_service.get_by_id(ticket_id)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return ApiResponse(
            success=True,
            message="Ticket retrieved successfully",
            data=ticket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedResponse)
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all tickets with pagination and filters"""
    try:
        ticket_service = TicketService(db)
        
        # Build filters
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
        if assigned_to:
            filters["assigned_to"] = assigned_to
        if customer_id:
            filters["customer_id"] = customer_id
        if channel:
            filters["channel"] = channel
        
        tickets = await ticket_service.get_all(skip=skip, limit=limit, filters=filters)
        total = await ticket_service.count(filters)
        
        return PaginatedResponse(
            success=True,
            message="Tickets retrieved successfully",
            data=tickets,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ticket_id}", response_model=ApiResponse)
async def update_ticket(
    ticket_id: str, 
    ticket_data: TicketUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update ticket"""
    try:
        ticket_service = TicketService(db)
        
        # Check if ticket exists
        existing_ticket = await ticket_service.get_by_id(ticket_id)
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update ticket
        update_dict = ticket_data.dict(exclude_unset=True)
        ticket = await ticket_service.update(ticket_id, update_dict)
        
        return ApiResponse(
            success=True,
            message="Ticket updated successfully",
            data=ticket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{ticket_id}", response_model=ApiResponse)
async def delete_ticket(ticket_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Delete ticket"""
    try:
        ticket_service = TicketService(db)
        
        # Check if ticket exists
        existing_ticket = await ticket_service.get_by_id(ticket_id)
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Delete ticket
        deleted = await ticket_service.delete(ticket_id)
        
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete ticket")
        
        return ApiResponse(
            success=True,
            message="Ticket deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customer/{customer_id}", response_model=ApiResponse)
async def get_tickets_by_customer(customer_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get tickets by customer"""
    try:
        ticket_service = TicketService(db)
        tickets = await ticket_service.get_by_customer(customer_id)
        
        return ApiResponse(
            success=True,
            message="Tickets retrieved successfully",
            data=tickets
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignee/{user_id}", response_model=ApiResponse)
async def get_tickets_by_assignee(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get tickets by assignee"""
    try:
        ticket_service = TicketService(db)
        tickets = await ticket_service.get_by_assignee(user_id)
        
        return ApiResponse(
            success=True,
            message="Tickets retrieved successfully",
            data=tickets
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{status}", response_model=ApiResponse)
async def get_tickets_by_status(status: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get tickets by status"""
    try:
        ticket_service = TicketService(db)
        tickets = await ticket_service.get_by_status(status)
        
        return ApiResponse(
            success=True,
            message="Tickets retrieved successfully",
            data=tickets
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{ticket_id}/assign", response_model=ApiResponse)
async def assign_ticket(
    ticket_id: str, 
    user_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Assign ticket to user"""
    try:
        ticket_service = TicketService(db)
        
        # Check if ticket exists
        existing_ticket = await ticket_service.get_by_id(ticket_id)
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Assign ticket
        ticket = await ticket_service.assign_ticket(ticket_id, user_id)
        
        return ApiResponse(
            success=True,
            message="Ticket assigned successfully",
            data=ticket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{ticket_id}/resolve", response_model=ApiResponse)
async def resolve_ticket(
    ticket_id: str, 
    resolution: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Resolve ticket"""
    try:
        ticket_service = TicketService(db)
        
        # Check if ticket exists
        existing_ticket = await ticket_service.get_by_id(ticket_id)
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Resolve ticket
        ticket = await ticket_service.resolve_ticket(ticket_id, resolution)
        
        return ApiResponse(
            success=True,
            message="Ticket resolved successfully",
            data=ticket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{ticket_id}/rate", response_model=ApiResponse)
async def rate_ticket(
    ticket_id: str, 
    rating: int, 
    comment: Optional[str] = None, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Rate ticket satisfaction"""
    try:
        ticket_service = TicketService(db)
        
        # Validate rating
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Check if ticket exists
        existing_ticket = await ticket_service.get_by_id(ticket_id)
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Rate ticket
        ticket = await ticket_service.rate_ticket(ticket_id, rating, comment)
        
        return ApiResponse(
            success=True,
            message="Ticket rated successfully",
            data=ticket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))