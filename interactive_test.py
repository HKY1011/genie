#!/usr/bin/env python3
"""
Interactive Test Script for Genie Backend
Allows users to input their own tasks and see detailed output about:
- Task extraction
- Subtask planning (how many subtasks are created)
- Orchestrator prioritization
- Calendar integration
"""

import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.task_extraction_agent import TaskExtractionAgent
from agents.planning_agent import PlanningAgent
from agents.genieorchestrator_agent import GenieOrchestrator
from integrations.google_calendar_api import GoogleCalendarAPI
from storage.json_store import JsonStore
from models.user_session import SessionManager
from dotenv import load_dotenv

def print_separator(title=""):
    """Print a nice separator"""
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("\n" + "="*60)

def test_task_extraction(user_input):
    """Test task extraction with detailed output"""
    print_separator("TASK EXTRACTION")
    
    try:
        extraction_agent = TaskExtractionAgent()
        print(f"📝 Processing input: '{user_input}'")
        
        # Add delay to avoid rate limiting
        print("⏳ Waiting 2 seconds to avoid rate limiting...")
        time.sleep(2)
        
        actions = extraction_agent.extract_task(user_input, existing_tasks=[])
        
        if actions and len(actions) > 0:
            action = actions[0]
            action_type = action.get('action', 'unknown')
            
            print(f"✅ Action Type: {action_type}")
            print(f"📋 Task Heading: {action.get('heading', 'Unknown')}")
            print(f"📄 Task Details: {action.get('details', 'No details')}")
            print(f"⏰ Deadline: {action.get('deadline', 'No deadline')}")
            print(f"🎯 Priority: {action.get('priority', 'No priority')}")
            
            return action
        else:
            print("❌ No actions extracted")
            return None
            
    except Exception as e:
        print(f"❌ Task extraction failed: {e}")
        return None

def test_task_planning(task_data):
    """Test task planning with detailed output"""
    print_separator("TASK PLANNING")
    
    try:
        planning_agent = PlanningAgent()
        
        # Ensure task details is not empty
        task_details = task_data.get('details', '')
        if not task_details or task_details.strip() == '':
            task_details = f"Complete the task: {task_data.get('heading', 'Unknown Task')}. This involves learning and implementing the required skills and knowledge."
        
        task_input = {
            "heading": task_data.get('heading', 'Unknown Task'),
            "details": task_details,
            "deadline": task_data.get('deadline'),
            "previous_chunks": [],
            "corrections_or_feedback": ""
        }
        
        print(f"📋 Planning subtasks for: {task_input['heading']}")
        print(f"📄 Task details: {task_input['details'][:100]}...")
        
        # Generate initial subtasks to see how many are created
        print("\n🔄 Generating initial subtasks...")
        task_id = "interactive_test_task"
        initial_subtasks = planning_agent.generate_initial_subtasks(task_input, task_id)
        
        print(f"📊 Total subtasks generated: {len(initial_subtasks)}")
        
        for i, subtask in enumerate(initial_subtasks, 1):
            print(f"\n  {i}. {subtask.get('chunk_heading', 'Unknown')}")
            print(f"     📄 Details: {subtask.get('chunk_details', 'No details')[:80]}...")
            print(f"     ⏱️  Estimated time: {subtask.get('estimated_time_minutes', 'Unknown')} minutes")
            print(f"     🔗 Resource: {subtask.get('resource', {}).get('title', 'No resource')}")
        
        # Get the first chunk for orchestrator
        print("\n🔄 Getting first chunk for orchestrator...")
        chunk = planning_agent.get_next_chunk(task_input)
        
        if chunk:
            print(f"✅ First chunk: {chunk.get('chunk_heading', 'Unknown')}")
            return chunk, initial_subtasks
        else:
            print("❌ Failed to get first chunk")
            return None, initial_subtasks
            
    except Exception as e:
        print(f"❌ Task planning failed: {e}")
        return None, []

