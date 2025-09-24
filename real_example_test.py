#!/usr/bin/env python3
"""
Real Example Test for TaskExtractionAgent
Shows actual responses from the agent with real user inputs.
"""

import sys
import os
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
        )
    ]
    return tasks

def test_real_examples():
    """Test with real user input examples"""
    print("🎯 Real Example Test - TaskExtractionAgent")
    print("=" * 60)
    
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
    print(f"✅ Created {len(tasks)} sample tasks")
    
    # Real user input examples
    examples = [
        {
            "description": "Adding a new task",
            "input": "I need to learn React by next Friday for my new project",
            "expected": "Should extract a new task with deadline"
        },
        {
            "description": "Marking a task as done",
            "input": "Mark the documentation task as completed",
            "expected": "Should mark the documentation task as done"
        },
        {
            "description": "Editing an existing task",
            "input": "Update the code review task to have a 2-hour time estimate",
            "expected": "Should update the time estimate of the code review task"
        },
        {
            "description": "Adding a subtask",
            "input": "Add a subtask to the documentation task to create API documentation",
            "expected": "Should add a subtask to the documentation task"
        },
        {
            "description": "Rescheduling a task",
            "input": "Move the documentation deadline to next Monday",
            "expected": "Should reschedule the documentation task deadline"
        },
        {
            "description": "Complex request with multiple actions",
            "input": "I need to learn Python basics by tomorrow, and also mark the setup task as done",
            "expected": "Should create a new task and mark setup task as done"
        }
    ]
    
    print(f"\n📋 Testing {len(examples)} real examples:")
    print("-" * 60)
    
    for i, example in enumerate(examples, 1):
        print(f"\n🔍 Example {i}: {example['description']}")
        print(f"📝 Input: \"{example['input']}\"")
        print(f"🎯 Expected: {example['expected']}")
        
        try:
            # Get agent response
            actions = agent.extract_task(example['input'], tasks)
            
            print(f"🤖 Agent Response:")
            if actions:
                for j, action in enumerate(actions, 1):
                    print(f"   Action {j}:")
                    for key, value in action.items():
                        if key == 'subtask' and isinstance(value, dict):
                            print(f"     {key}:")
                            for subkey, subvalue in value.items():
                                print(f"       {subkey}: {subvalue}")
                        else:
                            print(f"     {key}: {value}")
            else:
                print("   ❌ No actions extracted")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 40)

def show_current_tasks():
    """Show the current sample tasks"""
    print("\n📋 Current Sample Tasks:")
    print("-" * 40)
    
    tasks = setup_sample_tasks()
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.heading}")
        print(f"   Status: {task.status.value}")
        print(f"   Time: {task.time_estimate} min")
        if task.deadline:
            print(f"   Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Details: {task.details[:50]}...")
        print()

def main():
    """Run the real example test"""
    print("🚀 Starting Real Example Test")
    print("This will show actual TaskExtractionAgent responses")
    print()
    
    # Show current tasks first
    show_current_tasks()
    
    # Run the test
    test_real_examples()
    
    print("\n" + "=" * 60)
    print("✅ Real example test completed!")
    print("\n💡 Tips:")
    print("- The agent should extract structured actions from natural language")
    print("- Each action should have the correct 'action' type")
    print("- Task references should match existing tasks by ID or heading")
    print("- New tasks should have proper headings and details")

if __name__ == "__main__":
    main() 