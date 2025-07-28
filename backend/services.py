from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from models import *


class BaseService:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
    
    async def create(self, data: dict) -> dict:
        """Create a new document"""
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()
        
        result = await self.collection.insert_one(data)
        return await self.get_by_id(data['id'])
    
    async def get_by_id(self, id: str) -> Optional[dict]:
        """Get document by ID"""
        doc = await self.collection.find_one({"id": id})
        if doc:
            doc.pop('_id', None)  # Remove MongoDB's internal ID
        return doc
    
    async def get_all(self, skip: int = 0, limit: int = 100, filters: dict = None) -> List[dict]:
        """Get all documents with pagination and filters"""
        query = filters if filters else {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def update(self, id: str, data: dict) -> Optional[dict]:
        """Update document by ID"""
        data['updated_at'] = datetime.utcnow()
        result = await self.collection.update_one(
            {"id": id}, 
            {"$set": data}
        )
        if result.modified_count:
            return await self.get_by_id(id)
        return None
    
    async def delete(self, id: str) -> bool:
        """Delete document by ID"""
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def count(self, filters: dict = None) -> int:
        """Count documents with filters"""
        query = filters if filters else {}
        return await self.collection.count_documents(query)


class UserService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users")
    
    async def get_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        doc = await self.collection.find_one({"email": email})
        if doc:
            doc.pop('_id', None)
        return doc
    
    async def get_by_role(self, role: str) -> List[dict]:
        """Get users by role"""
        return await self.get_all(filters={"role": role})
    
    async def get_active_users(self) -> List[dict]:
        """Get active users"""
        return await self.get_all(filters={"is_active": True})
    
    async def update_status(self, user_id: str, status: str) -> Optional[dict]:
        """Update user status"""
        return await self.update(user_id, {"status": status})


class ScheduleService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "schedules")
    
    async def get_by_user(self, user_id: str) -> List[dict]:
        """Get schedules by user"""
        return await self.get_all(filters={"user_id": user_id})
    
    async def get_active_schedules(self) -> List[dict]:
        """Get active schedules"""
        return await self.get_all(filters={"is_active": True})


class AttendanceService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance")
    
    async def get_by_user_and_date(self, user_id: str, date: datetime) -> Optional[dict]:
        """Get attendance by user and date"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        doc = await self.collection.find_one({
            "user_id": user_id,
            "date": {"$gte": start_date, "$lte": end_date}
        })
        if doc:
            doc.pop('_id', None)
        return doc
    
    async def get_by_user_range(self, user_id: str, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get attendance by user within date range"""
        return await self.get_all(filters={
            "user_id": user_id,
            "date": {"$gte": start_date, "$lte": end_date}
        })
    
    async def check_in(self, user_id: str, timestamp: datetime = None) -> dict:
        """Check in user"""
        if not timestamp:
            timestamp = datetime.utcnow()
        
        date = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        existing = await self.get_by_user_and_date(user_id, date)
        
        if existing:
            return await self.update(existing['id'], {"check_in": timestamp})
        else:
            return await self.create({
                "user_id": user_id,
                "date": date,
                "check_in": timestamp,
                "status": "present"
            })
    
    async def check_out(self, user_id: str, timestamp: datetime = None) -> Optional[dict]:
        """Check out user"""
        if not timestamp:
            timestamp = datetime.utcnow()
        
        date = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        existing = await self.get_by_user_and_date(user_id, date)
        
        if existing:
            # Calculate hours worked
            hours_worked = None
            if existing.get('check_in'):
                hours_worked = (timestamp - existing['check_in']).total_seconds() / 3600
            
            return await self.update(existing['id'], {
                "check_out": timestamp,
                "hours_worked": hours_worked
            })
        return None


class GoalService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "goals")
    
    async def get_by_user(self, user_id: str) -> List[dict]:
        """Get goals by user"""
        return await self.get_all(filters={"user_id": user_id})
    
    async def get_by_team(self, team_id: str) -> List[dict]:
        """Get goals by team"""
        return await self.get_all(filters={"team_id": team_id})
    
    async def get_active_goals(self) -> List[dict]:
        """Get active goals"""
        return await self.get_all(filters={"is_active": True})
    
    async def update_progress(self, goal_id: str, current_value: float) -> Optional[dict]:
        """Update goal progress"""
        return await self.update(goal_id, {"current_value": current_value})


