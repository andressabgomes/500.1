#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for StarPrint CRM
Tests all CRUD operations, filtering, search, and edge cases
"""

import requests
import json
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
import os

# Get backend URL from environment
BACKEND_URL = "https://5aa68d36-1e1e-4d3d-94d8-0011ccae3a58.preview.emergentagent.com/api"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.created_entities = {
            'users': [],
            'customers': [],
            'tickets': [],
            'goals': [],
            'attendance': [],
            'monitoring': []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request and return response"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            
            return {
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'success': 200 <= response.status_code < 300
            }
        except Exception as e:
            return {
                'status_code': 0,
                'data': {'error': str(e)},
                'success': False
            }

    def test_health_check(self):
        """Test API health check"""
        print("\n=== Testing Health Check ===")
        
        response = self.make_request('GET', '/health')
        self.log_test(
            "Health Check",
            response['success'] and response['data'].get('status') == 'healthy',
            f"Status: {response['status_code']}, Data: {response['data']}"
        )

    def test_user_management(self):
        """Test User Management API"""
        print("\n=== Testing User Management API ===")
        
        # Test data with unique identifiers
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": f"Test User {unique_id}",
            "email": f"test.user.{unique_id}@starprint.com",
            "role": "agent",
            "phone": f"+55 11 9999-{unique_id[:4]}",
            "department": "Customer Support",
            "skills": ["Portuguese", "Customer Service", "Technical Support"]
        }
        
        # Test 1: Create User
        response = self.make_request('POST', '/users/', user_data)
        if response['success']:
            user_id = response['data']['data']['id']
            self.created_entities['users'].append(user_id)
            self.log_test("Create User", True, f"Created user with ID: {user_id}")
        else:
            self.log_test("Create User", False, f"Status: {response['status_code']}, Error: {response['data']}")
            return
        
        # Test 2: Get User by ID
        response = self.make_request('GET', f'/users/{user_id}')
        self.log_test(
            "Get User by ID",
            response['success'] and response['data']['data']['email'] == user_data['email'],
            f"Retrieved user: {response['data']['data']['name'] if response['success'] else response['data']}"
        )
        
        # Test 3: Get All Users
        response = self.make_request('GET', '/users/')
        self.log_test(
            "Get All Users",
            response['success'] and len(response['data']['data']) > 0,
            f"Retrieved {len(response['data']['data']) if response['success'] else 0} users"
        )
        
        # Test 4: Get User by Email
        response = self.make_request('GET', f'/users/email/{user_data["email"]}')
        self.log_test(
            "Get User by Email",
            response['success'] and response['data']['data']['id'] == user_id,
            f"Found user by email: {response['success']}"
        )
        
        # Test 5: Update User
        update_data = {
            "name": "Maria Silva Santos",
            "status": "busy",
            "department": "Technical Support"
        }
        response = self.make_request('PUT', f'/users/{user_id}', update_data)
        self.log_test(
            "Update User",
            response['success'] and response['data']['data']['name'] == update_data['name'],
            f"Updated user name: {response['data']['data']['name'] if response['success'] else response['data']}"
        )
        
        # Test 6: Update User Status
        response = self.make_request('PATCH', f'/users/{user_id}/status', params={'status': 'available'})
        self.log_test(
            "Update User Status",
            response['success'],
            f"Status update: {response['success']}"
        )
        
        # Test 7: Get Users by Role
        response = self.make_request('GET', f'/users/role/agent')
        self.log_test(
            "Get Users by Role",
            response['success'] and len(response['data']['data']) > 0,
            f"Found {len(response['data']['data']) if response['success'] else 0} agents"
        )
        
        # Test 8: Get Active Users
        response = self.make_request('GET', '/users/active/all')
        self.log_test(
            "Get Active Users",
            response['success'],
            f"Retrieved active users: {response['success']}"
        )
        
        # Test 9: Email Uniqueness Validation
        duplicate_user = user_data.copy()
        duplicate_user['name'] = "Another User"
        response = self.make_request('POST', '/users/', duplicate_user)
        self.log_test(
            "Email Uniqueness Validation",
            not response['success'] and response['status_code'] == 400,
            f"Correctly rejected duplicate email: {response['status_code'] == 400}"
        )

    def test_customer_management(self):
        """Test Customer Management API"""
        print("\n=== Testing Customer Management API ===")
        
        # Test data with unique identifiers
        unique_id = str(uuid.uuid4())[:8]
        customer_data = {
            "name": f"Test Company {unique_id}",
            "email": f"contact.{unique_id}@testcompany.com.br",
            "phone": f"+55 11 3333-{unique_id[:4]}",
            "company": f"Test Industry {unique_id}",
            "address": f"Test Street, {unique_id[:3]} - São Paulo, SP",
            "notes": "Test customer for API testing",
            "tags": ["test", "api", "automation"]
        }
        
        # Test 1: Create Customer
        response = self.make_request('POST', '/customers/', customer_data)
        if response['success']:
            customer_id = response['data']['data']['id']
            self.created_entities['customers'].append(customer_id)
            self.log_test("Create Customer", True, f"Created customer with ID: {customer_id}")
        else:
            self.log_test("Create Customer", False, f"Status: {response['status_code']}, Error: {response['data']}")
            return
        
        # Test 2: Get Customer by ID
        response = self.make_request('GET', f'/customers/{customer_id}')
        self.log_test(
            "Get Customer by ID",
            response['success'] and response['data']['data']['company'] == customer_data['company'],
            f"Retrieved customer: {response['data']['data']['name'] if response['success'] else response['data']}"
        )
        
        # Test 3: Get All Customers
        response = self.make_request('GET', '/customers/')
        self.log_test(
            "Get All Customers",
            response['success'] and len(response['data']['data']) > 0,
            f"Retrieved {len(response['data']['data']) if response['success'] else 0} customers"
        )
        
        # Test 4: Get Customer by Email
        response = self.make_request('GET', f'/customers/email/{customer_data["email"]}')
        self.log_test(
            "Get Customer by Email",
            response['success'] and response['data']['data']['id'] == customer_id,
            f"Found customer by email: {response['success']}"
        )
        
        # Test 5: Get Customer by Phone
        response = self.make_request('GET', f'/customers/phone/{customer_data["phone"]}')
        self.log_test(
            "Get Customer by Phone",
            response['success'] and response['data']['data']['id'] == customer_id,
            f"Found customer by phone: {response['success']}"
        )
        
        # Test 6: Search Customers
        response = self.make_request('GET', '/customers/search/ABC')
        self.log_test(
            "Search Customers",
            response['success'] and len(response['data']['data']) > 0,
            f"Search found {len(response['data']['data']) if response['success'] else 0} customers"
        )
        
        # Test 7: Update Customer
        update_data = {
            "name": "Empresa ABC Industrial Ltda",
            "notes": "Cliente premium com contrato renovado",
            "tags": ["premium", "industrial", "sao-paulo", "renewed"]
        }
        response = self.make_request('PUT', f'/customers/{customer_id}', update_data)
        self.log_test(
            "Update Customer",
            response['success'] and response['data']['data']['name'] == update_data['name'],
            f"Updated customer: {response['success']}"
        )
        
        # Test 8: Search with Pagination
        response = self.make_request('GET', '/customers/', params={'search': 'ABC', 'limit': 5})
        self.log_test(
            "Search with Pagination",
            response['success'],
            f"Paginated search: {response['success']}"
        )

    def test_ticket_management(self):
        """Test Support Ticket API"""
        print("\n=== Testing Support Ticket API ===")
        
        # Need customer and user for ticket creation
        if not self.created_entities['customers'] or not self.created_entities['users']:
            self.log_test("Ticket Management Setup", False, "Missing customer or user for ticket tests")
            return
        
        customer_id = self.created_entities['customers'][0]
        user_id = self.created_entities['users'][0]
        
        # Test data
        ticket_data = {
            "title": "Problema com impressão de etiquetas",
            "description": "Cliente relatando que as etiquetas estão saindo com qualidade ruim na impressora térmica modelo XYZ-123",
            "priority": "high",
            "channel": "phone",
            "customer_id": customer_id,
            "assigned_to": user_id,
            "tags": ["impressao", "qualidade", "termica"]
        }
        
        # Test 1: Create Ticket
        response = self.make_request('POST', '/tickets/', ticket_data)
        if response['success']:
            ticket_id = response['data']['data']['id']
            ticket_number = response['data']['data'].get('ticket_number', 'N/A')
            self.created_entities['tickets'].append(ticket_id)
            self.log_test("Create Ticket", True, f"Created ticket {ticket_number} with ID: {ticket_id}")
        else:
            self.log_test("Create Ticket", False, f"Status: {response['status_code']}, Error: {response['data']}")
            return
        
        # Test 2: Get Ticket by ID
        response = self.make_request('GET', f'/tickets/{ticket_id}')
        self.log_test(
            "Get Ticket by ID",
            response['success'] and response['data']['data']['title'] == ticket_data['title'],
            f"Retrieved ticket: {response['data']['data'].get('ticket_number', 'N/A') if response['success'] else response['data']}"
        )
        
        # Test 3: Get All Tickets
        response = self.make_request('GET', '/tickets/')
        self.log_test(
            "Get All Tickets",
            response['success'] and len(response['data']['data']) > 0,
            f"Retrieved {len(response['data']['data']) if response['success'] else 0} tickets"
        )
        
        # Test 4: Get Tickets by Customer
        response = self.make_request('GET', f'/tickets/customer/{customer_id}')
        self.log_test(
            "Get Tickets by Customer",
            response['success'] and len(response['data']['data']) > 0,
            f"Found {len(response['data']['data']) if response['success'] else 0} tickets for customer"
        )
        
        # Test 5: Get Tickets by Assignee
        response = self.make_request('GET', f'/tickets/assignee/{user_id}')
        self.log_test(
            "Get Tickets by Assignee",
            response['success'] and len(response['data']['data']) > 0,
            f"Found {len(response['data']['data']) if response['success'] else 0} tickets for assignee"
        )
        
        # Test 6: Get Tickets by Status
        response = self.make_request('GET', '/tickets/status/open')
        self.log_test(
            "Get Tickets by Status",
            response['success'],
            f"Found tickets by status: {response['success']}"
        )
        
        # Test 7: Update Ticket
        update_data = {
            "status": "in_progress",
            "priority": "urgent",
            "description": "Cliente relatando que as etiquetas estão saindo com qualidade ruim. Investigação iniciada."
        }
        response = self.make_request('PUT', f'/tickets/{ticket_id}', update_data)
        self.log_test(
            "Update Ticket",
            response['success'] and response['data']['data']['status'] == update_data['status'],
            f"Updated ticket status: {response['success']}"
        )
        
        # Test 8: Assign Ticket
        response = self.make_request('PATCH', f'/tickets/{ticket_id}/assign', params={'user_id': user_id})
        self.log_test(
            "Assign Ticket",
            response['success'],
            f"Ticket assignment: {response['success']}"
        )
        
        # Test 9: Resolve Ticket
        resolution = "Problema resolvido. Substituída a fita de impressão e ajustada a temperatura da impressora."
        response = self.make_request('PATCH', f'/tickets/{ticket_id}/resolve', params={'resolution': resolution})
        self.log_test(
            "Resolve Ticket",
            response['success'],
            f"Ticket resolution: {response['success']}"
        )
        
        # Test 10: Rate Ticket
        response = self.make_request('PATCH', f'/tickets/{ticket_id}/rate', params={'rating': 5, 'comment': 'Excelente atendimento!'})
        self.log_test(
            "Rate Ticket",
            response['success'],
            f"Ticket rating: {response['success']}"
        )
        
        # Test 11: Filter Tickets
        response = self.make_request('GET', '/tickets/', params={'priority': 'urgent', 'status': 'resolved'})
        self.log_test(
            "Filter Tickets",
            response['success'],
            f"Filtered tickets: {response['success']}"
        )

    def test_goals_management(self):
        """Test Goals and Performance API"""
        print("\n=== Testing Goals and Performance API ===")
        
        # Need user for goal creation
        if not self.created_entities['users']:
            self.log_test("Goals Management Setup", False, "Missing user for goal tests")
            return
        
        user_id = self.created_entities['users'][0]
        
        # Test data
        goal_data = {
            "title": "Resolver 50 tickets por semana",
            "description": "Meta individual para resolução de tickets de suporte técnico",
            "target_value": 50.0,
            "unit": "tickets",
            "user_id": user_id,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Test 1: Create Goal
        response = self.make_request('POST', '/goals/', goal_data)
        if response['success']:
            goal_id = response['data']['data']['id']
            self.created_entities['goals'].append(goal_id)
            self.log_test("Create Goal", True, f"Created goal with ID: {goal_id}")
        else:
            self.log_test("Create Goal", False, f"Status: {response['status_code']}, Error: {response['data']}")
            return
        
        # Test 2: Get Goal by ID
        response = self.make_request('GET', f'/goals/{goal_id}')
        self.log_test(
            "Get Goal by ID",
            response['success'] and response['data']['data']['title'] == goal_data['title'],
            f"Retrieved goal: {response['data']['data']['title'] if response['success'] else response['data']}"
        )
        
        # Test 3: Get All Goals
        response = self.make_request('GET', '/goals/')
        self.log_test(
            "Get All Goals",
            response['success'] and len(response['data']['data']) > 0,
            f"Retrieved {len(response['data']['data']) if response['success'] else 0} goals"
        )
        
        # Test 4: Get Goals by User
        response = self.make_request('GET', f'/goals/user/{user_id}')
        self.log_test(
            "Get Goals by User",
            response['success'] and len(response['data']['data']) > 0,
            f"Found {len(response['data']['data']) if response['success'] else 0} goals for user"
        )
        
        # Test 5: Get Active Goals
        response = self.make_request('GET', '/goals/active/all')
        self.log_test(
            "Get Active Goals",
            response['success'],
            f"Retrieved active goals: {response['success']}"
        )
        
        # Test 6: Update Goal Progress
        response = self.make_request('PATCH', f'/goals/{goal_id}/progress', params={'current_value': 25.0})
        self.log_test(
            "Update Goal Progress",
            response['success'] and response['data']['data']['current_value'] == 25.0,
            f"Updated progress: {response['data']['data']['current_value'] if response['success'] else response['data']}"
        )
        
        # Test 7: Update Goal
        update_data = {
            "title": "Resolver 60 tickets por semana",
            "target_value": 60.0,
            "description": "Meta individual aumentada para resolução de tickets"
        }
        response = self.make_request('PUT', f'/goals/{goal_id}', update_data)
        self.log_test(
            "Update Goal",
            response['success'] and response['data']['data']['target_value'] == 60.0,
            f"Updated goal: {response['success']}"
        )
        
        # Test 8: Filter Goals
        response = self.make_request('GET', '/goals/', params={'unit': 'tickets', 'is_active': True})
        self.log_test(
            "Filter Goals",
            response['success'],
            f"Filtered goals: {response['success']}"
        )

    def test_attendance_management(self):
        """Test Attendance Management API"""
        print("\n=== Testing Attendance Management API ===")
        
        # Need user for attendance
        if not self.created_entities['users']:
            self.log_test("Attendance Management Setup", False, "Missing user for attendance tests")
            return
        
        user_id = self.created_entities['users'][0]
        
        # Test 1: Check In
        response = self.make_request('POST', '/attendance/checkin', params={'user_id': user_id})
        if response['success']:
            attendance_id = response['data']['data']['id']
            self.created_entities['attendance'].append(attendance_id)
            self.log_test("Check In", True, f"Check-in successful for user: {user_id}")
        else:
            self.log_test("Check In", False, f"Status: {response['status_code']}, Error: {response['data']}")
            return
        
        # Test 2: Get Attendance by ID
        response = self.make_request('GET', f'/attendance/{attendance_id}')
        self.log_test(
            "Get Attendance by ID",
            response['success'] and response['data']['data']['user_id'] == user_id,
            f"Retrieved attendance: {response['success']}"
        )
        
        # Test 3: Get All Attendance Records
        response = self.make_request('GET', '/attendance/')
        self.log_test(
            "Get All Attendance Records",
            response['success'] and len(response['data']['data']) > 0,
            f"Retrieved {len(response['data']['data']) if response['success'] else 0} attendance records"
        )
        
        # Test 4: Get Attendance by User
        response = self.make_request('GET', f'/attendance/user/{user_id}')
        self.log_test(
            "Get Attendance by User",
            response['success'] and len(response['data']['data']) > 0,
            f"Found {len(response['data']['data']) if response['success'] else 0} attendance records for user"
        )
        
        # Test 5: Get Attendance by User and Date
        today = date.today().isoformat()
        response = self.make_request('GET', f'/attendance/user/{user_id}/date/{today}')
        self.log_test(
            "Get Attendance by User and Date",
            response['success'],
            f"Found attendance for today: {response['success']}"
        )
        
        # Test 6: Check Out
        response = self.make_request('POST', '/attendance/checkout', params={'user_id': user_id})
        self.log_test(
            "Check Out",
            response['success'] and response['data']['data'].get('hours_worked') is not None,
            f"Check-out successful with hours calculated: {response['success']}"
        )
        
        # Test 7: Update Attendance
        update_data = {
            "notes": "Trabalho remoto - reunião com cliente",
            "status": "present"
        }
        response = self.make_request('PUT', f'/attendance/{attendance_id}', update_data)
        self.log_test(
            "Update Attendance",
            response['success'],
            f"Updated attendance: {response['success']}"
        )
        
        # Test 8: Filter Attendance by Date Range
        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = date.today().isoformat()
        response = self.make_request('GET', '/attendance/', params={
            'user_id': user_id,
            'date_from': start_date,
            'date_to': end_date
        })
        self.log_test(
            "Filter Attendance by Date Range",
            response['success'],
            f"Filtered attendance records: {response['success']}"
        )

    def test_monitoring_metrics(self):
        """Test Monitoring Metrics API"""
        print("\n=== Testing Monitoring Metrics API ===")
        
        # Need user for metrics
        user_id = self.created_entities['users'][0] if self.created_entities['users'] else None
        
        # Test data
        metric_data = {
            "name": "tickets_resolved_per_hour",
            "value": 8.5,
            "unit": "tickets/hour",
            "category": "performance",
            "user_id": user_id,
            "metadata": {
                "shift": "morning",
                "department": "technical_support",
                "complexity": "medium"
            }
        }
        
        # Test 1: Create Metric
        response = self.make_request('POST', '/monitoring/metrics', metric_data)
        if response['success']:
            metric_id = response['data']['data']['id']
            self.created_entities['monitoring'].append(metric_id)
            self.log_test("Create Metric", True, f"Created metric with ID: {metric_id}")
        else:
            self.log_test("Create Metric", False, f"Status: {response['status_code']}, Error: {response['data']}")
            return
        
        # Test 2: Get Metric by ID
        response = self.make_request('GET', f'/monitoring/metrics/{metric_id}')
        self.log_test(
            "Get Metric by ID",
            response['success'] and response['data']['data']['name'] == metric_data['name'],
            f"Retrieved metric: {response['data']['data']['name'] if response['success'] else response['data']}"
        )
        
        # Test 3: Get All Metrics
        response = self.make_request('GET', '/monitoring/metrics')
        self.log_test(
            "Get All Metrics",
            response['success'] and len(response['data']['data']) > 0,
            f"Retrieved {len(response['data']['data']) if response['success'] else 0} metrics"
        )
        
        # Test 4: Get Metrics by Category
        response = self.make_request('GET', '/monitoring/metrics/category/performance')
        self.log_test(
            "Get Metrics by Category",
            response['success'] and len(response['data']['data']) > 0,
            f"Found {len(response['data']['data']) if response['success'] else 0} performance metrics"
        )
        
        # Test 5: Get Metrics by User
        if user_id:
            response = self.make_request('GET', f'/monitoring/metrics/user/{user_id}')
            self.log_test(
                "Get Metrics by User",
                response['success'],
                f"Found metrics for user: {response['success']}"
            )
        
        # Test 6: Get Latest Metrics
        response = self.make_request('GET', '/monitoring/metrics/latest', params={'limit': 10})
        self.log_test(
            "Get Latest Metrics",
            response['success'],
            f"Retrieved latest metrics: {response['success']}"
        )
        
        # Test 7: Get Dashboard Data
        response = self.make_request('GET', '/monitoring/dashboard')
        self.log_test(
            "Get Dashboard Data",
            response['success'] and 'performance' in response['data']['data'],
            f"Retrieved dashboard data: {response['success']}"
        )
        
        # Test 8: Filter Metrics
        response = self.make_request('GET', '/monitoring/metrics', params={
            'category': 'performance',
            'limit': 5
        })
        self.log_test(
            "Filter Metrics",
            response['success'],
            f"Filtered metrics: {response['success']}"
        )

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n=== Testing Edge Cases and Error Handling ===")
        
        # Test 1: Get Non-existent User
        fake_id = str(uuid.uuid4())
        response = self.make_request('GET', f'/users/{fake_id}')
        self.log_test(
            "Get Non-existent User",
            response['status_code'] == 404,
            f"Status code: {response['status_code']}, Expected: 404"
        )
        
        # Test 2: Create User with Invalid Email
        invalid_user = {
            "name": "Test User",
            "email": "invalid-email",
            "role": "agent"
        }
        response = self.make_request('POST', '/users/', invalid_user)
        self.log_test(
            "Create User with Invalid Email",
            not response['success'],
            f"Correctly rejected invalid email: {not response['success']}"
        )
        
        # Test 3: Create Ticket with Non-existent Customer
        invalid_ticket = {
            "title": "Test Ticket",
            "description": "Test Description",
            "channel": "email",
            "customer_id": str(uuid.uuid4())
        }
        response = self.make_request('POST', '/tickets/', invalid_ticket)
        self.log_test(
            "Create Ticket with Non-existent Customer",
            not response['success'] and response['status_code'] == 404,
            f"Correctly rejected non-existent customer: {response['status_code'] == 404}"
        )
        
        # Test 4: Rate Ticket with Invalid Rating
        if self.created_entities['tickets']:
            ticket_id = self.created_entities['tickets'][0]
            response = self.make_request('PATCH', f'/tickets/{ticket_id}/rate', params={'rating': 10})
            self.log_test(
                "Rate Ticket with Invalid Rating",
                not response['success'] and response['status_code'] == 400,
                f"Correctly rejected invalid rating: {response['status_code'] == 400}"
            )
        
        # Test 5: Update Non-existent Goal
        fake_goal_id = str(uuid.uuid4())
        response = self.make_request('PUT', f'/goals/{fake_goal_id}', {"title": "Updated Goal"})
        self.log_test(
            "Update Non-existent Goal",
            not response['success'] and response['status_code'] == 404,
            f"Correctly returned 404: {response['status_code'] == 404}"
        )

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        cleanup_count = 0
        
        # Delete in reverse order to handle dependencies
        for entity_type in ['monitoring', 'attendance', 'tickets', 'goals', 'customers', 'users']:
            for entity_id in self.created_entities[entity_type]:
                endpoint_map = {
                    'users': '/users/',
                    'customers': '/customers/',
                    'tickets': '/tickets/',
                    'goals': '/goals/',
                    'attendance': '/attendance/',
                    'monitoring': '/monitoring/metrics/'
                }
                
                endpoint = endpoint_map[entity_type] + entity_id
                response = self.make_request('DELETE', endpoint)
                if response['success']:
                    cleanup_count += 1
        
        print(f"Cleaned up {cleanup_count} test entities")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive Backend API Testing for StarPrint CRM")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Run all test suites
        self.test_health_check()
        self.test_user_management()
        self.test_customer_management()
        self.test_ticket_management()
        self.test_goals_management()
        self.test_attendance_management()
        self.test_monitoring_metrics()
        self.test_edge_cases()
        
        # Clean up test data
        self.cleanup_test_data()
        
        # Generate summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duration: {duration.total_seconds():.2f} seconds")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎉 Testing completed!")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'duration': duration.total_seconds(),
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = APITester(BACKEND_URL)
    results = tester.run_all_tests()