def test_orchestrator(task_data, chunk, all_subtasks):
    """Test orchestrator with detailed output"""
    print_separator("ORCHESTRATOR PRIORITIZATION")
    
    try:
        orchestrator = GenieOrchestrator()
        
        # Create orchestrator input data
        orchestrator_tasks = {
            "tasks": [{
                "id": "interactive_task_1",
                "heading": task_data.get('heading', 'Unknown Task'),
                "details": task_data.get('details', ''),
                "deadline": task_data.get('deadline'),
                "priority_score": 8.0,
                "subtasks": [{
                    "id": subtask.get('chunk_order', i+1),
                    "heading": subtask.get('chunk_heading', 'Unknown'),
                    "details": subtask.get('chunk_details', ''),
                    "estimated_time_minutes": subtask.get('estimated_time_minutes', 30),
                    "status": "pending",
                    "resource": subtask.get('resource', {}),
                    "dependencies": [],
                    "user_feedback": ""
                } for i, subtask in enumerate(all_subtasks)]
            }]
        }
        
        # Create sample schedule
        orchestrator_schedule = {
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
        
        # Convert to JSON
        all_tasks_json = json.dumps(orchestrator_tasks, indent=2)
        user_schedule_json = json.dumps(orchestrator_schedule, indent=2)
        
        print(f"📊 Total subtasks for orchestrator: {len(all_subtasks)}")
        print(f"📅 Available time slots: {len(orchestrator_schedule['availability']['free'])}")
        
        # Get next action
        next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
        
        if next_action:
            print(f"✅ Next action determined:")
            print(f"   🎯 Chunk ID: {next_action.get('next_chunk_id', 'Unknown')}")
            print(f"   📋 Chunk Heading: {next_action.get('chunk_heading', 'Unknown')}")
            print(f"   ⏰ Scheduled Start: {next_action.get('scheduled_time_start', 'Unknown')}")
            print(f"   ⏰ Scheduled End: {next_action.get('scheduled_time_end', 'Unknown')}")
            print(f"   📊 Priority Score: {next_action.get('priority_score', 'Unknown')}")
            print(f"   🔗 Resource: {next_action.get('resource', {}).get('title', 'No resource')}")
            
            return next_action
        else:
            print("❌ Orchestrator failed to determine next action")
            return None
            
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return None

def test_calendar_integration(next_action, task_data):
    """Test calendar integration"""
    print_separator("CALENDAR INTEGRATION")
    
    try:
        calendar_api = GoogleCalendarAPI()
        
        if not calendar_api.service:
            print("⚠️  Calendar API not available (check credentials)")
            return None
        
        # List calendars
        calendars = calendar_api.list_calendars()
        print(f"📅 Available calendars: {len(calendars)}")
        for cal in calendars[:3]:  # Show first 3
            print(f"   - {cal.get('summary', 'Unknown')} ({cal.get('id', 'Unknown')})")
        
        if next_action and next_action.get('scheduled_time_start'):
            try:
                start_time = datetime.fromisoformat(next_action['scheduled_time_start'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(next_action['scheduled_time_end'].replace('Z', '+00:00'))
                
                event_id = calendar_api.create_event(
                    summary=f"[Genie] {next_action['chunk_heading']}",
                    description=f"Task: {task_data.get('heading', 'Unknown Task')}\n\n{next_action.get('chunk_details', '')}\n\nResource: {next_action.get('resource', {}).get('title', 'No resource')}",
                    start_datetime=start_time,
                    end_datetime=end_time
                )
                
                if event_id:
                    print(f"✅ Calendar event created: {event_id}")
                    print(f"   📅 Event: {next_action['chunk_heading']}")
                    print(f"   ⏰ Time: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
                    
                    # Ask user if they want to keep or delete the event
                    response = input("\n🗑️  Delete this test event? (y/n): ").lower().strip()
                    if response == 'y':
                        calendar_api.delete_event(event_id)
                        print("✅ Test event deleted")
                    else:
                        print("✅ Test event kept in calendar")
                    
                    return event_id
                else:
                    print("❌ Failed to create calendar event")
                    return None
                    
            except Exception as e:
                print(f"❌ Calendar event creation failed: {e}")
                return None
        else:
            print("⚠️  No scheduled time available for calendar event")
            return None
            
    except Exception as e:
        print(f"❌ Calendar integration failed: {e}")
        return None

def main():
    """Main interactive test function"""
    print("🚀 GENIE BACKEND INTERACTIVE TEST")
    print("=" * 60)
    print("This script allows you to test the complete Genie workflow with your own tasks.")
    print("You'll see detailed output about task extraction, planning, and prioritization.")
    
    # Load environment variables
    load_dotenv()
    
    while True:
        print_separator()
        
        # Get user input
        user_input = input("📝 Enter your task (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            print("⚠️  Please enter a task description")
            continue
        
        print(f"\n🔄 Processing: '{user_input}'")
        
        # Step 1: Task Extraction
        task_data = test_task_extraction(user_input)
        if not task_data:
            print("❌ Task extraction failed. Please try again.")
            continue
        
        # Step 2: Task Planning
        chunk, all_subtasks = test_task_planning(task_data)
        if not chunk:
            print("❌ Task planning failed. Please try again.")
            continue
        
        # Step 3: Orchestrator
        next_action = test_orchestrator(task_data, chunk, all_subtasks)
        if not next_action:
            print("❌ Orchestrator failed. Please try again.")
            continue
        
        # Step 4: Calendar Integration (optional)
        calendar_response = input("\n📅 Create calendar event? (y/n): ").lower().strip()
        if calendar_response == 'y':
            test_calendar_integration(next_action, task_data)
        
        # Summary
        print_separator("SUMMARY")
        print(f"✅ Task: {task_data.get('heading', 'Unknown')}")
        print(f"📊 Subtasks created: {len(all_subtasks)}")
        print(f"🎯 Next action: {next_action.get('chunk_heading', 'Unknown')}")
        print(f"⏰ Scheduled for: {next_action.get('scheduled_time_start', 'Unknown')}")
        
        # Ask if user wants to continue
        continue_response = input("\n🔄 Test another task? (y/n): ").lower().strip()
        if continue_response != 'y':
            print("👋 Goodbye!")
            break

if __name__ == "__main__":
    main() 