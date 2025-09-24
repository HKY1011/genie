#!/usr/bin/env python3
"""
Test script for GenieOrchestrator
Tests the GenieOrchestrator with sample tasks and schedules.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.genieorchestrator_agent import GenieOrchestrator, GenieOrchestratorError
from dotenv import load_dotenv


def create_sample_tasks_json():
    """Create sample tasks JSON for testing"""
    sample_tasks = {
        "tasks": [
            {
                "id": "task_1",
                "heading": "Learn Python Programming",
                "details": "Master Python fundamentals to build web applications and data analysis projects",
                "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "priority_score": 8.5,
                "subtasks": [
                    {
                        "id": "chunk_1_1",
                        "heading": "Set up Python development environment",
                        "details": "Install Python, set up IDE, and write first Hello World program",
                        "estimated_time_minutes": 30,
                        "status": "done",
                        "resource": {
                            "title": "Python Installation Guide",
                            "url": "https://docs.python.org/3/using/index.html",
                            "type": "documentation",
                            "focus_section": "Installation section",
                            "paid": False
                        },
                        "dependencies": [],
                        "user_feedback": ""
                    },
                    {
                        "id": "chunk_1_2",
                        "heading": "Learn Python basics and data types",
                        "details": "Understand variables, strings, numbers, lists, and basic operations",
                        "estimated_time_minutes": 45,
                        "status": "pending",
                        "resource": {
                            "title": "Python Tutorial - Basic Types",
                            "url": "https://docs.python.org/3/tutorial/introduction.html",
                            "type": "documentation",
                            "focus_section": "Numbers, Strings, Lists sections",
                            "paid": False
                        },
                        "dependencies": ["chunk_1_1"],
                        "user_feedback": ""
                    },
                    {
                        "id": "chunk_1_3",
                        "heading": "Practice with functions and control flow",
                        "details": "Write functions, use if/else statements, and loops",
                        "estimated_time_minutes": 40,
                        "status": "pending",
                        "resource": {
                            "title": "Python Functions Tutorial",
                            "url": "https://docs.python.org/3/tutorial/controlflow.html",
                            "type": "documentation",
                            "focus_section": "Defining Functions and More Control Flow Tools",
                            "paid": False
                        },
                        "dependencies": ["chunk_1_2"],
                        "user_feedback": ""
                    }
                ]
            },
            {
                "id": "task_2",
                "heading": "Build React Todo App",
                "details": "Create a modern todo application with React hooks and local storage",
                "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "priority_score": 7.0,
                "subtasks": [
                    {
                        "id": "chunk_2_1",
                        "heading": "Set up React development environment",
                        "details": "Install Node.js, create React app, and understand project structure",
                        "estimated_time_minutes": 25,
                        "status": "done",
                        "resource": {
                            "title": "Create React App Documentation",
                            "url": "https://create-react-app.dev/docs/getting-started",
                            "type": "documentation",
                            "focus_section": "Getting Started section",
                            "paid": False
                        },
                        "dependencies": [],
                        "user_feedback": "Setup was easier than expected"
                    },
                    {
                        "id": "chunk_2_2",
                        "heading": "Create basic todo component structure",
                        "details": "Build the main TodoApp component with useState hook for todo list",
                        "estimated_time_minutes": 35,
                        "status": "pending",
                        "resource": {
                            "title": "React Hooks Tutorial",
                            "url": "https://react.dev/learn/hooks-overview",
                            "type": "documentation",
                            "focus_section": "useState Hook section",
                            "paid": False
                        },
                        "dependencies": ["chunk_2_1"],
                        "user_feedback": ""
                    },
                    {
                        "id": "chunk_2_3",
                        "heading": "Add todo functionality (add, edit, delete)",
                        "details": "Implement CRUD operations for todo items with proper state management",
                        "estimated_time_minutes": 45,
                        "status": "pending",
                        "resource": {
                            "title": "React State Management",
                            "url": "https://react.dev/learn/managing-state",
                            "type": "documentation",
                            "focus_section": "State as a Snapshot and Updating Objects in State",
                            "paid": False
                        },
                        "dependencies": ["chunk_2_2"],
                        "user_feedback": ""
                    }
                ]
            },
            {
                "id": "task_3",
                "heading": "Learn Machine Learning Basics",
                "details": "Understand fundamental ML concepts and implement basic algorithms",
                "deadline": (datetime.utcnow() + timedelta(days=21)).isoformat(),
                "priority_score": 6.5,
                "subtasks": [
                    {
                        "id": "chunk_3_1",
                        "heading": "Understand ML fundamentals and types",
                        "details": "Learn about supervised vs unsupervised learning, classification vs regression",
                        "estimated_time_minutes": 40,
                        "status": "pending",
                        "resource": {
                            "title": "Machine Learning Basics",
                            "url": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html",
                            "type": "documentation",
                            "focus_section": "Machine Learning: the problem setting",
                            "paid": False
                        },
                        "dependencies": [],
                        "user_feedback": ""
                    },
                    {
                        "id": "chunk_3_2",
                        "heading": "Install and explore scikit-learn",
                        "details": "Set up scikit-learn library and understand its basic structure",
                        "estimated_time_minutes": 30,
                        "status": "pending",
                        "resource": {
                            "title": "Scikit-learn Installation",
                            "url": "https://scikit-learn.org/stable/install.html",
                            "type": "documentation",
                            "focus_section": "Installation instructions",
                            "paid": False
                        },
                        "dependencies": ["chunk_3_1"],
                        "user_feedback": ""
                    }
                ]
            }
        ]
    }
    
    return json.dumps(sample_tasks, indent=2)


def create_sample_schedule_json():
    """Create sample user schedule JSON for testing"""
    sample_schedule = {
        "daily_schedule": [
            {
                "start_time": "09:00",
                "end_time": "11:00",
                "day_of_week": "daily",
                "energy_level": "high",
                "focus_type": "deep_work"
            },
            {
                "start_time": "11:00",
                "end_time": "12:00",
                "day_of_week": "daily",
                "energy_level": "medium",
                "focus_type": "light_work"
            },
            {
                "start_time": "14:00",
                "end_time": "16:00",
                "day_of_week": "daily",
                "energy_level": "high",
                "focus_type": "deep_work"
            },
            {
                "start_time": "16:00",
                "end_time": "17:00",
                "day_of_week": "daily",
                "energy_level": "low",
                "focus_type": "light_work"
            }
        ],
        "preferences": {
            "preferred_work_duration": 45,
            "max_work_duration": 90,
            "break_duration": 15,
            "energy_peak_hours": ["09:00-11:00", "14:00-16:00"],
            "avoid_work_hours": ["12:00-13:00", "18:00-20:00"]
        },
        "timezone": "UTC"
    }
    
    return json.dumps(sample_schedule, indent=2)


def test_genieorchestrator():
    """Test the GenieOrchestrator with sample data"""
    print("🎯 GenieOrchestrator Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        orchestrator = GenieOrchestrator()
        print("✅ GenieOrchestrator initialized successfully")
        
        # Get agent info
        info = orchestrator.get_agent_info()
        print(f"📊 Agent Info: {info}")
        
    except GenieOrchestratorError as e:
        print(f"❌ Failed to initialize GenieOrchestrator: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Create sample data
    print("\n📋 Creating sample tasks and schedule...")
    all_tasks_json = create_sample_tasks_json()
    user_schedule_json = create_sample_schedule_json()
    
    print(f"✅ Created {len(json.loads(all_tasks_json)['tasks'])} sample tasks")
    print(f"✅ Created schedule with {len(json.loads(user_schedule_json)['daily_schedule'])} time blocks")
    
    # Test the orchestrator
    print("\n🔍 Testing GenieOrchestrator...")
    try:
        result = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
        
        print("\n🎯 Next Action Recommended:")
        print("-" * 40)
        print(f"Task: {result['task_id']}")
        print(f"Chunk: {result['chunk_heading']}")
        print(f"Time: {result['estimated_time_minutes']} minutes")
        print(f"Priority Score: {result['priority_score']}")
        print(f"Scheduled: {result['scheduled_time_start']} to {result['scheduled_time_end']}")
        
        print(f"\n📚 Resource:")
        print(f"  Title: {result['resource']['title']}")
        print(f"  Type: {result['resource']['type']}")
        print(f"  URL: {result['resource']['url']}")
        print(f"  Focus: {result['resource']['focus_section']}")
        print(f"  Paid: {result['resource']['paid']}")
        
        print(f"\n📖 Instructions:")
        print(f"  {result['chunk_details']}")
        
        print(f"\n📊 Progress Summary:")
        print(f"  Completed: {result['progress_summary']['completed_chunks']}/{result['progress_summary']['total_chunks']}")
        
        if result.get('warnings'):
            print(f"\n⚠️  Warnings: {result['warnings']}")
        
        if result['progress_summary'].get('upcoming_deadlines_warning'):
            print(f"\n⏰ Deadline Warning: {result['progress_summary']['upcoming_deadlines_warning']}")
        
        return True
        
    except GenieOrchestratorError as e:
        print(f"❌ GenieOrchestrator error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🔧 Testing Error Handling...")
    
    try:
        orchestrator = GenieOrchestrator()
    except GenieOrchestratorError:
        print("⚠️  Skipping error handling tests - orchestrator not initialized")
        return True
    
    # Test invalid JSON
    try:
        orchestrator.get_next_action("invalid json", "also invalid")
        print("❌ Expected error but got success")
        return False
    except GenieOrchestratorError as e:
        if "Invalid JSON" in str(e):
            print("✅ Correctly caught invalid JSON error")
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    
    # Test empty JSON
    try:
        orchestrator.get_next_action("", "")
        print("❌ Expected error but got success")
        return False
    except GenieOrchestratorError as e:
        if "cannot be empty" in str(e):
            print("✅ Correctly caught empty input error")
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return True


def main():
    """Run all tests"""
    print("🎯 GenieOrchestrator Test Suite")
    print("=" * 50)
    
    # Test main functionality
    main_success = test_genieorchestrator()
    
    # Test error handling
    error_success = test_error_handling()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  Main Functionality: {'✅ Passed' if main_success else '❌ Failed'}")
    print(f"  Error Handling: {'✅ Passed' if error_success else '❌ Failed'}")
    
    if main_success and error_success:
        print("\n🎉 All tests passed! GenieOrchestrator is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main()) 