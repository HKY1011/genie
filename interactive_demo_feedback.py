#!/usr/bin/env python3
"""
Interactive Genie Demo with Feedback Loop
Test the complete feedback loop system with natural language interaction.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.supervisor_agent import SupervisorAgent
from models.user_session import SessionManager
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

def show_session_status(session_manager, user_id):
    """Show current session status"""
    session = session_manager.load_session(user_id)
    if not session:
        print("📊 No session data available")
        return
    
    print("\n📊 Current Session Status:")
    print("-" * 30)
    print(f"👤 User: {session.user_id}")
    print(f"📋 Total tasks: {len(session.tasks)}")
    print(f"✅ Completed today: {session.tasks_completed_today}")
    print(f"⏱️  Focus time today: {session.total_focus_time_today} minutes")
    print(f"📈 Completion history: {len(session.completion_history)}")
    print(f"⚡ Energy patterns: {len(session.energy_patterns)}")
    
    # Show task details
    if session.tasks:
        print(f"\n📋 Task Details:")
        for task in session.tasks:
            status_icon = "✅" if task.status.value == "done" else "⏳"
            print(f"   {status_icon} {task.heading} ({task.status.value})")
            if task.subtasks:
                for subtask in task.subtasks:
                    subtask_icon = "✅" if subtask.status.value == "done" else "⏳"
                    print(f"      {subtask_icon} {subtask.heading} ({subtask.status.value})")
    
    # Show productivity stats
    stats = session.get_productivity_stats()
    if stats['total_tasks_completed'] > 0:
        print(f"\n📊 Productivity Statistics:")
        print(f"   Total completed: {stats['total_tasks_completed']}")
        print(f"   Average time: {stats['average_completion_time']} min")
        print(f"   Average difficulty: {stats['average_difficulty']}/10")
        print(f"   Average productivity: {stats['average_productivity']}/10")
        print(f"   Completion rate: {stats['completion_rate']}%")

def interactive_demo():
    """Run the interactive demo with feedback loop"""
    print("🎯 Interactive Genie Demo with Feedback Loop")
    print("=" * 50)
    print("Test the complete feedback loop system!")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize supervisor agent
    print("\n🚀 Initializing SupervisorAgent...")
    try:
        session_manager = SessionManager()
        supervisor = SupervisorAgent(session_manager)
        print("✅ SupervisorAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SupervisorAgent: {e}")
        return
    
    # Get user ID
    user_id = input("\n👤 Enter your user ID (or press Enter for default): ").strip() or "demo_user"
    print(f"👤 User ID: {user_id}")
    
    # Get user availability
    schedule = get_user_availability()
    
    # Update user preferences in session
    print("\n📝 Setting up initial tasks...")
    print("Tell me what you want to work on:")
    print("Examples:")
    print("  - I need to learn Python programming by next Friday")
    print("  - Build a React todo app with authentication")
    print("  - Write a research paper on machine learning")
    print("  - Prepare for job interview next week")
    print()
    
    # Get initial tasks
    initial_tasks = input("What would you like to work on? ").strip()
    
    if initial_tasks:
        print(f"\n📝 Processing: {initial_tasks}")
        result = supervisor.process_user_feedback(initial_tasks, user_id)
        
        if result.success:
            print(f"✅ {result.user_message}")
            print(f"💬 {result.motivational_message}")
            
            if result.next_action:
                print(f"\n🎯 Next Action:")
                print(f"   📋 Task: {result.next_action.get('task_id', 'Unknown')}")
                print(f"   🎯 Chunk: {result.next_action.get('chunk_heading', 'Unknown')}")
                print(f"   ⏱️  Time: {result.next_action.get('estimated_time_minutes', 0)} minutes")
                print(f"   📅 Scheduled: {result.next_action.get('scheduled_time_start', 'Unknown')}")
                
                if result.next_action.get('resource'):
                    resource = result.next_action['resource']
                    print(f"   📚 Resource: {resource.get('title', 'Unknown')}")
                    print(f"   🔗 URL: {resource.get('url', 'Unknown')}")
        else:
            print(f"❌ {result.user_message}")
            if result.errors:
                print(f"   Errors: {', '.join(result.errors)}")
    
    # Show initial status
    show_session_status(session_manager, user_id)
    
    # Interactive feedback loop
    print("\n🔄 Interactive Feedback Loop")
    print("=" * 40)
    print("Now you can interact with Genie using natural language!")
    print("\nExamples of what you can say:")
    print("  ✅ 'I finished the Python task, it took 90 minutes and was challenging'")
    print("  🔄 'The React app is too hard, can you break it down?'")
    print("  📝 'Add a new task: learn machine learning by next Friday'")
    print("  ⏰ 'Change the React deadline to next Monday'")
    print("  📊 'Show me my progress'")
    print("  🎯 'What should I do next?'")
    print("  🚪 'quit' to exit")
    print()
    
    while True:
        user_input = input("💬 What would you like to tell Genie? ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        print(f"\n🔄 Processing: {user_input}")
        
        # Process feedback through supervisor
        result = supervisor.process_user_feedback(user_input, user_id)
        
        # Display results
        print(f"\n📋 Result: {result.user_message}")
        print(f"💬 {result.motivational_message}")
        
        if result.next_action:
            print(f"\n🎯 Next Action:")
            print(f"   📋 Task: {result.next_action.get('task_id', 'Unknown')}")
            print(f"   🎯 Chunk: {result.next_action.get('chunk_heading', 'Unknown')}")
            print(f"   ⏱️  Time: {result.next_action.get('estimated_time_minutes', 0)} minutes")
            print(f"   📅 Scheduled: {result.next_action.get('scheduled_time_start', 'Unknown')}")
            
            if result.next_action.get('resource'):
                resource = result.next_action['resource']
                print(f"   📚 Resource: {resource.get('title', 'Unknown')}")
                print(f"   🔗 URL: {resource.get('url', 'Unknown')}")
        
        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"   • {rec.get('reasoning', 'No reasoning provided')}")
        
        if result.errors:
            print(f"\n⚠️  Errors: {', '.join(result.errors)}")
        
        print(f"\n⏱️  Processing time: {result.processing_time:.2f}s")
        print(f"📊 Confidence: {result.confidence_score:.2f}")
        
        # Show updated status
        show_session_status(session_manager, user_id)
        
        print("\n" + "-" * 50)
    
    # Final status
    print("\n📊 Final Session Status:")
    show_session_status(session_manager, user_id)
    
    print("\n👋 Thanks for testing Genie's feedback loop system!")
    print("💡 The system successfully:")
    print("   ✅ Processed natural language feedback")
    print("   ✅ Generated adaptive recommendations")
    print("   ✅ Provided motivational messages")
    print("   ✅ Updated persistent state")
    print("   ✅ Generated next action recommendations")
    print("   ✅ Maintained session persistence")

if __name__ == "__main__":
    interactive_demo() 