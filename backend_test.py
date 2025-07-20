#!/usr/bin/env python3
"""
StarPrint CRM Backend API Testing Suite
Tests all backend endpoints comprehensively including authentication, team management, shifts, and dashboard.
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys

# Backend URL from frontend/.env
BASE_URL = "https://f3c85fdb-8f92-495a-adb8-255eae7bdd70.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.manager_token = None
        self.agent_token = None
        self.manager_user = None
        self.agent_user = None
        self.test_team_member_id = None
        self.test_shift_id = None
        self.results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "team_management": {"passed": 0, "failed": 0, "details": []},
            "shift_management": {"passed": 0, "failed": 0, "details": []},
            "dashboard": {"passed": 0, "failed": 0, "details": []},
            "error_handling": {"passed": 0, "failed": 0, "details": []}
        }

    def log_result(self, category, test_name, passed, details=""):
        """Log test result"""
        if passed:
            self.results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results[category]["failed"] += 1
            status = "❌ FAIL"
        
        self.results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")

    def test_user_registration(self):
        """Test user registration for both manager and agent roles"""
        print("\n=== TESTING USER REGISTRATION ===")
        
        # Test manager registration
        manager_data = {
            "email": f"manager_{uuid.uuid4().hex[:8]}@starprint.com",
            "name": "Sarah Johnson",
            "password": "SecurePass123!",
            "role": "manager"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=manager_data)
            if response.status_code == 200:
                data = response.json()
                self.manager_token = data["access_token"]
                self.manager_user = data["user"]
                self.log_result("authentication", "Manager Registration", True, 
                              f"Manager registered successfully with ID: {self.manager_user['id']}")
            else:
                self.log_result("authentication", "Manager Registration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("authentication", "Manager Registration", False, f"Exception: {str(e)}")

        # Test agent registration
        agent_data = {
            "email": f"agent_{uuid.uuid4().hex[:8]}@starprint.com",
            "name": "Mike Chen",
            "password": "AgentPass456!",
            "role": "agent"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=agent_data)
            if response.status_code == 200:
                data = response.json()
                self.agent_token = data["access_token"]
                self.agent_user = data["user"]
                self.log_result("authentication", "Agent Registration", True, 
                              f"Agent registered successfully with ID: {self.agent_user['id']}")
            else:
                self.log_result("authentication", "Agent Registration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("authentication", "Agent Registration", False, f"Exception: {str(e)}")

    def test_user_login(self):
        """Test user login functionality"""
        print("\n=== TESTING USER LOGIN ===")
        
        if not self.manager_user or not self.agent_user:
            self.log_result("authentication", "Login Test Setup", False, "Registration failed, cannot test login")
            return

        # Test manager login
        manager_login = {
            "email": self.manager_user["email"],
            "password": "SecurePass123!"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=manager_login)
            if response.status_code == 200:
                data = response.json()
                self.log_result("authentication", "Manager Login", True, 
                              f"Manager logged in successfully, token received")
            else:
                self.log_result("authentication", "Manager Login", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("authentication", "Manager Login", False, f"Exception: {str(e)}")

        # Test agent login
        agent_login = {
            "email": self.agent_user["email"],
            "password": "AgentPass456!"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=agent_login)
            if response.status_code == 200:
                data = response.json()
                self.log_result("authentication", "Agent Login", True, 
                              f"Agent logged in successfully, token received")
            else:
                self.log_result("authentication", "Agent Login", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("authentication", "Agent Login", False, f"Exception: {str(e)}")

    def test_auth_me_endpoint(self):
        """Test auth/me endpoint to verify user info retrieval"""
        print("\n=== TESTING AUTH/ME ENDPOINT ===")
        
        if not self.manager_token:
            self.log_result("authentication", "Auth/Me Test Setup", False, "No manager token available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/auth/me", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data["id"] == self.manager_user["id"] and data["role"] == "manager":
                    self.log_result("authentication", "Auth/Me Endpoint", True, 
                                  f"User info retrieved correctly: {data['name']} ({data['role']})")
                else:
                    self.log_result("authentication", "Auth/Me Endpoint", False, 
                                  f"User info mismatch: {data}")
            else:
                self.log_result("authentication", "Auth/Me Endpoint", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("authentication", "Auth/Me Endpoint", False, f"Exception: {str(e)}")

    def test_invalid_login(self):
        """Test invalid login attempts"""
        print("\n=== TESTING INVALID LOGIN ===")
        
        # Test with wrong password
        invalid_login = {
            "email": self.manager_user["email"] if self.manager_user else "test@example.com",
            "password": "WrongPassword123!"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=invalid_login)
            if response.status_code == 400:
                self.log_result("authentication", "Invalid Password Login", True, 
                              "Correctly rejected invalid password")
            else:
                self.log_result("authentication", "Invalid Password Login", False, 
                              f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("authentication", "Invalid Password Login", False, f"Exception: {str(e)}")

        # Test with non-existent email
        nonexistent_login = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=nonexistent_login)
            if response.status_code == 400:
                self.log_result("authentication", "Non-existent Email Login", True, 
                              "Correctly rejected non-existent email")
            else:
                self.log_result("authentication", "Non-existent Email Login", False, 
                              f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("authentication", "Non-existent Email Login", False, f"Exception: {str(e)}")

    def test_team_member_creation(self):
        """Test team member creation with role-based access"""
        print("\n=== TESTING TEAM MEMBER CREATION ===")
        
        if not self.manager_token:
            self.log_result("team_management", "Team Member Creation Setup", False, "No manager token available")
            return

        # Test creating team member with manager account
        team_member_data = {
            "name": "Jessica Williams",
            "email": f"jessica_{uuid.uuid4().hex[:8]}@starprint.com",
            "role": "agent",
            "phone": "+1-555-0123",
            "department": "Customer Support",
            "hire_date": datetime.utcnow().isoformat()
        }
        
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.post(f"{self.base_url}/team-members", json=team_member_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_team_member_id = data["id"]
                self.log_result("team_management", "Manager Create Team Member", True, 
                              f"Team member created successfully: {data['name']} (ID: {data['id']})")
            else:
                self.log_result("team_management", "Manager Create Team Member", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("team_management", "Manager Create Team Member", False, f"Exception: {str(e)}")

        # Test creating team member with agent account (should fail)
        if self.agent_token:
            agent_headers = {"Authorization": f"Bearer {self.agent_token}"}
            
            try:
                response = requests.post(f"{self.base_url}/team-members", json=team_member_data, headers=agent_headers)
                if response.status_code == 403:
                    self.log_result("team_management", "Agent Create Team Member (Should Fail)", True, 
                                  "Correctly rejected agent attempt to create team member")
                else:
                    self.log_result("team_management", "Agent Create Team Member (Should Fail)", False, 
                                  f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("team_management", "Agent Create Team Member (Should Fail)", False, f"Exception: {str(e)}")

    def test_team_member_listing(self):
        """Test listing all team members"""
        print("\n=== TESTING TEAM MEMBER LISTING ===")
        
        if not self.manager_token:
            self.log_result("team_management", "Team Member Listing Setup", False, "No manager token available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/team-members", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("team_management", "List Team Members", True, 
                              f"Retrieved {len(data)} team members")
            else:
                self.log_result("team_management", "List Team Members", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("team_management", "List Team Members", False, f"Exception: {str(e)}")

    def test_team_member_update(self):
        """Test updating team member details and status"""
        print("\n=== TESTING TEAM MEMBER UPDATE ===")
        
        if not self.manager_token or not self.test_team_member_id:
            self.log_result("team_management", "Team Member Update Setup", False, "No manager token or team member ID available")
            return

        update_data = {
            "status": "on_leave",
            "department": "Technical Support"
        }
        
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.put(f"{self.base_url}/team-members/{self.test_team_member_id}", 
                                  json=update_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "on_leave" and data["department"] == "Technical Support":
                    self.log_result("team_management", "Update Team Member", True, 
                                  f"Team member updated successfully: status={data['status']}, dept={data['department']}")
                else:
                    self.log_result("team_management", "Update Team Member", False, 
                                  f"Update data mismatch: {data}")
            else:
                self.log_result("team_management", "Update Team Member", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("team_management", "Update Team Member", False, f"Exception: {str(e)}")

    def test_shift_creation(self):
        """Test shift creation with role-based access"""
        print("\n=== TESTING SHIFT CREATION ===")
        
        if not self.manager_token or not self.test_team_member_id:
            self.log_result("shift_management", "Shift Creation Setup", False, "No manager token or team member ID available")
            return

        # Create shift for tomorrow
        tomorrow = datetime.utcnow() + timedelta(days=1)
        shift_start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        shift_end = shift_start + timedelta(hours=8)
        
        shift_data = {
            "team_member_id": self.test_team_member_id,
            "start_time": shift_start.isoformat(),
            "end_time": shift_end.isoformat(),
            "notes": "Regular morning shift"
        }
        
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.post(f"{self.base_url}/shifts", json=shift_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_shift_id = data["id"]
                self.log_result("shift_management", "Manager Create Shift", True, 
                              f"Shift created successfully: {data['team_member_name']} from {data['start_time']} to {data['end_time']}")
            else:
                self.log_result("shift_management", "Manager Create Shift", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("shift_management", "Manager Create Shift", False, f"Exception: {str(e)}")

        # Test creating shift with agent account (should fail)
        if self.agent_token:
            agent_headers = {"Authorization": f"Bearer {self.agent_token}"}
            
            try:
                response = requests.post(f"{self.base_url}/shifts", json=shift_data, headers=agent_headers)
                if response.status_code == 403:
                    self.log_result("shift_management", "Agent Create Shift (Should Fail)", True, 
                                  "Correctly rejected agent attempt to create shift")
                else:
                    self.log_result("shift_management", "Agent Create Shift (Should Fail)", False, 
                                  f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("shift_management", "Agent Create Shift (Should Fail)", False, f"Exception: {str(e)}")

    def test_shift_status_update(self):
        """Test updating shift status"""
        print("\n=== TESTING SHIFT STATUS UPDATE ===")
        
        if not self.manager_token or not self.test_shift_id:
            self.log_result("shift_management", "Shift Status Update Setup", False, "No manager token or shift ID available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        # Update shift to in_progress
        try:
            response = requests.put(f"{self.base_url}/shifts/{self.test_shift_id}/status", 
                                  params={"status": "in_progress"}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "in_progress":
                    self.log_result("shift_management", "Update Shift to In Progress", True, 
                                  f"Shift status updated to: {data['status']}")
                else:
                    self.log_result("shift_management", "Update Shift to In Progress", False, 
                                  f"Status mismatch: expected 'in_progress', got '{data['status']}'")
            else:
                self.log_result("shift_management", "Update Shift to In Progress", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("shift_management", "Update Shift to In Progress", False, f"Exception: {str(e)}")

        # Update shift to completed
        try:
            response = requests.put(f"{self.base_url}/shifts/{self.test_shift_id}/status", 
                                  params={"status": "completed"}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "completed":
                    self.log_result("shift_management", "Update Shift to Completed", True, 
                                  f"Shift status updated to: {data['status']}")
                else:
                    self.log_result("shift_management", "Update Shift to Completed", False, 
                                  f"Status mismatch: expected 'completed', got '{data['status']}'")
            else:
                self.log_result("shift_management", "Update Shift to Completed", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("shift_management", "Update Shift to Completed", False, f"Exception: {str(e)}")

    def test_shift_listing(self):
        """Test listing shifts with proper sorting"""
        print("\n=== TESTING SHIFT LISTING ===")
        
        if not self.manager_token:
            self.log_result("shift_management", "Shift Listing Setup", False, "No manager token available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/shifts", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("shift_management", "List Shifts", True, 
                              f"Retrieved {len(data)} shifts")
            else:
                self.log_result("shift_management", "List Shifts", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("shift_management", "List Shifts", False, f"Exception: {str(e)}")

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        print("\n=== TESTING DASHBOARD STATS ===")
        
        if not self.manager_token:
            self.log_result("dashboard", "Dashboard Stats Setup", False, "No manager token available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=headers)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_team_members", "active_members", "members_on_shift", 
                                 "completed_shifts_today", "upcoming_shifts", "missed_shifts"]
                
                if all(field in data for field in required_fields):
                    self.log_result("dashboard", "Dashboard Stats", True, 
                                  f"Stats retrieved: {data['total_team_members']} total members, {data['active_members']} active")
                else:
                    self.log_result("dashboard", "Dashboard Stats", False, 
                                  f"Missing required fields in response: {data}")
            else:
                self.log_result("dashboard", "Dashboard Stats", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("dashboard", "Dashboard Stats", False, f"Exception: {str(e)}")

    def test_recent_shifts(self):
        """Test recent shifts endpoint"""
        print("\n=== TESTING RECENT SHIFTS ===")
        
        if not self.manager_token:
            self.log_result("dashboard", "Recent Shifts Setup", False, "No manager token available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/recent-shifts", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("dashboard", "Recent Shifts", True, 
                              f"Retrieved {len(data)} recent shifts")
            else:
                self.log_result("dashboard", "Recent Shifts", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("dashboard", "Recent Shifts", False, f"Exception: {str(e)}")

    def test_unauthorized_access(self):
        """Test endpoints without authentication"""
        print("\n=== TESTING UNAUTHORIZED ACCESS ===")
        
        endpoints = [
            "/auth/me",
            "/team-members",
            "/shifts",
            "/dashboard/stats"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code == 401 or response.status_code == 403:
                    self.log_result("error_handling", f"Unauthorized Access {endpoint}", True, 
                                  f"Correctly rejected unauthorized access (status: {response.status_code})")
                else:
                    self.log_result("error_handling", f"Unauthorized Access {endpoint}", False, 
                                  f"Expected 401/403, got {response.status_code}")
            except Exception as e:
                self.log_result("error_handling", f"Unauthorized Access {endpoint}", False, f"Exception: {str(e)}")

    def test_nonexistent_resources(self):
        """Test CRUD operations with non-existent IDs"""
        print("\n=== TESTING NON-EXISTENT RESOURCES ===")
        
        if not self.manager_token:
            self.log_result("error_handling", "Non-existent Resources Setup", False, "No manager token available")
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        fake_id = str(uuid.uuid4())
        
        # Test non-existent team member
        try:
            response = requests.put(f"{self.base_url}/team-members/{fake_id}", 
                                  json={"name": "Test"}, headers=headers)
            if response.status_code == 404:
                self.log_result("error_handling", "Non-existent Team Member Update", True, 
                              "Correctly returned 404 for non-existent team member")
            else:
                self.log_result("error_handling", "Non-existent Team Member Update", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Non-existent Team Member Update", False, f"Exception: {str(e)}")

        # Test non-existent shift
        try:
            response = requests.put(f"{self.base_url}/shifts/{fake_id}/status", 
                                  params={"status": "completed"}, headers=headers)
            if response.status_code == 404:
                self.log_result("error_handling", "Non-existent Shift Update", True, 
                              "Correctly returned 404 for non-existent shift")
            else:
                self.log_result("error_handling", "Non-existent Shift Update", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Non-existent Shift Update", False, f"Exception: {str(e)}")

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n=== CLEANING UP TEST DATA ===")
        
        if not self.manager_token:
            return

        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        # Delete test team member (this will also delete associated shifts)
        if self.test_team_member_id:
            try:
                response = requests.delete(f"{self.base_url}/team-members/{self.test_team_member_id}", headers=headers)
                if response.status_code == 200:
                    print("✅ Test team member and associated shifts cleaned up successfully")
                else:
                    print(f"⚠️ Failed to clean up test team member: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Exception during cleanup: {str(e)}")

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("STARPRINT CRM BACKEND API TEST SUMMARY")
        print("="*80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            if results["details"]:
                for detail in results["details"]:
                    print(f"    {detail}")
        
        print(f"\n{'='*80}")
        print(f"OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📊 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%" if (total_passed+total_failed) > 0 else "N/A")
        print("="*80)
        
        return total_passed, total_failed

    def run_all_tests(self):
        """Run all backend API tests"""
        print("Starting StarPrint CRM Backend API Testing...")
        print(f"Testing against: {self.base_url}")
        
        # Authentication tests
        self.test_user_registration()
        self.test_user_login()
        self.test_auth_me_endpoint()
        self.test_invalid_login()
        
        # Team management tests
        self.test_team_member_creation()
        self.test_team_member_listing()
        self.test_team_member_update()
        
        # Shift management tests
        self.test_shift_creation()
        self.test_shift_status_update()
        self.test_shift_listing()
        
        # Dashboard tests
        self.test_dashboard_stats()
        self.test_recent_shifts()
        
        # Error handling tests
        self.test_unauthorized_access()
        self.test_nonexistent_resources()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        total_passed, total_failed = self.print_summary()
        
        return total_passed > 0 and total_failed == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)