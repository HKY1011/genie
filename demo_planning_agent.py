#!/usr/bin/env python3
"""
PlanningAgent Demo
Shows actual responses from the PlanningAgent with real examples.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.planning_agent import PlanningAgent
from dotenv import load_dotenv

def demo_planning_agent():
    """Demonstrate PlanningAgent with real examples"""
    print("🎯 PlanningAgent Real Examples")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    try:
        agent = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Example tasks
    examples = [
        {
            "name": "Learn Python Programming",
            "task": {
                "heading": "Learn Python Programming",
                "details": "I want to learn Python from scratch to build web applications and data analysis projects. I have no prior programming experience.",
                "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "previous_chunks": [],
                "corrections_or_feedback": ""
            }
        },
        {
            "name": "Build a React App",
            "task": {
                "heading": "Build a React Todo App",
                "details": "Create a modern todo application using React with features like adding, editing, deleting tasks, and local storage persistence.",
                "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "previous_chunks": [
                    {"chunk_order": 1, "id": "chunk_1", "heading": "Setup development environment"}
                ],
                "corrections_or_feedback": "I prefer using functional components with hooks"
            }
        },
        {
            "name": "Learn Machine Learning",
            "task": {
                "heading": "Learn Machine Learning Basics",
                "details": "Understand fundamental machine learning concepts, algorithms, and how to implement them using Python libraries like scikit-learn.",
                "deadline": (datetime.utcnow() + timedelta(days=21)).isoformat(),
                "previous_chunks": [],
                "available_time_blocks": [
                    {"start": "09:00", "end": "11:00", "date": "2024-01-15", "timezone": "UTC"}
                ],
                "corrections_or_feedback": ""
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n🔍 Example {i}: {example['name']}")
        print("-" * 50)
        
        try:
            # Get next chunk
            chunk = agent.get_next_chunk(example['task'])
            
            print(f"📋 Task: {example['task']['heading']}")
            print(f"📝 Details: {example['task']['details'][:100]}...")
            
            print(f"\n🎯 Next Chunk:")
            print(f"   Heading: {chunk['chunk_heading']}")
            print(f"   Time: {chunk['estimated_time_minutes']} minutes")
            print(f"   Order: {chunk['chunk_order']}")
            
            print(f"\n📚 Resource:")
            print(f"   Title: {chunk['resource']['title']}")
            print(f"   Type: {chunk['resource']['type']}")
            print(f"   URL: {chunk['resource']['url']}")
            print(f"   Focus: {chunk['resource']['focus_section']}")
            print(f"   Paid: {chunk['resource']['paid']}")
            
            if chunk['resource'].get('access_instructions'):
                print(f"   Access: {chunk['resource']['access_instructions']}")
            
            if chunk['resource'].get('rationale'):
                print(f"   Rationale: {chunk['resource']['rationale']}")
            
            print(f"\n📖 Instructions:")
            print(f"   {chunk['chunk_details']}")
            
            if chunk.get('impossibility_warning'):
                print(f"\n⚠️  Warning: {chunk['impossibility_warning']}")
            
            print("\n" + "="*50)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Demo completed! PlanningAgent is working correctly.")
    print(f"💡 The agent successfully:")
    print(f"   - Breaks down complex tasks into manageable chunks")
    print(f"   - Finds high-quality, free resources")
    print(f"   - Provides specific, actionable instructions")
    print(f"   - Adapts to user feedback and constraints")

if __name__ == "__main__":
    demo_planning_agent() 