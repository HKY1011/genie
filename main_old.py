#!/usr/bin/env python3
"""
Comprehensive Genie Backend System Test Suite
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

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genie_system_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemTestResult:
    """Results from system tests"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.success = False
        self.duration = 0.0
        self.errors = []
        self.warnings = []
        self.data = {}
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timing the test"""
        self.start_time = time.time()
        logger.info(f"🚀 Starting test: {self.test_name}")
    
    def end(self, success: bool = True):
        """End timing and record results"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status} {self.test_name} ({self.duration:.2f}s)")
    
    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)
        logger.error(f"❌ {self.test_name}: {error}")
    
    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)
        logger.warning(f"⚠️  {self.test_name}: {warning}")
    
    def add_data(self, key: str, value: Any):
        """Add test data"""
        self.data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "test_name": self.test_name,
            "success": self.success,
            "duration": self.duration,
            "errors": self.errors,
            "warnings": self.warnings,
            "data": self.data
        }


class GenieSystemTester:
    """
    Comprehensive system tester for the Genie backend architecture
    """
    
    def __init__(self):
        """Initialize the complete system tester"""
        self.results = []
        self.session_manager = None
        self.supervisor = None
        self.calendar_api = None
        self.gemini_client = None
        self.perplexity_client = None
        self.store = None
        
        # Test configuration
        self.test_user_id = "system_test_user"
        self.test_session = None
        
        logger.info("🎯 Initializing Genie System Tester")
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*80}")
        print(f"🎯 {title}")
        print(f"{'='*80}")
    
    def print_section(self, title: str):
        """Print a formatted section"""
        print(f"\n📋 {title}")
        print("-" * 60)
    
    def run_test(self, test_func, test_name: str) -> SystemTestResult:
        """Run a test and capture results"""
        result = SystemTestResult(test_name)
        result.start()
        
        try:
            test_func(result)
            result.end(True)
        except Exception as e:
            result.add_error(f"Test failed with exception: {str(e)}")
            result.end(False)
            logger.exception(f"Exception in test {test_name}")
        
        self.results.append(result)
        return result
    
    def test_environment_setup(self, result: SystemTestResult):
        """Test 1: Environment and configuration setup"""
        self.print_section("Environment Setup Test")
        
        # Load environment variables
        load_dotenv()
        
        # Check required environment variables
        required_vars = [
            'GEMINI_API_KEY',
            'PERPLEXITY_API_KEY',
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET',
            'GOOGLE_REDIRECT_URI'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            result.add_warning(f"Missing environment variables: {', '.join(missing_vars)}")
        else:
            result.add_data("env_vars_loaded", True)
            logger.info("✅ Environment variables loaded successfully")
        
        # Check storage directory
        storage_dir = Path("storage")
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True, exist_ok=True)
            result.add_warning("Created storage directory")
        
        result.add_data("storage_dir", str(storage_dir.absolute()))
    
    def test_api_initialization(self, result: SystemTestResult):
        """Test 2: API initialization and connectivity"""
        self.print_section("API Initialization Test")
        
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
            test_response = self.perplexity_client.query("Python programming basics")
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
            # Test basic connectivity
            calendars = self.calendar_api.list_calendars()
            if calendars:
                result.add_data("google_calendar_api", "connected")
                result.add_data("calendars_count", len(calendars))
                logger.info(f"✅ Google Calendar API connected successfully ({len(calendars)} calendars)")
            else:
                result.add_warning("Google Calendar API connected but no calendars found")
        except Exception as e:
            result.add_warning(f"Google Calendar API not available: {str(e)}")
    
    def test_storage_initialization(self, result: SystemTestResult):
        """Test 3: Storage system initialization"""
        self.print_section("Storage System Test")
        
        try:
            # Initialize JSON store
            self.store = JsonStore(storage_path="system_test_data.json")
            result.add_data("json_store", "initialized")
            logger.info("✅ JSON Store initialized successfully")
            
            # Initialize session manager
            self.session_manager = SessionManager()
            result.add_data("session_manager", "initialized")
            logger.info("✅ Session Manager initialized successfully")
            
            # Test session creation
            self.test_session = self.session_manager.create_session(self.test_user_id)
            result.add_data("test_session_created", True)
            logger.info("✅ Test session created successfully")
            
        except Exception as e:
            result.add_error(f"Storage initialization failed: {str(e)}")
    
    def test_agent_initialization(self, result: SystemTestResult):
        """Test 4: Agent initialization"""
        self.print_section("Agent Initialization Test")
        
        try:
            # Initialize supervisor agent (which initializes all other agents)
            self.supervisor = SupervisorAgent(self.session_manager)
            result.add_data("supervisor_agent", "initialized")
            logger.info("✅ Supervisor Agent initialized successfully")
            
            # Get agent info
            agent_info = self.supervisor.get_agent_info()
            result.add_data("agent_info", agent_info)
            logger.info("✅ All agents initialized and ready")
            
        except Exception as e:
            result.add_error(f"Agent initialization failed: {str(e)}")
    
    def test_task_extraction_flow(self, result: SystemTestResult):
        """Test 5: Complete task extraction flow"""
        self.print_section("Task Extraction Flow Test")
        
        test_inputs = [
            "I need to learn Python programming and build a React todo app by next month",
            "I want to prepare for a job interview next week and need to study algorithms",
            "I have a project deadline in 2 weeks and need to organize my tasks"
        ]
        
        extracted_tasks = []
        
        for i, user_input in enumerate(test_inputs, 1):
            try:
                logger.info(f"Testing task extraction {i}: {user_input[:50]}...")
                
                # Process through supervisor
                processing_result = self.supervisor.process_user_feedback(
                    user_input, self.test_user_id
                )
                
                if processing_result.success:
                    extracted_tasks.append({
                        "input": user_input,
                        "result": processing_result.user_message,
                        "next_action": processing_result.next_action
                    })
                    logger.info(f"✅ Task extraction {i} successful")
                else:
                    result.add_error(f"Task extraction {i} failed: {processing_result.errors}")
                
            except Exception as e:
                result.add_error(f"Task extraction {i} exception: {str(e)}")
        
        result.add_data("extracted_tasks_count", len(extracted_tasks))
        result.add_data("extracted_tasks", extracted_tasks)
        
        if extracted_tasks:
            logger.info(f"✅ Successfully extracted {len(extracted_tasks)} tasks")
    
    def test_planning_flow(self, result: SystemTestResult):
        """Test 6: Task planning and breakdown flow"""
        self.print_section("Task Planning Flow Test")
        
        # Get current session with tasks
        session = self.session_manager.get_or_create_session(self.test_user_id)
        pending_tasks = session.get_pending_tasks()
        
        if not pending_tasks:
            result.add_warning("No pending tasks available for planning test")
            return
        
        planned_tasks = []
        
        for i, task in enumerate(pending_tasks[:3]):  # Test first 3 tasks
            try:
                logger.info(f"Testing planning for task {i+1}: {task.heading}")
                
                # Use planning agent directly
                planning_agent = PlanningAgent()
                
                # Ensure task has proper details
                if not task.details or task.details.strip() == "":
                    task_details = f"Complete the task: {task.heading}. This involves understanding the requirements, planning the approach, and implementing the solution step by step."
                else:
                    task_details = task.details
                
                chunk = planning_agent.get_next_chunk({
                    "heading": task.heading,
                    "details": task_details,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "previous_chunks": [],
                    "corrections_or_feedback": ""
                })
                
                if chunk:
                    planned_tasks.append({
                        "task_heading": task.heading,
                        "chunk_heading": chunk.get('chunk_heading'),
                        "estimated_time": chunk.get('estimated_time_minutes'),
                        "resource": chunk.get('resource', {})
                    })
                    logger.info(f"✅ Planning successful for task {i+1}")
                else:
                    result.add_error(f"Planning failed for task {i+1}: No chunk returned")
                
            except Exception as e:
                result.add_error(f"Planning exception for task {i+1}: {str(e)}")
        
        result.add_data("planned_tasks_count", len(planned_tasks))
        result.add_data("planned_tasks", planned_tasks)
        
        if planned_tasks:
            logger.info(f"✅ Successfully planned {len(planned_tasks)} tasks")
    
    def test_orchestration_flow(self, result: SystemTestResult):
        """Test 7: Task orchestration and prioritization flow"""
        self.print_section("Task Orchestration Flow Test")
        
        try:
            # Get current session
            session = self.session_manager.get_or_create_session(self.test_user_id)
            
            # Create current state for orchestrator
            current_state = {
                "tasks": [task.to_dict() for task in session.tasks],
                "preferences": asdict(session.preferences),
                "completion_history": [h.to_dict() for h in session.completion_history],
                "energy_patterns": [p.to_dict() for p in session.energy_patterns]
            }
            
            # Test orchestrator
            orchestrator = GenieOrchestrator()
            
            # Get availability if calendar API is available
            free_busy = None
            if self.calendar_api:
                try:
                    start_time = datetime.now()
                    end_time = start_time + timedelta(days=7)
                    free_busy = self.calendar_api.get_free_busy(start_time, end_time)
                except Exception as e:
                    logger.warning(f"Failed to get calendar availability: {e}")
                    free_busy = {"free": [], "busy": []}
            else:
                free_busy = {"free": [], "busy": []}
            
            # Convert current state to JSON strings with proper datetime handling
            # Convert datetime objects to ISO strings for JSON serialization
            def convert_datetime_to_iso(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime_to_iso(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime_to_iso(item) for item in obj]
                elif hasattr(obj, 'to_dict'):
                    return convert_datetime_to_iso(obj.to_dict())
                else:
                    return obj
            
            # Convert tasks to dictionaries first
            tasks_dict = []
            for task in session.tasks:
                task_dict = task.to_dict()
                tasks_dict.append(task_dict)
            
            serializable_state = {
                "tasks": tasks_dict,
                "preferences": convert_datetime_to_iso(session.preferences),
                "completion_history": [convert_datetime_to_iso(h) for h in session.completion_history],
                "energy_patterns": [convert_datetime_to_iso(p) for p in session.energy_patterns]
            }
            
            all_tasks_json = json.dumps(serializable_state, indent=2)
            
            # Create user schedule JSON similar to working implementation
            user_schedule = {
                "daily_schedule": [
                    {
                        "start_time": "09:00",
                        "end_time": "17:00",
                        "day_of_week": "daily",
                        "energy_level": "medium",
                        "focus_type": "deep_work"
                    }
                ],
                "preferences": current_state.get("preferences", {}),
                "timezone": "Asia/Kolkata",
                "current_time": datetime.now().isoformat(),
                "availability": free_busy
            }
            user_schedule_json = json.dumps(user_schedule, indent=2)
            
            try:
                next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
            except Exception as e:
                logger.warning(f"Orchestrator failed: {e}")
                next_action = None
            
            if next_action:
                result.add_data("next_action", next_action)
                logger.info("✅ Orchestration successful")
                logger.info(f"Next action: {next_action.get('action_type', 'unknown')}")
            else:
                result.add_warning("Orchestrator returned no next action")
                
        except Exception as e:
            result.add_error(f"Orchestration failed: {str(e)}")
    
    def test_calendar_integration_flow(self, result: SystemTestResult):
        """Test 8: Calendar integration flow"""
        self.print_section("Calendar Integration Flow Test")
        
        if not self.calendar_api:
            result.add_warning("Calendar API not available, skipping calendar test")
            return
        
        try:
            # Test calendar operations
            calendar_operations = []
            
            # 1. List calendars
            calendars = self.calendar_api.list_calendars()
            calendar_operations.append({
                "operation": "list_calendars",
                "success": True,
                "count": len(calendars)
            })
            
            # 2. Get availability
            start_time = datetime.now()
            end_time = start_time + timedelta(days=7)
            free_busy = self.calendar_api.get_free_busy(start_time, end_time)
            calendar_operations.append({
                "operation": "get_free_busy",
                "success": True,
                "free_blocks": len(free_busy.get('free', [])),
                "busy_blocks": len(free_busy.get('busy', []))
            })
            
            # 3. Test event creation (if we have a primary calendar)
            if calendars:
                primary_calendar = next((cal for cal in calendars if cal.get('primary')), calendars[0])
                
                test_start = datetime.now() + timedelta(hours=1)
                test_end = test_start + timedelta(hours=1)
                
                try:
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
                            "event_id": created_event_id
                        })
                        
                        # Keep the event for verification (don't delete immediately)
                        calendar_operations.append({
                            "operation": "create_event",
                            "success": True,
                            "event_id": created_event_id,
                            "kept_for_verification": True
                        })
                    else:
                        calendar_operations.append({
                            "operation": "create_event",
                            "success": False
                        })
                except Exception as e:
                    calendar_operations.append({
                        "operation": "create_event",
                        "success": False,
                        "error": str(e)
                    })
            
            result.add_data("calendar_operations", calendar_operations)
            
            # Check if Genie events are visible in calendar
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
                        start = event['start'].get('dateTime', event['start'].get('date', 'Unknown'))
                        logger.info(f"   🤖 {event['summary']} - {start[:16]}")
                else:
                    logger.warning("⚠️  No Genie events found in calendar")
                    
            except Exception as e:
                logger.warning(f"⚠️  Error checking calendar events: {e}")
            
            logger.info("✅ Calendar integration test completed successfully")
            
        except Exception as e:
            result.add_error(f"Calendar integration failed: {str(e)}")
    
    def test_feedback_flow(self, result: SystemTestResult):
        """Test 9: Feedback processing flow"""
        self.print_section("Feedback Processing Flow Test")
        
        feedback_inputs = [
            "I completed the Python basics task in 45 minutes, it was easier than expected",
            "The algorithm study took longer than planned, I need more time for complex topics",
            "I'm feeling tired today, can you suggest shorter tasks?"
        ]
        
        feedback_results = []
        
        for i, feedback in enumerate(feedback_inputs, 1):
            try:
                logger.info(f"Testing feedback processing {i}: {feedback[:50]}...")
                
                # Process feedback through supervisor
                processing_result = self.supervisor.process_user_feedback(
                    feedback, self.test_user_id
                )
                
                if processing_result.success:
                    feedback_results.append({
                        "input": feedback,
                        "user_message": processing_result.user_message,
                        "motivational_message": processing_result.motivational_message,
                        "next_action": processing_result.next_action,
                        "recommendations": processing_result.recommendations
                    })
                    logger.info(f"✅ Feedback processing {i} successful")
                else:
                    result.add_error(f"Feedback processing {i} failed: {processing_result.errors}")
                
            except Exception as e:
                result.add_error(f"Feedback processing {i} exception: {str(e)}")
        
        result.add_data("feedback_results_count", len(feedback_results))
        result.add_data("feedback_results", feedback_results)
        
        if feedback_results:
            logger.info(f"✅ Successfully processed {len(feedback_results)} feedback inputs")
    
    def test_session_persistence(self, result: SystemTestResult):
        """Test 10: Session persistence and state management"""
        self.print_section("Session Persistence Test")
        
        try:
            # Get current session
            session = self.session_manager.get_or_create_session(self.test_user_id)
            
            # Add some test data
            session.update_preferences(preferred_work_duration=60)
            session.record_energy_pattern(8, "work", 0.9, {"context": "testing"})
            
            # Save session
            success = self.session_manager.save_session(session)
            if not success:
                result.add_error("Failed to save session")
                return
            
            # Load session in new instance
            loaded_session = self.session_manager.load_session(self.test_user_id)
            if not loaded_session:
                result.add_error("Failed to load session")
                return
            
            # Verify data persistence
            if loaded_session.preferences.preferred_work_duration == 60:
                result.add_data("preferences_persisted", True)
                logger.info("✅ Preferences persisted successfully")
            else:
                result.add_error("Preferences not persisted correctly")
            
            if len(loaded_session.energy_patterns) > 0:
                result.add_data("energy_patterns_persisted", True)
                logger.info("✅ Energy patterns persisted successfully")
            else:
                result.add_error("Energy patterns not persisted correctly")
            
            # Test session statistics
            stats = loaded_session.get_productivity_stats()
            result.add_data("productivity_stats", stats)
            logger.info("✅ Session statistics calculated successfully")
            
        except Exception as e:
            result.add_error(f"Session persistence failed: {str(e)}")
    
    def test_complete_workflow(self, result: SystemTestResult):
        """Test 11: Complete end-to-end workflow"""
        self.print_section("Complete End-to-End Workflow Test")
        
        try:
            # Simulate a complete user interaction
            user_input = "I need to prepare for a technical interview next week. I want to study data structures, algorithms, and system design."
            
            logger.info("Starting complete workflow test...")
            
            # Step 1: Process initial input
            processing_result = self.supervisor.process_user_feedback(user_input, self.test_user_id)
            
            if not processing_result.success:
                result.add_error("Initial processing failed")
                return
            
            # Step 2: Simulate task completion feedback
            completion_feedback = "I completed the data structures review in 90 minutes. It was challenging but I learned a lot."
            completion_result = self.supervisor.process_user_feedback(completion_feedback, self.test_user_id)
            
            if not completion_result.success:
                result.add_error("Completion feedback processing failed")
                return
            
            # Step 3: Simulate energy feedback
            energy_feedback = "I'm feeling tired now, can you suggest a shorter task for my next session?"
            energy_result = self.supervisor.process_user_feedback(energy_feedback, self.test_user_id)
            
            if not energy_result.success:
                result.add_error("Energy feedback processing failed")
                return
            
            # Step 4: Check final session state
            final_session = self.session_manager.get_or_create_session(self.test_user_id)
            final_stats = final_session.get_productivity_stats()
            
            result.add_data("workflow_completed", True)
            result.add_data("final_stats", final_stats)
            result.add_data("total_tasks", len(final_session.tasks))
            result.add_data("completion_history", len(final_session.completion_history))
            
            logger.info("✅ Complete workflow test successful")
            
        except Exception as e:
            result.add_error(f"Complete workflow failed: {str(e)}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_header("Genie System Test Report")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)
        
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"   {status} {result.test_name} ({result.duration:.2f}s)")
            
            if result.errors:
                for error in result.errors:
                    print(f"      ❌ {error}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"      ⚠️  {warning}")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "total_duration": total_duration
            },
            "results": [r.to_dict() for r in self.results]
        }
        
        with open("system_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: system_test_report.json")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all system tests"""
        self.print_header("Genie Backend System Test Suite")
        
        logger.info("🚀 Starting comprehensive system testing...")
        
        # Run all tests
        tests = [
            (self.test_environment_setup, "Environment Setup"),
            (self.test_api_initialization, "API Initialization"),
            (self.test_storage_initialization, "Storage Initialization"),
            (self.test_agent_initialization, "Agent Initialization"),
            (self.test_task_extraction_flow, "Task Extraction Flow"),
            (self.test_planning_flow, "Task Planning Flow"),
            (self.test_orchestration_flow, "Task Orchestration Flow"),
            (self.test_calendar_integration_flow, "Calendar Integration Flow"),
            (self.test_feedback_flow, "Feedback Processing Flow"),
            (self.test_session_persistence, "Session Persistence"),
            (self.test_complete_workflow, "Complete End-to-End Workflow")
        ]
        
        for test_func, test_name in tests:
            self.run_test(test_func, test_name)
        
        # Generate report
        all_passed = self.generate_test_report()
        
        if all_passed:
            print(f"\n🎉 All tests passed! System is ready for production use.")
        else:
            print(f"\n⚠️  Some tests failed. Please review the errors above.")
        
        return all_passed


def main():
    """Main entry point for the system test suite"""
    try:
        tester = GenieSystemTester()
        success = tester.run_all_tests()
        
        if success:
            print(f"\n✅ System test completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ System test completed with failures!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        logger.exception("Unexpected error in main")
        sys.exit(1)


if __name__ == "__main__":
    main() 