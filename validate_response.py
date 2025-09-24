#!/usr/bin/env python3
"""
Interactive Response Validation for TaskExtractionAgent
Allows you to input your own text and see the agent's response.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from models.task_model import Task, TaskStatus
from agents.task_extraction_agent import TaskExtractionAgent
from dotenv import load_dotenv

def setup_sample_tasks():
    """Create sample tasks for testing"""
    tasks = [
        Task(
            heading="Complete project documentation",
            details="Write comprehensive documentation for the genie_backend project including API docs and user guides",
            time_estimate=120,
            status=TaskStatus.IN_PROGRESS,
            deadline=datetime.utcnow() + timedelta(days=3)
        ),
        Task(
            heading="Review code changes",
            details="Review all pending pull requests and provide feedback to team members",
            time_estimate=60,
            status=TaskStatus.PENDING,
            deadline=datetime.utcnow() + timedelta(days=1)
        ),
        Task(
            heading="Setup development environment",
            details="Install all required dependencies and configure local development setup",
            time_estimate=45,
            status=TaskStatus.DONE
        ),
        Task(
            heading="Write unit tests",
            details="Create comprehensive unit tests for all modules",
            time_estimate=90,
            status=TaskStatus.PENDING
        )
    ]
    return tasks

def show_current_tasks(tasks):
    """Display current tasks"""
    print("\n📋 Current Tasks:")
    print("-" * 50)
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.heading}")
        print(f"   ID: {task.id}")
        print(f"   Status: {task.status.value}")
        print(f"   Time: {task.time_estimate} min")
        if task.deadline:
            print(f"   Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Details: {task.details[:60]}...")
        print()

def validate_single_input():
    """Validate a single user input"""
    print("🔍 Interactive Response Validation")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not set in .env file")
        print("Please add your actual Gemini API key to .env file")
        return
    
    # Initialize agent
    try:
        agent = TaskExtractionAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Setup sample tasks
    tasks = setup_sample_tasks()
    show_current_tasks(tasks)
    
    while True:
        print("\n" + "=" * 50)
        print("💬 Enter your input (or 'quit' to exit):")
        user_input = input("> ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            print("⚠️  Please enter some text")
            continue
        
        print(f"\n🤖 Processing: \"{user_input}\"")
        print("-" * 40)
        
        try:
            # Get agent response
            actions = agent.extract_task(user_input, tasks)
            
            print("📤 Agent Response:")
            if actions:
                for i, action in enumerate(actions, 1):
                    print(f"\n   Action {i}:")
                    print(f"   {json.dumps(action, indent=4)}")
                    
                    # Validate action structure
                    print(f"\n   ✅ Validation:")
                    if 'action' in action:
                        print(f"      - Action type: {action['action']}")
                    else:
                        print(f"      - ❌ Missing 'action' field")
                    
                    if action.get('action') == 'add':
                        if 'heading' in action:
                            print(f"      - ✅ New task heading: {action['heading']}")
                        else:
                            print(f"      - ❌ Missing 'heading' for new task")
                    
                    elif action.get('action') in ['edit', 'mark_done', 'reschedule', 'add_subtask']:
                        if 'target_task' in action:
                            print(f"      - ✅ Target task: {action['target_task']}")
                        else:
                            print(f"      - ❌ Missing 'target_task'")
                    
                    if 'deadline' in action and action['deadline']:
                        print(f"      - ✅ Deadline: {action['deadline']}")
                    
                    if 'time_estimate' in action:
                        print(f"      - ✅ Time estimate: {action['time_estimate']} minutes")
                        
            else:
                print("   ❌ No actions extracted")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

def validate_multiple_inputs():
    """Validate multiple inputs from a file"""
    print("📁 Batch Validation from File")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not set in .env file")
        return
    
    # Initialize agent
    try:
        agent = TaskExtractionAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Setup sample tasks
    tasks = setup_sample_tasks()
    show_current_tasks(tasks)
    
    # Sample inputs for batch testing
    sample_inputs = [
        "I need to finish the documentation by tomorrow",
        "Mark the setup task as completed",
        "Update the code review to take 3 hours",
        "Add a subtask to documentation for user manual",
        "Move the unit tests deadline to next week",
        "I want to learn Docker basics by Friday",
        "The project documentation is done",
        "Change the review task priority to high"
    ]
    
    print(f"\n📋 Testing {len(sample_inputs)} sample inputs:")
    print("-" * 50)
    
    results = []
    for i, user_input in enumerate(sample_inputs, 1):
        print(f"\n🔍 Test {i}: \"{user_input}\"")
        
        try:
            actions = agent.extract_task(user_input, tasks)
            
            if actions:
                print(f"   ✅ Extracted {len(actions)} action(s)")
                for j, action in enumerate(actions, 1):
                    action_type = action.get('action', 'unknown')
                    print(f"      Action {j}: {action_type}")
                    
                    if action_type == 'add':
                        heading = action.get('heading', 'N/A')
                        print(f"         New task: {heading}")
                    elif action_type in ['edit', 'mark_done', 'reschedule', 'add_subtask']:
                        target = action.get('target_task', 'N/A')
                        print(f"         Target: {target}")
            else:
                print("   ❌ No actions extracted")
                
            results.append({
                'input': user_input,
                'actions': actions,
                'success': bool(actions)
            })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'input': user_input,
                'actions': [],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n📊 Batch Test Summary:")
    print("-" * 30)
    successful = sum(1 for r in results if r['success'])
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {len(results) - successful}/{len(results)}")
    
    if successful < len(results):
        print(f"\n❌ Failed inputs:")
        for result in results:
            if not result['success']:
                print(f"   - \"{result['input']}\"")
                if 'error' in result:
                    print(f"     Error: {result['error']}")

def main():
    """Main function"""
    print("🎯 TaskExtractionAgent Response Validator")
    print("=" * 50)
    
    while True:
        print("\nChoose validation mode:")
        print("1. Interactive (enter your own inputs)")
        print("2. Batch test (run predefined examples)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            validate_single_input()
        elif choice == '2':
            validate_multiple_inputs()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("⚠️  Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 