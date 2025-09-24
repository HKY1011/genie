#!/usr/bin/env python3
"""
Complete Genie System Demo
Demonstrates all three agents working together: TaskExtractionAgent, PlanningAgent, and GenieOrchestrator.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.task_extraction_agent import TaskExtractionAgent
from agents.planning_agent import PlanningAgent
from agents.genieorchestrator_agent import GenieOrchestrator
from dotenv import load_dotenv

def demo_complete_system():
    """Demonstrate the complete Genie system"""
    print("🎯 Complete Genie System Demo")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    print("📋 System Components:")
    print("  ✅ TaskExtractionAgent - Extracts tasks from natural language")
    print("  ✅ PlanningAgent - Breaks down tasks into manageable chunks")
    print("  ✅ GenieOrchestrator - Prioritizes and schedules next actions")
    print("  ✅ JsonStore - Persistent task storage")
    print("  ✅ Gemini API - Task extraction and orchestration")
    print("  ✅ Perplexity API - Task breakdown and resource finding")
    
    # Initialize all agents
    print("\n🚀 Initializing Agents...")
    try:
        task_extractor = TaskExtractionAgent()
        planner = PlanningAgent()
        orchestrator = GenieOrchestrator()
        print("✅ All agents initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return
    
    # Demo 1: Task Extraction
    print("\n" + "=" * 60)
    print("🔍 Demo 1: Task Extraction")
    print("=" * 60)
    
    user_input = "I need to learn Python programming and build a React todo app by next month"
    existing_tasks = []
    
    print(f"📝 User Input: \"{user_input}\"")
    
    try:
        actions = task_extractor.extract_task(user_input, existing_tasks)
        
        print(f"\n🤖 Extracted Actions:")
        for i, action in enumerate(actions, 1):
            print(f"  Action {i}: {action['action']}")
            if action['action'] == 'add':
                print(f"    Heading: {action['heading']}")
                print(f"    Details: {action['details']}")
                if action.get('deadline'):
                    print(f"    Deadline: {action['deadline']}")
        
        print(f"✅ Successfully extracted {len(actions)} tasks")
        
    except Exception as e:
        print(f"❌ Task extraction error: {e}")
        return
    
    # Demo 2: Task Planning
    print("\n" + "=" * 60)
    print("📋 Demo 2: Task Planning")
    print("=" * 60)
    
    # Create a task for planning
    task_for_planning = {
        "heading": "Learn Python Programming",
        "details": "Master Python fundamentals to build web applications and data analysis projects. I have no prior programming experience.",
        "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "previous_chunks": [],
        "corrections_or_feedback": ""
    }
    
    print(f"📝 Planning Task: {task_for_planning['heading']}")
    print(f"📅 Deadline: {task_for_planning['deadline']}")
    
    try:
        chunk = planner.get_next_chunk(task_for_planning)
        
        print(f"\n🎯 Next Chunk:")
        print(f"  Heading: {chunk['chunk_heading']}")
        print(f"  Time: {chunk['estimated_time_minutes']} minutes")
        print(f"  Resource: {chunk['resource']['title']}")
        print(f"  Type: {chunk['resource']['type']}")
        print(f"  Paid: {chunk['resource']['paid']}")
        
        print(f"✅ Successfully planned next chunk")
        
    except Exception as e:
        print(f"❌ Task planning error: {e}")
        return
    
    # Demo 3: Task Orchestration
    print("\n" + "=" * 60)
    print("🎼 Demo 3: Task Orchestration")
    print("=" * 60)
    
    # Create sample tasks and schedule for orchestration
    all_tasks_json = json.dumps({
        "tasks": [
            {
                "id": "task_1",
                "heading": "Learn Python Programming",
                "details": "Master Python fundamentals",
                "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "priority_score": 8.5,
                "subtasks": [
                    {
                        "id": "chunk_1_1",
                        "heading": "Set up Python environment",
                        "details": "Install Python and write first program",
                        "estimated_time_minutes": 30,
                        "status": "done",
                        "resource": {"title": "Python Guide", "url": "https://docs.python.org", "type": "documentation", "focus_section": "Installation", "paid": False},
                        "dependencies": [],
                        "user_feedback": ""
                    },
                    {
                        "id": "chunk_1_2",
                        "heading": "Learn Python basics",
                        "details": "Understand variables, strings, lists",
                        "estimated_time_minutes": 45,
                        "status": "pending",
                        "resource": {"title": "Python Tutorial", "url": "https://docs.python.org/tutorial", "type": "documentation", "focus_section": "Basics", "paid": False},
                        "dependencies": ["chunk_1_1"],
                        "user_feedback": ""
                    }
                ]
            },
            {
                "id": "task_2",
                "heading": "Build React Todo App",
                "details": "Create modern todo application",
                "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "priority_score": 7.0,
                "subtasks": [
                    {
                        "id": "chunk_2_1",
                        "heading": "Set up React environment",
                        "details": "Install Node.js and create React app",
                        "estimated_time_minutes": 25,
                        "status": "done",
                        "resource": {"title": "React Setup", "url": "https://react.dev", "type": "documentation", "focus_section": "Getting Started", "paid": False},
                        "dependencies": [],
                        "user_feedback": "Setup was easy"
                    },
                    {
                        "id": "chunk_2_2",
                        "heading": "Create todo component",
                        "details": "Build main TodoApp component",
                        "estimated_time_minutes": 35,
                        "status": "pending",
                        "resource": {"title": "React Components", "url": "https://react.dev/components", "type": "documentation", "focus_section": "Components", "paid": False},
                        "dependencies": ["chunk_2_1"],
                        "user_feedback": ""
                    }
                ]
            }
        ]
    })
    
    user_schedule_json = json.dumps({
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
            "max_work_duration": 90
        },
        "timezone": "UTC"
    })
    
    print(f"📋 Tasks: 2 tasks with multiple subtasks")
    print(f"📅 Schedule: 2 high-energy time blocks")
    
    try:
        next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
        
        print(f"\n🎯 Orchestrator Recommendation:")
        print(f"  Task: {next_action['task_id']}")
        print(f"  Chunk: {next_action['chunk_heading']}")
        print(f"  Time: {next_action['estimated_time_minutes']} minutes")
        print(f"  Priority: {next_action['priority_score']}")
        print(f"  Scheduled: {next_action['scheduled_time_start']} to {next_action['scheduled_time_end']}")
        
        print(f"\n📚 Resource:")
        print(f"  Title: {next_action['resource']['title']}")
        print(f"  Type: {next_action['resource']['type']}")
        print(f"  Focus: {next_action['resource']['focus_section']}")
        
        print(f"\n📊 Progress: {next_action['progress_summary']['completed_chunks']}/{next_action['progress_summary']['total_chunks']} chunks completed")
        
        if next_action.get('warnings'):
            print(f"\n⚠️  Warnings: {next_action['warnings']}")
        
        print(f"✅ Successfully orchestrated next action")
        
    except Exception as e:
        print(f"❌ Task orchestration error: {e}")
        return
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Complete System Demo Summary")
    print("=" * 60)
    
    print("✅ All three agents working together:")
    print("  1. TaskExtractionAgent - Extracted tasks from natural language")
    print("  2. PlanningAgent - Broke down tasks into manageable chunks")
    print("  3. GenieOrchestrator - Prioritized and scheduled next actions")
    
    print("\n🚀 System Capabilities:")
    print("  ✅ Natural language task extraction")
    print("  ✅ Intelligent task breakdown with resources")
    print("  ✅ Multi-task prioritization and scheduling")
    print("  ✅ Context-aware recommendations")
    print("  ✅ Deadline and energy level consideration")
    print("  ✅ Progress tracking and warnings")
    
    print("\n💡 Ready for Production Use!")
    print("  The complete Genie system can now:")
    print("  - Understand user goals from natural language")
    print("  - Break down complex tasks into actionable steps")
    print("  - Prioritize across multiple tasks and deadlines")
    print("  - Schedule work based on user availability and energy")
    print("  - Provide high-quality resources for each step")

if __name__ == "__main__":
    demo_complete_system() 