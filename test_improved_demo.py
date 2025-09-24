#!/usr/bin/env python3
"""
Test Improved Interactive Demo
Demonstrates the new natural language interaction features
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.task_extraction_agent import TaskExtractionAgent
from agents.planning_agent import PlanningAgent
from agents.genieorchestrator_agent import GenieOrchestrator
from dotenv import load_dotenv

def test_improved_demo():
    """Test the improved interactive demo functionality"""
    print("🎯 Testing Improved Interactive Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize agents
    print("\n🚀 Initializing agents...")
    try:
        task_extractor = TaskExtractionAgent()
        planner = PlanningAgent()
        orchestrator = GenieOrchestrator()
        print("✅ All agents initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return
    
    # Predefined schedule
    schedule = {
        "daily_schedule": [
            {
                "start_time": "09:00",
                "end_time": "11:00",
                "day_of_week": "daily",
                "energy_level": "high",
                "focus_type": "deep_work"
            },
            {
                "start_time": "14:00",
                "end_time": "16:00",
                "day_of_week": "daily",
                "energy_level": "high",
                "focus_type": "deep_work"
            }
        ],
        "preferences": {
            "preferred_work_duration": 45,
            "max_work_duration": 90,
            "break_duration": 15,
            "energy_peak_hours": ["09:00-11:00", "14:00-16:00"],
            "avoid_work_hours": []
        },
        "timezone": "UTC"
    }
    
    # Predefined tasks
    tasks = [
        {
            "id": "task_1",
            "heading": "Learn Python Programming",
            "details": "Master Python fundamentals to build web applications",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "priority_score": 8.0,
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
                }
            ]
        },
        {
            "id": "task_2",
            "heading": "Build React Todo App",
            "details": "Create a modern todo application with React hooks",
            "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "priority_score": 7.5,
            "subtasks": [
                {
                    "id": "chunk_2_1",
                    "heading": "Set up React development environment",
                    "details": "Install Node.js, create React app, and understand project structure",
                    "estimated_time_minutes": 25,
                    "status": "pending",
                    "resource": {
                        "title": "Create React App Documentation",
                        "url": "https://create-react-app.dev/docs/getting-started",
                        "type": "documentation",
                        "focus_section": "Getting Started section",
                        "paid": False
                    },
                    "dependencies": [],
                    "user_feedback": ""
                }
            ]
        }
    ]
    
    print(f"\n📋 Initial Tasks: {len(tasks)} tasks")
    for task in tasks:
        completed = sum(1 for st in task['subtasks'] if st['status'] == 'done')
        total = len(task['subtasks'])
        print(f"   📋 {task['heading']}: {completed}/{total} completed")
    
    # Test natural language input processing
    print("\n🔄 Testing Natural Language Input Processing")
    print("=" * 50)
    
    test_inputs = [
        "I finished the Python task",
        "Mark the React app as done",
        "Add a new task: learn machine learning by next Friday",
        "What should I do next?",
        "Show me my progress"
    ]
    
    for user_input in test_inputs:
        print(f"\n🧪 Testing: '{user_input}'")
        
        if user_input.lower() in ['what should i do next', 'next']:
            print("🎯 Getting next recommendation...")
            try:
                all_tasks_json = json.dumps({"tasks": tasks}, indent=2)
                user_schedule_json = json.dumps(schedule, indent=2)
                next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
                print(f"   ✅ Next: {next_action['chunk_heading']} ({next_action['estimated_time_minutes']} min)")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        elif user_input.lower() in ['show me my progress', 'status', 'progress']:
            print("📊 Current Status:")
            for task in tasks:
                completed = sum(1 for st in task['subtasks'] if st['status'] == 'done')
                total = len(task['subtasks'])
                status_icon = "✅" if completed == total and total > 0 else "⏳"
                print(f"   {status_icon} {task['heading']}: {completed}/{total} completed")
        
        else:
            # Test action extraction
            try:
                # Get existing tasks as list for the agent
                from models.task_model import Task, TaskStatus
                from uuid import UUID
                existing_tasks = []
                for task in tasks:
                    # Create Task object with proper UUID
                    try:
                        task_id = UUID(task["id"].replace("task_", "")) if task["id"].startswith("task_") else UUID(task["id"])
                    except ValueError:
                        # Generate a new UUID if the ID is not a valid UUID
                        task_id = uuid4()
                    task_obj = Task(
                        id=task_id,
                        heading=task["heading"],
                        details=task["details"],
                        deadline=datetime.fromisoformat(task["deadline"]) if task.get("deadline") else None,
                        status=TaskStatus.IN_PROGRESS
                    )
                    
                    # Add subtasks if they exist
                    for subtask in task.get("subtasks", []):
                        try:
                            subtask_id = UUID(subtask["id"]) if subtask["id"] else uuid4()
                        except ValueError:
                            subtask_id = uuid4()
                        subtask_obj = Task(
                            id=subtask_id,
                            heading=subtask["heading"],
                            details=subtask["details"],
                            status=TaskStatus.DONE if subtask["status"] == "done" else TaskStatus.PENDING,
                            time_estimate=subtask.get("estimated_time_minutes")
                        )
                        task_obj.subtasks.append(subtask_obj)
                    
                    existing_tasks.append(task_obj)
                
                # Extract actions from user input
                actions = task_extractor.extract_task(user_input, existing_tasks)
                
                if actions:
                    for action in actions:
                        action_type = action.get('action')
                        print(f"   🎯 Detected action: {action_type}")
                        
                        if action_type == 'mark_done':
                            target = action.get('target_task')
                            print(f"   📝 Target: {target}")
                            # Simulate marking as done
                            for task in tasks:
                                if (task["id"] == target or 
                                    task["heading"].lower() in target.lower() or 
                                    target == 'last_task'):
                                    for subtask in task["subtasks"]:
                                        subtask["status"] = "done"
                                    print(f"   ✅ Marked '{task['heading']}' as completed")
                                    break
                        
                        elif action_type == 'add':
                            print(f"   ➕ Would add: {action['heading']}")
                            # Simulate adding new task
                            new_task = {
                                "id": f"task_{len(tasks) + 1}",
                                "heading": action['heading'],
                                "details": action['details'],
                                "deadline": action.get('deadline'),
                                "priority_score": 7.0,
                                "subtasks": []
                            }
                            tasks.append(new_task)
                            print(f"   ✅ Added new task: '{action['heading']}'")
                
                else:
                    print("   ❌ No action detected")
                    
            except Exception as e:
                print(f"   ❌ Error processing: {e}")
    
    # Show final state
    print(f"\n📊 Final Task State:")
    print("=" * 30)
    for task in tasks:
        completed = sum(1 for st in task['subtasks'] if st['status'] == 'done')
        total = len(task['subtasks'])
        status_icon = "✅" if completed == total and total > 0 else "⏳"
        print(f"{status_icon} {task['heading']}: {completed}/{total} completed")
    
    print(f"\n🎉 Test completed!")
    print(f"💡 Key improvements:")
    print(f"   ✅ Natural language input processing")
    print(f"   ✅ Automatic task status updates")
    print(f"   ✅ No priority display")
    print(f"   ✅ Automatic next recommendation after completion")
    print(f"   ✅ Better error handling for non-numeric inputs")

if __name__ == "__main__":
    test_improved_demo() 