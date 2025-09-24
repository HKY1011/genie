#!/usr/bin/env python3
"""
Debug script to test prompt formatting
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from models.task_model import Task, TaskStatus
from agents.task_extraction_agent import TaskExtractionAgent


def debug_prompt():
    """Debug the prompt formatting"""
    print("=== Debugging Prompt Format ===")
    
    # Create a simple task
    task = Task(
        heading="Test task",
        details="This is a test task",
        time_estimate=30
    )
    
    # Initialize agent
    agent = TaskExtractionAgent()
    
    # Test the prompt formatting
    user_input = "Add a new task to learn Python"
    existing_tasks = [task]
    
    try:
        prompt = agent._format_prompt(user_input, existing_tasks)
        print("Formatted prompt:")
        print("=" * 50)
        print(prompt)
        print("=" * 50)
        
        # Test JSON parsing
        print("\nTesting JSON parsing...")
        import json
        
        # Simulate a response that might cause issues
        test_response = '''
        [
          {
            "action": "add",
            "heading": "Learn Python",
            "details": "Study Python programming language",
            "deadline": null
          }
        ]
        '''
        
        parsed = json.loads(test_response)
        print(f"✅ JSON parsing successful: {parsed}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_prompt() 