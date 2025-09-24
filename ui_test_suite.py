#!/usr/bin/env python3
"""
Comprehensive UI Test Suite for Genie Task Management System
Tests multiple user flow scenarios to identify and fix UI issues
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UITestSuite:
    """Comprehensive UI testing suite for Genie system"""
    
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
    
    def test_health_check(self):
        """Test 1: Basic health check"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('status') == 'healthy':
                    self.log_test("Health Check", True, "System is healthy")
                    return True
                else:
                    self.log_test("Health Check", False, f"Health check failed: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {e}")
            return False
    
    def test_homepage_load(self):
        """Test 2: Homepage loads correctly"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                if "genie" in response.text.lower():
                    self.log_test("Homepage Load", True, "Homepage loaded successfully")
                    return True
                else:
                    self.log_test("Homepage Load", False, "Homepage content not found")
                    return False
            else:
                self.log_test("Homepage Load", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Homepage Load", False, f"Exception: {e}")
            return False
    
    def test_task_creation_flow(self, task_description: str):
        """Test 3: Complete task creation flow"""
        try:
            # Create task
            task_data = {
                "task_name": task_description,
                "user_id": "test_user"
            }
            response = self.session.post(f"{self.base_url}/api/tasks", json=task_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    task_id = data.get('task_id')
                    self.log_test(f"Task Creation: {task_description[:30]}...", True, f"Task ID: {task_id}")
                    
                    # Get current subtask
                    subtask_response = self.session.get(f"{self.base_url}/api/current-subtask")
                    if subtask_response.status_code == 200:
                        subtask_data = subtask_response.json()
                        if subtask_data.get('success'):
                            self.log_test("Current Subtask Retrieval", True, "Subtask retrieved")
                            return task_id
                        else:
                            self.log_test("Current Subtask Retrieval", False, "Failed to get subtask")
                            return task_id
                    else:
                        self.log_test("Current Subtask Retrieval", False, f"HTTP {subtask_response.status_code}")
                        return task_id
                else:
                    self.log_test(f"Task Creation: {task_description[:30]}...", False, f"API error: {data}")
                    return None
            else:
                self.log_test(f"Task Creation: {task_description[:30]}...", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test(f"Task Creation: {task_description[:30]}...", False, f"Exception: {e}")
            return None
    
    def test_feedback_submission(self, feedback_type: str):
        """Test 4: Feedback submission"""
        try:
            feedback_data = {
                "feedback_type": feedback_type,
                "feedback_text": f"Test feedback: {feedback_type}",
                "rating": 4,
                "user_id": "test_user"
            }
            response = self.session.post(f"{self.base_url}/api/feedback", json=feedback_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(f"Feedback Submission: {feedback_type}", True, "Feedback submitted successfully")
                    return True
                else:
                    self.log_test(f"Feedback Submission: {feedback_type}", False, f"API error: {data}")
                    return False
            else:
                self.log_test(f"Feedback Submission: {feedback_type}", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"Feedback Submission: {feedback_type}", False, f"Exception: {e}")
            return False
    
    def test_task_list_retrieval(self):
        """Test 5: Task list retrieval"""
        try:
            response = self.session.get(f"{self.base_url}/api/tasks?user_id=test_user")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    tasks = data.get('tasks', [])
                    self.log_test("Task List Retrieval", True, f"Retrieved {len(tasks)} tasks")
                    return tasks
                else:
                    self.log_test("Task List Retrieval", False, f"API error: {data}")
                    return []
            else:
                self.log_test("Task List Retrieval", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Task List Retrieval", False, f"Exception: {e}")
            return []
    
    def test_task_transition_flow(self):
        """Test 6: Complete task transition flow (create -> feedback -> next task)"""
        try:
            # Step 1: Create first task
            task1_id = self.test_task_creation_flow("Learn JavaScript programming")
            if not task1_id:
                self.log_test("Task Transition Flow", False, "Failed to create first task")
                return False
            
            time.sleep(2)  # Wait for processing
            
            # Step 2: Submit feedback
            feedback_success = self.test_feedback_submission("done")
            if not feedback_success:
                self.log_test("Task Transition Flow", False, "Failed to submit feedback")
                return False
            
            time.sleep(2)  # Wait for processing
            
            # Step 3: Create second task
            task2_id = self.test_task_creation_flow("Build a React application")
            if not task2_id:
                self.log_test("Task Transition Flow", False, "Failed to create second task")
                return False
            
            # Step 4: Verify both tasks exist
            tasks = self.test_task_list_retrieval()
            if len(tasks) >= 2:
                self.log_test("Task Transition Flow", True, f"Successfully transitioned between {len(tasks)} tasks")
                return True
            else:
                self.log_test("Task Transition Flow", False, f"Expected 2+ tasks, got {len(tasks)}")
                return False
                
        except Exception as e:
            self.log_test("Task Transition Flow", False, f"Exception: {e}")
            return False
    
    def test_multiple_feedback_scenarios(self):
        """Test 7: Test multiple feedback scenarios"""
        try:
            # Create a task for feedback testing
            task_id = self.test_task_creation_flow("Test feedback scenarios")
            if not task_id:
                return False
            
            time.sleep(2)
            
            # Test different feedback types
            feedback_types = ["done", "difficult", "easy"]
            success_count = 0
            
            for feedback_type in feedback_types:
                if self.test_feedback_submission(feedback_type):
                    success_count += 1
                time.sleep(1)  # Small delay between feedback
            
            if success_count == len(feedback_types):
                self.log_test("Multiple Feedback Scenarios", True, f"All {len(feedback_types)} feedback types worked")
                return True
            else:
                self.log_test("Multiple Feedback Scenarios", False, f"{success_count}/{len(feedback_types)} feedback types worked")
                return False
                
        except Exception as e:
            self.log_test("Multiple Feedback Scenarios", False, f"Exception: {e}")
            return False
    
    def test_session_persistence(self):
        """Test 8: Test session persistence across requests"""
        try:
            # Create task with session
            task_id = self.test_task_creation_flow("Session persistence test")
            if not task_id:
                return False
            
            time.sleep(2)
            
            # Make multiple requests to test session persistence
            requests_made = 0
            successful_requests = 0
            
            for i in range(5):
                response = self.session.get(f"{self.base_url}/api/current-subtask")
                requests_made += 1
                if response.status_code == 200:
                    successful_requests += 1
                time.sleep(0.5)
            
            if successful_requests == requests_made:
                self.log_test("Session Persistence", True, f"All {requests_made} requests successful")
                return True
            else:
                self.log_test("Session Persistence", False, f"{successful_requests}/{requests_made} requests successful")
                return False
                
        except Exception as e:
            self.log_test("Session Persistence", False, f"Exception: {e}")
            return False
    
    def test_error_handling(self):
        """Test 9: Test error handling for invalid requests"""
        try:
            # Test invalid task creation
            invalid_data = {"invalid_field": "test"}
            response = self.session.post(f"{self.base_url}/api/tasks", json=invalid_data)
            
            if response.status_code in [400, 422, 500]:
                self.log_test("Error Handling - Invalid Task", True, f"Properly handled invalid request: {response.status_code}")
            else:
                self.log_test("Error Handling - Invalid Task", False, f"Expected error status, got {response.status_code}")
            
            # Test invalid feedback
            invalid_feedback = {"invalid_field": "test"}
            response = self.session.post(f"{self.base_url}/api/feedback", json=invalid_feedback)
            
            if response.status_code in [400, 422, 500]:
                self.log_test("Error Handling - Invalid Feedback", True, f"Properly handled invalid feedback: {response.status_code}")
                return True
            else:
                self.log_test("Error Handling - Invalid Feedback", False, f"Expected error status, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {e}")
            return False
    
    def test_concurrent_operations(self):
        """Test 10: Test concurrent operations"""
        try:
            import threading
            
            results = []
            
            def create_task(task_name):
                try:
                    task_data = {"task_name": task_name, "user_id": "test_user"}
                    response = self.session.post(f"{self.base_url}/api/tasks", json=task_data)
                    results.append(response.status_code == 200)
                except:
                    results.append(False)
            
            # Create multiple threads for concurrent task creation
            threads = []
            task_names = ["Concurrent Task 1", "Concurrent Task 2", "Concurrent Task 3"]
            
            for task_name in task_names:
                thread = threading.Thread(target=create_task, args=(task_name,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            successful_operations = sum(results)
            if successful_operations >= 2:  # At least 2 out of 3 should succeed
                self.log_test("Concurrent Operations", True, f"{successful_operations}/3 concurrent operations successful")
                return True
            else:
                self.log_test("Concurrent Operations", False, f"{successful_operations}/3 concurrent operations successful")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Operations", False, f"Exception: {e}")
            return False
    
    def run_all_tests(self):
        """Run all test scenarios"""
        logger.info("🚀 Starting Comprehensive UI Test Suite")
        logger.info("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Homepage Load", self.test_homepage_load),
            ("Task Creation Flow", lambda: self.test_task_creation_flow("Test task creation")),
            ("Feedback Submission", lambda: self.test_feedback_submission("done")),
            ("Task List Retrieval", self.test_task_list_retrieval),
            ("Task Transition Flow", self.test_task_transition_flow),
            ("Multiple Feedback Scenarios", self.test_multiple_feedback_scenarios),
            ("Session Persistence", self.test_session_persistence),
            ("Error Handling", self.test_error_handling),
            ("Concurrent Operations", self.test_concurrent_operations)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test crashed: {e}")
        
        # Generate test report
        logger.info("=" * 60)
        logger.info(f"📊 Test Results: {passed}/{total} tests passed")
        logger.info("=" * 60)
        
        # Save detailed results
        with open("ui_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        return passed, total

def main():
    """Main function to run the UI test suite"""
    test_suite = UITestSuite()
    passed, total = test_suite.run_all_tests()
    
    if passed == total:
        print("🎉 All tests passed! UI is working correctly.")
        return 0
    else:
        print(f"⚠️ {total - passed} tests failed. Check ui_test_results.json for details.")
        return 1

if __name__ == "__main__":
    exit(main()) 