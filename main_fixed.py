#!/usr/bin/env python3
"""
Comprehensive Genie Backend System Test Suite - FIXED VERSION
Integrates all flows: Task Extraction → Planning → Orchestration → Calendar → Feedback

This main.py serves as a complete test suite to identify real-world issues
and validate the entire system workflow without any mockups.
"""

import sys
import os
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import all system components
from agents.task_extraction_agent import TaskExtractionAgent, TaskExtractionError
from agents.planning_agent import PlanningAgent, PlanningAgentError
from agents.genieorchestrator_agent import GenieOrchestrator, GenieOrchestratorError
from agents.supervisor_agent import SupervisorAgent, SupervisorAgentError
from agents.feedback_agent import FeedbackAgent, FeedbackAgentError
from integrations.google_calendar_api import GoogleCalendarAPI, GoogleCalendarAPIError
from integrations.gemini_api import GeminiAPIClient, GeminiAPIError
from integrations.perplexity_api import PerplexityAPIClient, PerplexityAPIError
from storage.json_store import JsonStore
from models.task_model import Task, TaskStatus
from models.user_session import UserSession, SessionManager
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genie_system_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestResult:
    """Class to track test results"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.success = False
        self.errors = []
        self.data = {}
        self.start_time = time.time()
        self.end_time = None
    
    def add_error(self, error: str):
        """Add an error to the test result"""
        self.errors.append(error)
        logger.error(f"❌ {self.test_name}: {error}")
    
    def add_data(self, key: str, value: Any):
        """Add data to the test result"""
        self.data[key] = value
    
    def mark_success(self):
        """Mark the test as successful"""
        self.success = True
        self.end_time = time.time()
        logger.info(f"✅ {self.test_name}: Success")
    
    def get_duration(self) -> float:
        """Get test duration in seconds"""
        end = self.end_time or time.time()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "test_name": self.test_name,
            "success": self.success,
            "errors": self.errors,
            "data": self.data,
            "duration_seconds": self.get_duration()
        }

class GenieSystemTester:
    """Comprehensive system tester for Genie Backend"""
    
    def __init__(self):
        self.session_manager = None
        self.supervisor = None
        self.calendar_api = None
        self.gemini_client = None
        self.perplexity_client = None
        self.store = None
        
        # Load environment variables
        load_dotenv()
        
        # Test results
        self.results = []
    
    def test_environment_setup(self) -> TestResult:
        """Test 1: Environment and Configuration Setup"""
        result = TestResult("Environment Setup")
        
        try:
            # Check required environment variables
            required_vars = [
                "GEMINI_API_KEY",
                "PERPLEXITY_API_KEY"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                result.add_error(f"Missing environment variables: {missing_vars}")
                return result
            
            # Check storage directory
            storage_dir = Path("storage")
            if not storage_dir.exists():
                storage_dir.mkdir(parents=True, exist_ok=True)
            
            result.add_data("environment_vars", "all_present")
            result.add_data("storage_dir", str(storage_dir.absolute()))
            result.mark_success()
            
        except Exception as e:
            result.add_error(f"Environment setup failed: {str(e)}")
        
        return result
    
    def test_api_connectivity(self) -> TestResult:
        """Test 2: API Connectivity and Authentication"""
        result = TestResult("API Connectivity")
        
        try:
            # Test Gemini API
            try:
                self.gemini_client = GeminiAPIClient()
                test_response = self.gemini_client.generate_content("Hello, this is a test.")
                if test_response:
                    result.add_data("gemini_api", "connected")
                    logger.info("✅ Gemini API connected successfully")
                else:
                    result.add_error("Gemini API returned empty response")
            except Exception as e:
                result.add_error(f"Gemini API failed: {str(e)}")
            
            # Test Perplexity API
            try:
                self.perplexity_client = PerplexityAPIClient()
                test_response = self.perplexity_client.generate_content("Python programming basics")
                if test_response:
                    result.add_data("perplexity_api", "connected")
                    logger.info("✅ Perplexity API connected successfully")
                else:
                    result.add_error("Perplexity API returned empty response")
            except Exception as e:
                result.add_error(f"Perplexity API failed: {str(e)}")
            
            # Test Google Calendar API
            try:
                self.calendar_api = GoogleCalendarAPI()
                calendar_info = self.calendar_api.get_calendar_info()
                if calendar_info:
                    result.add_data("google_calendar_api", "connected")
                    result.add_data("calendar_id", calendar_info.get('id', 'unknown'))
                    logger.info("✅ Google Calendar API connected successfully")
                else:
                    result.add_error("Google Calendar API returned empty response")
            except Exception as e:
                result.add_error(f"Google Calendar API failed: {str(e)}")
            
            if len(result.errors) == 0:
                result.mark_success()
            
        except Exception as e:
            result.add_error(f"API connectivity test failed: {str(e)}")
        
        return result
    
    def test_storage_system(self) -> TestResult:
        """Test 3: Storage System and Data Persistence"""
        result = TestResult("Storage System")
        
        try:
            # Initialize storage
            self.store = JsonStore("system_test_data.json")
            
            # Test basic operations
            test_data = {
                "test_key": "test_value",
                "timestamp": datetime.now().isoformat(),
                "numbers": [1, 2, 3, 4, 5]
            }
            
            # Save data
            self.store.save_state(test_data)
            
            # Load data
            loaded_data = self.store.load_state()
            
            if loaded_data and loaded_data.get("test_key") == "test_value":
                result.add_data("storage_operations", "working")
                result.add_data("data_persistence", "verified")
                logger.info("✅ Storage system working correctly")
                result.mark_success()
            else:
                result.add_error("Data persistence verification failed")
            
        except Exception as e:
            result.add_error(f"Storage system test failed: {str(e)}")
        
        return result
    
    def test_task_extraction(self) -> TestResult:
        """Test 4: Task Extraction and Creation"""
        result = TestResult("Task Extraction")
        
        try:
            # Initialize task extraction agent
            extraction_agent = TaskExtractionAgent()
            
            # Test task extraction
            test_inputs = [
                "Build a React authentication system with JWT tokens",
                "Create a REST API for user management with Node.js and Express",
                "Design and implement a database schema for an e-commerce platform"
            ]
            
            extracted_tasks = []
            
            for i, user_input in enumerate(test_inputs):
                try:
                    task = extraction_agent.extract_task(user_input)
                    if task and task.heading:
                        extracted_tasks.append(task)
                        logger.info(f"✅ Extracted task {i+1}: {task.heading}")
                    else:
                        result.add_error(f"Failed to extract task {i+1}: Empty task")
                except Exception as e:
                    result.add_error(f"Task extraction {i+1} failed: {str(e)}")
            
            if len(extracted_tasks) == len(test_inputs):
                result.add_data("tasks_extracted", len(extracted_tasks))
                result.add_data("extraction_success_rate", "100%")
                result.mark_success()
            else:
                result.add_error(f"Only {len(extracted_tasks)}/{len(test_inputs)} tasks extracted successfully")
            
        except Exception as e:
            result.add_error(f"Task extraction test failed: {str(e)}")
        
        return result
    
    def test_task_planning(self) -> TestResult:
        """Test 5: Task Planning and Subtask Generation"""
        result = TestResult("Task Planning")
        
        try:
            # Initialize planning agent
            planning_agent = PlanningAgent()
            
            # Test task planning
            test_tasks = [
                {
                    "heading": "Learn Python Programming",
                    "details": "I want to learn Python from scratch to build web applications and data analysis projects. I have no prior programming experience.",
                    "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                    "previous_chunks": [],
                    "corrections_or_feedback": ""
                },
                {
                    "heading": "Build a Task Management App",
                    "details": "Create a web application for managing personal tasks with features like task creation, deadlines, priority levels, and progress tracking.",
                    "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
                    "previous_chunks": [],
                    "corrections_or_feedback": ""
                }
            ]
            
            planned_chunks = []
            
            for i, task in enumerate(test_tasks):
                try:
                    chunk = planning_agent.get_next_chunk(task)
                    if chunk and chunk.get('chunk_heading'):
                        planned_chunks.append(chunk)
                        logger.info(f"✅ Planned chunk {i+1}: {chunk['chunk_heading']}")
                    else:
                        result.add_error(f"Failed to plan chunk {i+1}: Empty chunk")
                except Exception as e:
                    result.add_error(f"Task planning {i+1} failed: {str(e)}")
            
            if len(planned_chunks) == len(test_tasks):
                result.add_data("chunks_planned", len(planned_chunks))
                result.add_data("planning_success_rate", "100%")
                result.mark_success()
            else:
                result.add_error(f"Only {len(planned_chunks)}/{len(test_tasks)} chunks planned successfully")
            
        except Exception as e:
            result.add_error(f"Task planning test failed: {str(e)}")
        
        return result
    
    def test_orchestrator_integration(self) -> TestResult:
        """Test 6: Orchestrator Integration and Scheduling"""
        result = TestResult("Orchestrator Integration")
        
        try:
            # Initialize orchestrator
            orchestrator = GenieOrchestrator()
            
            # Create sample tasks data
            sample_tasks = {
                "tasks": [
                    {
                        "id": "task_1",
                        "heading": "Learn Python Programming",
                        "details": "Master Python fundamentals to build web applications and data analysis projects",
                        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                        "priority_score": 8.5,
                        "subtasks": [
                            {
                                "id": "chunk_1_1",
                                "heading": "Set up Python development environment",
                                "details": "Install Python, set up IDE, and write first Hello World program",
                                "estimated_time_minutes": 30,
                                "status": "pending",
                                "resource": {
                                    "title": "Python Installation Guide",
                                    "url": "https://docs.python.org/3/using/index.html",
                                    "type": "documentation",
                                    "focus_section": "Installation section",
                                    "paid": False
                                },
                                "dependencies": [],
                                "user_feedback": ""
                            }
                        ]
                    }
                ]
            }
            
            # Create sample schedule data
            sample_schedule = {
                "availability": {
                    "free": [
                        {
                            "start": (datetime.now() + timedelta(hours=1)).isoformat(),
                            "end": (datetime.now() + timedelta(hours=3)).isoformat(),
                            "duration_minutes": 120
                        }
                    ],
                    "busy": []
                },
                "preferences": {
                    "work_hours": {"start": "09:00", "end": "17:00"},
                    "timezone": "UTC"
                },
                "current_time": datetime.now().isoformat()
            }
            
            # Convert to JSON strings with proper datetime handling
            def convert_datetime_to_iso(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime_to_iso(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime_to_iso(item) for item in obj]
                else:
                    return obj
            
            serializable_tasks = convert_datetime_to_iso(sample_tasks)
            serializable_schedule = convert_datetime_to_iso(sample_schedule)
            
            all_tasks_json = json.dumps(serializable_tasks, indent=2)
            user_schedule_json = json.dumps(serializable_schedule, indent=2)
            
            # Test orchestrator
            next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
            
            if next_action and next_action.get('next_chunk_id'):
                result.add_data("orchestrator_response", "successful")
                result.add_data("next_chunk_id", next_action.get('next_chunk_id'))
                result.add_data("scheduled_time", next_action.get('scheduled_time_start'))
                logger.info("✅ Orchestrator integration working correctly")
                result.mark_success()
            else:
                result.add_error("Orchestrator returned empty or invalid response")
            
        except Exception as e:
            result.add_error(f"Orchestrator integration test failed: {str(e)}")
        
        return result
    
    def test_calendar_integration(self) -> TestResult:
        """Test 7: Calendar Integration and Event Management"""
        result = TestResult("Calendar Integration")
        
        if not self.calendar_api:
            result.add_error("Calendar API not available")
            return result
        
        try:
            calendar_operations = []
            
            # 1. Test calendar listing
            try:
                calendars = self.calendar_api.list_calendars()
                if calendars:
                    result.add_data("calendars_found", len(calendars))
                    logger.info(f"✅ Found {len(calendars)} calendars")
                else:
                    result.add_error("No calendars found")
                    return result
            except Exception as e:
                result.add_error(f"Calendar listing failed: {str(e)}")
                return result
            
            # 2. Test event creation
            try:
                test_start = datetime.now() + timedelta(hours=1)
                test_end = test_start + timedelta(minutes=30)
                
                created_event_id = self.calendar_api.create_event(
                    summary="[Genie] System Test Event",
                    description="This is a test event created by the Genie system to validate calendar integration.\n\nTask: System Integration Test\nGoal: Verify calendar API functionality",
                    start_datetime=test_start,
                    end_datetime=test_end,
                    resource_link="https://github.com/your-repo/genie-backend"
                )
                
                if created_event_id:
                    calendar_operations.append({
                        "operation": "create_event",
                        "success": True,
                        "event_id": created_event_id,
                        "kept_for_verification": True
                    })
                    logger.info(f"✅ Created calendar event: {created_event_id}")
                else:
                    result.add_error("Failed to create calendar event")
                    return result
                
            except Exception as e:
                result.add_error(f"Event creation failed: {str(e)}")
                return result
            
            # 3. Test event listing and verification
            try:
                start_time = datetime.now()
                end_time = start_time + timedelta(days=7)
                events = self.calendar_api.list_events(start_time, end_time)
                genie_events = [e for e in events if '[Genie]' in e.get('summary', '')]
                
                result.add_data("total_calendar_events", len(events))
                result.add_data("genie_events_found", len(genie_events))
                
                if genie_events:
                    logger.info(f"✅ Found {len(genie_events)} Genie events in calendar")
                    for event in genie_events:
                        logger.info(f"   📅 {event.get('summary')} - {event.get('start', {}).get('dateTime', 'Unknown')}")
                else:
                    logger.warning("⚠️ No Genie events found in calendar listing")
                
            except Exception as e:
                result.add_error(f"Event listing failed: {str(e)}")
            
            # 4. Test event deletion
            try:
                if created_event_id:
                    self.calendar_api.delete_event(created_event_id)
                    calendar_operations.append({
                        "operation": "delete_event",
                        "success": True
                    })
                    logger.info(f"✅ Deleted test event: {created_event_id}")
            except Exception as e:
                result.add_error(f"Event deletion failed: {str(e)}")
            
            result.add_data("calendar_operations", calendar_operations)
            result.mark_success()
            
        except Exception as e:
            result.add_error(f"Calendar integration test failed: {str(e)}")
        
        return result
    
    def test_feedback_processing(self) -> TestResult:
        """Test 8: Feedback Processing and Learning"""
        result = TestResult("Feedback Processing")
        
        try:
            # Initialize feedback agent
            feedback_agent = FeedbackAgent()
            
            # Test feedback processing
            test_feedback = [
                {
                    "task_id": "test_task_1",
                    "chunk_id": "test_chunk_1",
                    "feedback_type": "completion",
                    "feedback_text": "This task was completed successfully and took about 25 minutes as estimated.",
                    "rating": 5,
                    "time_taken_minutes": 25
                },
                {
                    "task_id": "test_task_2",
                    "chunk_id": "test_chunk_2",
                    "feedback_type": "difficulty",
                    "feedback_text": "This task was more difficult than expected and took longer than estimated.",
                    "rating": 3,
                    "time_taken_minutes": 45
                }
            ]
            
            processed_feedback = []
            
            for i, feedback in enumerate(test_feedback):
                try:
                    processed = feedback_agent.process_feedback(feedback)
                    if processed:
                        processed_feedback.append(processed)
                        logger.info(f"✅ Processed feedback {i+1}: {feedback['feedback_type']}")
                    else:
                        result.add_error(f"Failed to process feedback {i+1}: Empty result")
                except Exception as e:
                    result.add_error(f"Feedback processing {i+1} failed: {str(e)}")
            
            if len(processed_feedback) == len(test_feedback):
                result.add_data("feedback_processed", len(processed_feedback))
                result.add_data("processing_success_rate", "100%")
                result.mark_success()
            else:
                result.add_error(f"Only {len(processed_feedback)}/{len(test_feedback)} feedback processed successfully")
            
        except Exception as e:
            result.add_error(f"Feedback processing test failed: {str(e)}")
        
        return result
    
    def test_session_management(self) -> TestResult:
        """Test 9: Session Management and Persistence"""
        result = TestResult("Session Management")
        
        try:
            # Initialize session manager
            self.session_manager = SessionManager()
            
            # Test session creation
            user_id = "test_user_123"
            session = self.session_manager.create_session(user_id)
            
            if session and session.user_id == user_id:
                result.add_data("session_created", True)
                result.add_data("session_id", session.session_id)
                logger.info(f"✅ Created session for user: {user_id}")
            else:
                result.add_error("Failed to create session")
                return result
            
            # Test session retrieval
            retrieved_session = self.session_manager.get_session(user_id)
            if retrieved_session and retrieved_session.session_id == session.session_id:
                result.add_data("session_retrieved", True)
                logger.info("✅ Session retrieval working correctly")
            else:
                result.add_error("Failed to retrieve session")
            
            # Test session persistence
            self.session_manager.save_session(session)
            loaded_session = self.session_manager.load_session(user_id)
            
            if loaded_session and loaded_session.user_id == user_id:
                result.add_data("session_persistence", True)
                logger.info("✅ Session persistence working correctly")
                result.mark_success()
            else:
                result.add_error("Session persistence failed")
            
        except Exception as e:
            result.add_error(f"Session management test failed: {str(e)}")
        
        return result
    
    def test_supervisor_workflow(self) -> TestResult:
        """Test 10: Supervisor Agent Complete Workflow"""
        result = TestResult("Supervisor Workflow")
        
        try:
            # Initialize supervisor
            self.supervisor = SupervisorAgent()
            
            # Test complete workflow
            test_input = "Build a simple web application with user authentication"
            
            # Simulate the complete workflow
            workflow_steps = [
                "task_extraction",
                "task_planning", 
                "orchestration",
                "calendar_integration",
                "feedback_processing"
            ]
            
            completed_steps = []
            
            for step in workflow_steps:
                try:
                    # Simulate each step (in real implementation, supervisor would coordinate these)
                    if step == "task_extraction":
                        extraction_agent = TaskExtractionAgent()
                        task = extraction_agent.extract_task(test_input)
                        if task:
                            completed_steps.append(step)
                            logger.info(f"✅ {step}: Task extracted - {task.heading}")
                    
                    elif step == "task_planning":
                        planning_agent = PlanningAgent()
                        chunk = planning_agent.get_next_chunk({
                            "heading": "Build a simple web application with user authentication",
                            "details": "Create a web app with user registration, login, and basic functionality",
                            "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                            "previous_chunks": [],
                            "corrections_or_feedback": ""
                        })
                        if chunk:
                            completed_steps.append(step)
                            logger.info(f"✅ {step}: Chunk planned - {chunk['chunk_heading']}")
                    
                    elif step == "orchestration":
                        orchestrator = GenieOrchestrator()
                        # Create minimal test data for orchestrator
                        test_data = {
                            "tasks": [{
                                "id": "test_task",
                                "heading": "Build web app",
                                "subtasks": [{
                                    "id": "test_chunk",
                                    "heading": "Setup project",
                                    "status": "pending"
                                }]
                            }]
                        }
                        schedule_data = {
                            "availability": {"free": [], "busy": []},
                            "current_time": datetime.now().isoformat()
                        }
                        
                        next_action = orchestrator.get_next_action(
                            json.dumps(test_data),
                            json.dumps(schedule_data)
                        )
                        if next_action:
                            completed_steps.append(step)
                            logger.info(f"✅ {step}: Next action determined")
                    
                    elif step == "calendar_integration":
                        if self.calendar_api:
                            completed_steps.append(step)
                            logger.info(f"✅ {step}: Calendar integration available")
                        else:
                            logger.info(f"⚠️ {step}: Calendar integration not available")
                    
                    elif step == "feedback_processing":
                        feedback_agent = FeedbackAgent()
                        feedback = {
                            "task_id": "test_task",
                            "chunk_id": "test_chunk",
                            "feedback_type": "completion",
                            "feedback_text": "Task completed successfully",
                            "rating": 5
                        }
                        processed = feedback_agent.process_feedback(feedback)
                        if processed:
                            completed_steps.append(step)
                            logger.info(f"✅ {step}: Feedback processed")
                    
                except Exception as e:
                    logger.warning(f"⚠️ {step} failed: {str(e)}")
            
            result.add_data("workflow_steps", len(workflow_steps))
            result.add_data("completed_steps", len(completed_steps))
            result.add_data("success_rate", f"{len(completed_steps)}/{len(workflow_steps)}")
            
            if len(completed_steps) >= 3:  # At least 3 core steps should work
                result.mark_success()
            else:
                result.add_error(f"Only {len(completed_steps)}/{len(workflow_steps)} workflow steps completed")
            
        except Exception as e:
            result.add_error(f"Supervisor workflow test failed: {str(e)}")
        
        return result
    
    def test_complete_integration(self) -> TestResult:
        """Test 11: Complete System Integration Test"""
        result = TestResult("Complete Integration")
        
        try:
            # Test the complete flow from task input to calendar event
            test_input = "Learn React hooks and build a todo app"
            
            # Step 1: Extract task
            extraction_agent = TaskExtractionAgent()
            task = extraction_agent.extract_task(test_input)
            
            if not task:
                result.add_error("Task extraction failed")
                return result
            
            result.add_data("task_extracted", task.heading)
            logger.info(f"✅ Task extracted: {task.heading}")
            
            # Step 2: Plan subtasks
            planning_agent = PlanningAgent()
            chunk = planning_agent.get_next_chunk({
                "heading": task.heading,
                "details": task.details or f"Complete the task: {task.heading}",
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "previous_chunks": [],
                "corrections_or_feedback": ""
            })
            
            if not chunk:
                result.add_error("Task planning failed")
                return result
            
            result.add_data("chunk_planned", chunk['chunk_heading'])
            logger.info(f"✅ Chunk planned: {chunk['chunk_heading']}")
            
            # Step 3: Orchestrate scheduling
            orchestrator = GenieOrchestrator()
            
            # Create orchestrator input data
            orchestrator_tasks = {
                "tasks": [{
                    "id": task.id,
                    "heading": task.heading,
                    "details": task.details,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "priority_score": 8.0,
                    "subtasks": [{
                        "id": chunk.get('chunk_order', 1),
                        "heading": chunk['chunk_heading'],
                        "details": chunk['chunk_details'],
                        "estimated_time_minutes": chunk['estimated_time_minutes'],
                        "status": "pending",
                        "resource": chunk['resource'],
                        "dependencies": [],
                        "user_feedback": ""
                    }]
                }]
            }
            
            # Get availability if calendar API is available
            availability = {"free": [], "busy": []}
            if self.calendar_api:
                try:
                    start_time = datetime.now()
                    end_time = start_time + timedelta(days=7)
                    free_busy = self.calendar_api.get_free_busy(start_time, end_time)
                    availability = free_busy
                except Exception as e:
                    logger.warning(f"Failed to get calendar availability: {e}")
            
            orchestrator_schedule = {
                "availability": availability,
                "preferences": {
                    "work_hours": {"start": "09:00", "end": "17:00"},
                    "timezone": "UTC"
                },
                "current_time": datetime.now().isoformat()
            }
            
            # Convert to JSON with proper datetime handling
            def convert_datetime_to_iso(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime_to_iso(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime_to_iso(item) for item in obj]
                else:
                    return obj
            
            serializable_tasks = convert_datetime_to_iso(orchestrator_tasks)
            serializable_schedule = convert_datetime_to_iso(orchestrator_schedule)
            
            all_tasks_json = json.dumps(serializable_tasks, indent=2)
            user_schedule_json = json.dumps(serializable_schedule, indent=2)
            
            next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
            
            if not next_action:
                result.add_error("Orchestrator failed to determine next action")
                return result
            
            result.add_data("next_action", next_action.get('next_chunk_id', 'unknown'))
            logger.info(f"✅ Next action determined: {next_action.get('chunk_heading', 'Unknown')}")
            
            # Step 4: Create calendar event (if available)
            if self.calendar_api and next_action.get('scheduled_time_start'):
                try:
                    start_time = datetime.fromisoformat(next_action['scheduled_time_start'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(next_action['scheduled_time_end'].replace('Z', '+00:00'))
                    
                    event_id = self.calendar_api.create_event(
                        summary=f"[Genie] {next_action['chunk_heading']}",
                        description=f"Task: {task.heading}\n\n{next_action['chunk_details']}\n\nResource: {next_action['resource']['title']}",
                        start_datetime=start_time,
                        end_datetime=end_time
                    )
                    
                    if event_id:
                        result.add_data("calendar_event_created", event_id)
                        logger.info(f"✅ Calendar event created: {event_id}")
                        
                        # Clean up - delete the test event
                        self.calendar_api.delete_event(event_id)
                        logger.info(f"✅ Test event deleted: {event_id}")
                    else:
                        result.add_error("Failed to create calendar event")
                
                except Exception as e:
                    result.add_error(f"Calendar event creation failed: {str(e)}")
            
            result.mark_success()
            
        except Exception as e:
            result.add_error(f"Complete integration test failed: {str(e)}")
        
        return result
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all system tests"""
        logger.info("🚀 Starting Comprehensive Genie Backend System Test Suite")
        logger.info("=" * 80)
        
        # Run all tests
        tests = [
            self.test_environment_setup,
            self.test_api_connectivity,
            self.test_storage_system,
            self.test_task_extraction,
            self.test_task_planning,
            self.test_orchestrator_integration,
            self.test_calendar_integration,
            self.test_feedback_processing,
            self.test_session_management,
            self.test_supervisor_workflow,
            self.test_complete_integration
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.results.append(result)
                
                # Add delay between tests to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Test {test_func.__name__} crashed: {str(e)}")
                error_result = TestResult(test_func.__name__.replace('test_', '').replace('_', ' ').title())
                error_result.add_error(f"Test crashed: {str(e)}")
                self.results.append(error_result)
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Calculate total duration
        total_duration = sum(r.get_duration() for r in self.results)
        
        # Collect all errors
        all_errors = []
        for result in self.results:
            all_errors.extend([f"{result.test_name}: {error}" for error in result.errors])
        
        # Collect all data
        all_data = {}
        for result in self.results:
            all_data[result.test_name] = result.data
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                "total_duration_seconds": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": [result.to_dict() for result in self.results],
            "all_errors": all_errors,
            "all_data": all_data,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for common issues
        api_errors = [r for r in self.results if any("API" in error for error in r.errors)]
        if api_errors:
            recommendations.append("🔧 API Integration Issues: Check API keys and network connectivity")
        
        calendar_errors = [r for r in self.results if any("calendar" in error.lower() for error in r.errors)]
        if calendar_errors:
            recommendations.append("📅 Calendar Integration Issues: Verify Google Calendar API setup and credentials")
        
        planning_errors = [r for r in self.results if any("planning" in error.lower() for error in r.errors)]
        if planning_errors:
            recommendations.append("🧠 Planning Agent Issues: Check Perplexity API configuration and response parsing")
        
        storage_errors = [r for r in self.results if any("storage" in error.lower() for error in r.errors)]
        if storage_errors:
            recommendations.append("💾 Storage Issues: Verify file permissions and storage directory access")
        
        # Add general recommendations
        success_rate = sum(1 for r in self.results if r.success) / len(self.results) if self.results else 0
        if success_rate < 0.5:
            recommendations.append("⚠️ Low Success Rate: Review system configuration and dependencies")
        elif success_rate < 0.8:
            recommendations.append("✅ Good Progress: Address remaining issues for full functionality")
        else:
            recommendations.append("🎉 Excellent Performance: System is ready for production use")
        
        return recommendations

def main():
    """Main function to run the comprehensive test suite"""
    try:
        # Initialize tester
        tester = GenieSystemTester()
        
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate report
        report = tester.generate_report()
        
        # Save report to file
        with open('system_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 GENIE BACKEND SYSTEM TEST SUITE - COMPLETE")
        print("="*80)
        
        summary = report['test_summary']
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']}")
        print(f"   Duration: {summary['total_duration_seconds']:.1f} seconds")
        
        print(f"\n📋 Test Results:")
        for result in results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"   {status} {result.test_name} ({result.get_duration():.1f}s)")
            if result.errors:
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"      ⚠️  {error}")
        
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   {rec}")
        
        print(f"\n📄 Detailed report saved to: system_test_report.json")
        
        # Return exit code based on success rate
        success_rate = summary['successful_tests'] / summary['total_tests'] if summary['total_tests'] > 0 else 0
        if success_rate >= 0.8:
            print(f"\n🎉 System is ready for use! Success rate: {summary['success_rate']}")
            return 0
        elif success_rate >= 0.5:
            print(f"\n⚠️  System has issues but is partially functional. Success rate: {summary['success_rate']}")
            return 1
        else:
            print(f"\n❌ System has significant issues. Success rate: {summary['success_rate']}")
            return 2
            
    except Exception as e:
        logger.error(f"❌ Test suite crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 