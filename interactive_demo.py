#!/usr/bin/env python3
"""
Interactive Genie Demo
Test the complete system with multiple tasks and real-time orchestration.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.supervisor_agent import SupervisorAgent
from agents.task_extraction_agent import TaskExtractionAgent
from agents.planning_agent import PlanningAgent
from agents.genieorchestrator_agent import GenieOrchestrator
from models.user_session import SessionManager
from models.task_model import Task, TaskStatus
from dotenv import load_dotenv

def get_user_availability():
    """Get user availability preferences"""
    print("\n📅 Setting Up Your Availability")
    print("=" * 40)
    
    print("Let's set up your typical daily schedule:")
    
    schedule = {
        "daily_schedule": [],
        "preferences": {},
        "timezone": "UTC"
    }
    
    # Get work hours
    print("\n🕐 What are your typical work hours?")
    start_time = input("Start time (e.g., 09:00): ").strip() or "09:00"
    end_time = input("End time (e.g., 17:00): ").strip() or "17:00"
    
    # Get energy levels
    print("\n⚡ When do you have the most energy?")
    print("1. Morning (high energy)")
    print("2. Afternoon (medium energy)")
    print("3. Evening (low energy)")
    energy_choice = input("Choose (1-3): ").strip() or "1"
    
    energy_map = {"1": "high", "2": "medium", "3": "low"}
    energy_level = energy_map.get(energy_choice, "high")
    
    # Create schedule blocks
    schedule["daily_schedule"] = [
        {
            "start_time": start_time,
            "end_time": end_time,
            "day_of_week": "daily",
            "energy_level": energy_level,
            "focus_type": "deep_work"
        }
    ]
    
    # Get preferences
    print("\n⏱️  Work session preferences:")
    preferred_duration = input("Preferred work session length (minutes, e.g., 45): ").strip() or "45"
    max_duration = input("Maximum work session length (minutes, e.g., 90): ").strip() or "90"
    
    # Handle non-numeric input gracefully
    try:
        preferred_duration = int(preferred_duration)
    except ValueError:
        preferred_duration = 45
    
    try:
        max_duration = int(max_duration)
    except ValueError:
        max_duration = 90
    
    schedule["preferences"] = {
        "preferred_work_duration": preferred_duration,
        "max_work_duration": max_duration,
        "break_duration": 15,
        "energy_peak_hours": [f"{start_time}-{end_time}"],
        "avoid_work_hours": []
    }
    
    print(f"\n✅ Schedule configured:")
    print(f"   Work hours: {start_time} - {end_time}")
    print(f"   Energy level: {energy_level}")
    print(f"   Preferred session: {preferred_duration} minutes")
    print(f"   Max session: {max_duration} minutes")
    
    return schedule

def create_task_from_input(task_input, task_id):
    """Create a task structure from user input"""
    # Use TaskExtractionAgent to extract structured task
    try:
        task_extractor = TaskExtractionAgent()
        actions = task_extractor.extract_task(task_input, [])
        
        if actions and actions[0]['action'] == 'add':
            action = actions[0]
            return {
                "id": f"task_{task_id}",
                "heading": action['heading'],
                "details": action['details'],
                "deadline": action.get('deadline'),
                "priority_score": 7.0,  # Default priority
                "subtasks": []  # Will be populated by PlanningAgent
            }
    except Exception as e:
        print(f"⚠️  Task extraction failed: {e}")
    
    # Fallback: create basic task structure
    return {
        "id": f"task_{task_id}",
        "heading": task_input[:50] + "..." if len(task_input) > 50 else task_input,
        "details": task_input,
        "deadline": None,
        "priority_score": 7.0,
        "subtasks": []
    }

def break_down_task(task, planner):
    """Break down a task into subtasks using PlanningAgent"""
    try:
        # Create task dict for planning
        task_dict = {
            "heading": task["heading"],
            "details": task["details"],
            "deadline": task.get("deadline"),
            "previous_chunks": [],
            "corrections_or_feedback": ""
        }
        
        # Get first chunk
        chunk = planner.get_next_chunk(task_dict)
        
        # Create subtask structure
        subtask = {
            "id": f"{task['id']}_chunk_1",
            "heading": chunk["chunk_heading"],
            "details": chunk["chunk_details"],
            "estimated_time_minutes": chunk["estimated_time_minutes"],
            "status": "pending",
            "resource": chunk["resource"],
            "dependencies": [],
            "user_feedback": ""
        }
        
        task["subtasks"].append(subtask)
        
        # Get second chunk if available
        try:
            task_dict["previous_chunks"] = [{"chunk_order": 1, "id": subtask["id"], "heading": subtask["heading"]}]
            chunk2 = planner.get_next_chunk(task_dict)
            
            subtask2 = {
                "id": f"{task['id']}_chunk_2",
                "heading": chunk2["chunk_heading"],
                "details": chunk2["chunk_details"],
                "estimated_time_minutes": chunk2["estimated_time_minutes"],
                "status": "pending",
                "resource": chunk2["resource"],
                "dependencies": [subtask["id"]],
                "user_feedback": ""
            }
            
            task["subtasks"].append(subtask2)
            
        except Exception:
            pass  # Second chunk not available
        
        return True
        
    except Exception as e:
        print(f"⚠️  Task breakdown failed: {e}")
        return False

def process_user_input(user_input, tasks, task_extractor):
    """Process natural language user input and extract actions"""
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
        
        if not actions:
            return False, "No action detected in your input"
        
        # Process each action
        for action in actions:
            action_type = action.get('action')
            
            if action_type == 'mark_done':
                target = action.get('target_task')
                if target:
                    # Find the task to mark as done
                    for task in tasks:
                        if (task["id"] == target or 
                            task["heading"].lower() in target.lower() or 
                            target == 'last_task'):
                            # Mark all subtasks as done
                            for subtask in task["subtasks"]:
                                subtask["status"] = "done"
                            return True, f"✅ Marked '{task['heading']}' as completed"
                    
                    return False, f"❌ Task '{target}' not found"
            
            elif action_type == 'add':
                # Create new task
                new_task = {
                    "id": f"task_{len(tasks) + 1}",
                    "heading": action['heading'],
                    "details": action['details'],
                    "deadline": action.get('deadline'),
                    "priority_score": 7.0,
                    "subtasks": []
                }
                tasks.append(new_task)
                return True, f"✅ Added new task: '{action['heading']}'"
            
            elif action_type == 'edit':
                target = action.get('target_task')
                if target:
                    for task in tasks:
                        if (task["id"] == target or 
                            task["heading"].lower() in target.lower() or 
                            target == 'last_task'):
                            if 'heading' in action:
                                task["heading"] = action['heading']
                            if 'details' in action:
                                task["details"] = action['details']
                            if 'deadline' in action:
                                task["deadline"] = action['deadline']
                            return True, f"✅ Updated task: '{task['heading']}'"
                    
                    return False, f"❌ Task '{target}' not found"
        
        return True, "Action processed successfully"
        
    except Exception as e:
        return False, f"Error processing input: {e}"

def get_next_recommendation(tasks, schedule, orchestrator):
    """Get the next action recommendation"""
    try:
        # Convert to JSON for orchestrator
        all_tasks_json = json.dumps({"tasks": tasks}, indent=2)
        user_schedule_json = json.dumps(schedule, indent=2)
        
        next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
        
        print("\n🎯 RECOMMENDED NEXT ACTION:")
        print("-" * 40)
        print(f"📋 Task: {next_action['task_id']}")
        print(f"🎯 Chunk: {next_action['chunk_heading']}")
        print(f"⏱️  Time: {next_action['estimated_time_minutes']} minutes")
        print(f"📅 Scheduled: {next_action['scheduled_time_start']} to {next_action['scheduled_time_end']}")
        
        print(f"\n📚 Resource:")
        print(f"   Title: {next_action['resource']['title']}")
        print(f"   Type: {next_action['resource']['type']}")
        print(f"   URL: {next_action['resource']['url']}")
        print(f"   Focus: {next_action['resource']['focus_section']}")
        print(f"   Paid: {next_action['resource']['paid']}")
        
        if next_action['resource'].get('rationale'):
            print(f"   Why: {next_action['resource']['rationale']}")
        
        print(f"\n📖 Instructions:")
        print(f"   {next_action['chunk_details']}")
        
        print(f"\n📊 Progress Summary:")
        print(f"   Completed: {next_action['progress_summary']['completed_chunks']}/{next_action['progress_summary']['total_chunks']} chunks")
        
        if next_action['progress_summary'].get('upcoming_deadlines_warning'):
            print(f"   ⏰ {next_action['progress_summary']['upcoming_deadlines_warning']}")
        
        if next_action.get('warnings'):
            print(f"\n⚠️  Warnings: {next_action['warnings']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting recommendation: {e}")
        return False

def show_status(tasks):
    """Show current task status"""
    print("\n📊 Current Status:")
    print("-" * 30)
    for task in tasks:
        completed = sum(1 for st in task['subtasks'] if st['status'] == 'done')
        total = len(task['subtasks'])
        status_icon = "✅" if completed == total and total > 0 else "⏳"
        print(f"{status_icon} {task['heading']}: {completed}/{total} completed")
        
        # Show pending subtasks
        pending_subtasks = [st for st in task['subtasks'] if st['status'] == 'pending']
        if pending_subtasks:
            for subtask in pending_subtasks[:2]:  # Show first 2 pending
                print(f"   ⏳ {subtask['heading']} ({subtask['estimated_time_minutes']} min)")

def interactive_demo():
    """Run the interactive demo"""
    print("🎯 Interactive Genie Demo")
    print("=" * 50)
    print("Test the complete Genie system with multiple tasks!")
    
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
    
    # Get user availability
    schedule = get_user_availability()
    
    # Collect tasks from user
    print("\n📝 Adding Tasks")
    print("=" * 40)
    print("Enter your tasks (one per line, press Enter twice when done):")
    print("Examples:")
    print("  - I need to learn Python programming by next Friday")
    print("  - Build a React todo app with authentication")
    print("  - Write a research paper on machine learning")
    print("  - Prepare for job interview next week")
    print()
    
    tasks = []
    task_id = 1
    
    while True:
        task_input = input(f"Task {task_id} (or press Enter to finish): ").strip()
        
        if not task_input:
            break
        
        print(f"Processing: {task_input}")
        
        # Create task structure
        task = create_task_from_input(task_input, task_id)
        
        # Break down task into subtasks
        print("Breaking down task into manageable chunks...")
        if break_down_task(task, planner):
            print(f"✅ Created {len(task['subtasks'])} subtasks")
        else:
            print("⚠️  Using basic task structure")
        
        tasks.append(task)
        task_id += 1
    
    if not tasks:
        print("❌ No tasks entered. Exiting.")
        return
    
    print(f"\n✅ Added {len(tasks)} tasks")
    
    # Show current state
    print("\n📊 Current Task State:")
    print("=" * 40)
    for task in tasks:
        print(f"📋 {task['heading']}")
        print(f"   Subtasks: {len(task['subtasks'])}")
        for subtask in task['subtasks']:
            status = "✅" if subtask['status'] == 'done' else "⏳"
            print(f"   {status} {subtask['heading']} ({subtask['estimated_time_minutes']} min)")
        print()
    
    # Get initial recommendation
    print("\n🎯 Getting Next Action Recommendation...")
    print("=" * 40)
    
    if not get_next_recommendation(tasks, schedule, orchestrator):
        return
    
    # Interactive task management
    print("\n🔄 Interactive Task Management")
    print("=" * 40)
    print("Just tell me what you want to do! Examples:")
    print("  - 'I finished the Python task'")
    print("  - 'Mark the React app as done'")
    print("  - 'Add a new task: learn machine learning'")
    print("  - 'What should I do next?'")
    print("  - 'Show me my progress'")
    print("  - 'quit' to exit")
    
    while True:
        user_input = input("\nWhat would you like to do? ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        elif user_input.lower() in ['next', 'what should i do next', 'recommend']:
            get_next_recommendation(tasks, schedule, orchestrator)
        elif user_input.lower() in ['status', 'progress', 'show progress']:
            show_status(tasks)
        else:
            # Process natural language input
            success, message = process_user_input(user_input, tasks, task_extractor)
            print(message)
            
            if success:
                # Automatically get next recommendation if a task was completed
                if 'completed' in message.lower() or 'done' in message.lower():
                    print("\n🎯 Getting next recommendation...")
                    get_next_recommendation(tasks, schedule, orchestrator)
    
    print("\n👋 Thanks for testing Genie!")

if __name__ == "__main__":
    interactive_demo() 