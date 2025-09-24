#!/usr/bin/env python3
"""
Quick Test - Immediate demonstration with predefined tasks
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.genieorchestrator_agent import GenieOrchestrator
from dotenv import load_dotenv

def quick_test():
    """Quick test with predefined tasks"""
    print("🎯 Quick Genie Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize orchestrator
    try:
        orchestrator = GenieOrchestrator()
        print("✅ GenieOrchestrator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Predefined tasks
    tasks = {
        "tasks": [
            {
                "id": "task_1",
                "heading": "Learn Python Programming",
                "details": "Master Python fundamentals to build web applications and data analysis projects",
                "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "priority_score": 9.0,
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
                "details": "Create a modern todo application with React hooks and local storage",
                "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "priority_score": 7.5,
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
                    }
                ]
            },
            {
                "id": "task_3",
                "heading": "Prepare for Job Interview",
                "details": "Study algorithms, practice coding problems, and prepare for technical interview",
                "deadline": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "priority_score": 8.5,
                "subtasks": [
                    {
                        "id": "chunk_3_1",
                        "heading": "Review basic algorithms and data structures",
                        "details": "Study arrays, linked lists, trees, graphs, and basic algorithms",
                        "estimated_time_minutes": 60,
                        "status": "pending",
                        "resource": {
                            "title": "GeeksforGeeks - Data Structures",
                            "url": "https://www.geeksforgeeks.org/data-structures/",
                            "type": "article",
                            "focus_section": "Basic data structures section",
                            "paid": False
                        },
                        "dependencies": [],
                        "user_feedback": ""
                    }
                ]
            }
        ]
    }
    
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
            },
            {
                "start_time": "16:00",
                "end_time": "17:00",
                "day_of_week": "daily",
                "energy_level": "medium",
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
    
    print(f"📋 Tasks: {len(tasks['tasks'])} tasks with multiple subtasks")
    print(f"📅 Schedule: 3 time blocks with energy levels")
    
    # Convert to JSON
    all_tasks_json = json.dumps(tasks, indent=2)
    user_schedule_json = json.dumps(schedule, indent=2)
    
    # Get recommendation
    print("\n🎯 Getting Next Action Recommendation...")
    print("=" * 50)
    
    try:
        next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
        
        print("🎯 RECOMMENDED NEXT ACTION:")
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
        
        print(f"\n✅ Successfully orchestrated next action!")
        
        # Show why this was chosen
        print(f"\n💡 Why this was recommended:")
        print(f"   - Deadline proximity: {next_action.get('deadline', 'No deadline')}")
        print(f"   - Fits in available time: {next_action['estimated_time_minutes']} min")
        print(f"   - Energy level match: Scheduled during high energy period")
        
    except Exception as e:
        print(f"❌ Orchestration error: {e}")
        return
    
    print(f"\n🎉 Quick test completed!")
    print(f"💡 Try 'python3 interactive_demo.py' for a full interactive experience")

if __name__ == "__main__":
    quick_test() 