class CustomerService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "customers")
    
    async def get_by_email(self, email: str) -> Optional[dict]:
        """Get customer by email"""
        doc = await self.collection.find_one({"email": email})
        if doc:
            doc.pop('_id', None)
        return doc
    
    async def get_by_phone(self, phone: str) -> Optional[dict]:
        """Get customer by phone"""
        doc = await self.collection.find_one({"phone": phone})
        if doc:
            doc.pop('_id', None)
        return doc
    
    async def search(self, query: str) -> List[dict]:
        """Search customers by name, email, or company"""
        return await self.get_all(filters={
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
                {"company": {"$regex": query, "$options": "i"}}
            ]
        })


class TicketService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "tickets")
    
    async def get_by_customer(self, customer_id: str) -> List[dict]:
        """Get tickets by customer"""
        return await self.get_all(filters={"customer_id": customer_id})
    
    async def get_by_assignee(self, user_id: str) -> List[dict]:
        """Get tickets by assignee"""
        return await self.get_all(filters={"assigned_to": user_id})
    
    async def get_by_status(self, status: str) -> List[dict]:
        """Get tickets by status"""
        return await self.get_all(filters={"status": status})
    
    async def get_by_priority(self, priority: str) -> List[dict]:
        """Get tickets by priority"""
        return await self.get_all(filters={"priority": priority})
    
    async def assign_ticket(self, ticket_id: str, user_id: str) -> Optional[dict]:
        """Assign ticket to user"""
        return await self.update(ticket_id, {"assigned_to": user_id})
    
    async def resolve_ticket(self, ticket_id: str, resolution: str) -> Optional[dict]:
        """Resolve ticket"""
        return await self.update(ticket_id, {
            "status": "resolved",
            "resolution": resolution,
            "resolved_at": datetime.utcnow()
        })
    
    async def rate_ticket(self, ticket_id: str, rating: int, comment: str = None) -> Optional[dict]:
        """Rate ticket satisfaction"""
        update_data = {"satisfaction_rating": rating}
        if comment:
            update_data["satisfaction_comment"] = comment
        return await self.update(ticket_id, update_data)


class MonitoringService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "monitoring_metrics")
    
    async def get_by_category(self, category: str) -> List[dict]:
        """Get metrics by category"""
        return await self.get_all(filters={"category": category})
    
    async def get_by_user(self, user_id: str) -> List[dict]:
        """Get metrics by user"""
        return await self.get_all(filters={"user_id": user_id})
    
    async def get_by_timerange(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get metrics within time range"""
        return await self.get_all(filters={
            "timestamp": {"$gte": start_date, "$lte": end_date}
        })
    
    async def get_latest_metrics(self, limit: int = 100) -> List[dict]:
        """Get latest metrics"""
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs


class ReportService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "reports")
    
    async def get_by_type(self, report_type: str) -> List[dict]:
        """Get reports by type"""
        return await self.get_all(filters={"type": report_type})
    
    async def get_by_user(self, user_id: str) -> List[dict]:
        """Get reports by user"""
        return await self.get_all(filters={"generated_by": user_id})
    
    async def get_public_reports(self) -> List[dict]:
        """Get public reports"""
        return await self.get_all(filters={"is_public": True})


class SettingsService(BaseService):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "settings")
    
    async def get_by_key(self, key: str) -> Optional[dict]:
        """Get setting by key"""
        doc = await self.collection.find_one({"key": key})
        if doc:
            doc.pop('_id', None)
        return doc
    
    async def get_by_category(self, category: str) -> List[dict]:
        """Get settings by category"""
        return await self.get_all(filters={"category": category})
    
    async def get_public_settings(self) -> List[dict]:
        """Get public settings"""
        return await self.get_all(filters={"is_public": True})
    
    async def update_setting(self, key: str, value: Any, user_id: str) -> Optional[dict]:
        """Update setting value"""
        existing = await self.get_by_key(key)
        if existing:
            return await self.update(existing['id'], {
                "value": value,
                "updated_by": user_id
            })
        return None