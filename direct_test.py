#!/usr/bin/env python3
"""
Direct Test - Simple way to test TaskExtractionAgent directly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from models.task_model import Task, TaskStatus
from agents.task_extraction_agent import TaskExtractionAgent

# Load environment variables
load_dotenv()

# Create a simple task
task = Task("Write documentation", "Create project docs")

# Initialize agent
agent = TaskExtractionAgent()

# Test directly
user_input = "I need to learn Python by Friday"
print(f"Input: {user_input}")
print(f"Existing task: {task.heading}")

# Get response
actions = agent.extract_task(user_input, [task])
print(f"Response: {actions}") 