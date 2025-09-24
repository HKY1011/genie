#!/usr/bin/env python3
"""
Test script for PlanningAgent
Tests the PlanningAgent with sample tasks and validates responses.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.planning_agent import PlanningAgent, PlanningAgentError
from dotenv import load_dotenv


def test_planning_agent_initialization():
    """Test PlanningAgent initialization"""
    print("=== Testing PlanningAgent Initialization ===")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your_perplexity_api_key_here":
        print("⚠️  PERPLEXITY_API_KEY not set in .env file")
        print("   PlanningAgent will fail to initialize without a valid API key")
        return False
    
    try:
        agent = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
        
        # Get agent info
        info = agent.get_agent_info()
        print(f"Agent info: {info}")
        
        return True
        
    except PlanningAgentError as e:
        print(f"❌ Failed to initialize PlanningAgent: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_sample_tasks():
    """Test PlanningAgent with sample tasks"""
    print("\n=== Testing Sample Tasks ===")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your_perplexity_api_key_here":
        print("❌ PERPLEXITY_API_KEY not set. Cannot test with real API calls.")
        return False
    
    try:
        agent = PlanningAgent()
    except PlanningAgentError as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False
    
    # Sample tasks for testing
    sample_tasks = [
        {
            "heading": "Learn Python Programming",
            "details": "I want to learn Python from scratch to build web applications and data analysis projects. I have no prior programming experience.",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "previous_chunks": [],
            "corrections_or_feedback": ""
        },
        {
            "heading": "Build a Task Management App",
            "details": "Create a web application for managing personal tasks with features like task creation, deadlines, priority levels, and progress tracking.",
            "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "previous_chunks": [
                {"chunk_order": 1, "id": "chunk_1", "heading": "Setup development environment"}
            ],
            "corrections_or_feedback": "I prefer using React for the frontend"
        },
        {
            "heading": "Learn Machine Learning Basics",
            "details": "Understand fundamental machine learning concepts, algorithms, and how to implement them using Python libraries.",
            "deadline": (datetime.utcnow() + timedelta(days=21)).isoformat(),
            "previous_chunks": [],
            "available_time_blocks": [
                {"start": "09:00", "end": "11:00", "date": "2024-01-15", "timezone": "UTC"},
                {"start": "14:00", "end": "16:00", "date": "2024-01-16", "timezone": "UTC"}
            ],
            "corrections_or_feedback": ""
        }
    ]
    
    successful_tests = 0
    total_tests = len(sample_tasks)
    
    for i, task in enumerate(sample_tasks, 1):
        print(f"\n--- Test {i}: {task['heading']} ---")
        
        try:
            # Get next chunk
            chunk = agent.get_next_chunk(task)
            
            print(f"✅ Successfully generated chunk:")
            print(f"   Heading: {chunk['chunk_heading']}")
            print(f"   Time: {chunk['estimated_time_minutes']} minutes")
            print(f"   Order: {chunk['chunk_order']}")
            print(f"   Resource: {chunk['resource']['title']}")
            print(f"   Resource Type: {chunk['resource']['type']}")
            print(f"   Paid: {chunk['resource']['paid']}")
            
            if chunk.get('impossibility_warning'):
                print(f"   ⚠️  Warning: {chunk['impossibility_warning']}")
            
            successful_tests += 1
            
        except PlanningAgentError as e:
            print(f"❌ PlanningAgent error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print(f"\n=== Test Summary ===")
    print(f"Successful: {successful_tests}/{total_tests}")
    
    return successful_tests == total_tests


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n=== Testing Error Handling ===")
    
    # Load environment variables
    load_dotenv()
    
    try:
        agent = PlanningAgent()
    except PlanningAgentError:
        print("⚠️  Skipping error handling tests - agent not initialized")
        return True
    
    # Test cases for error handling
    error_test_cases = [
        {
            "name": "Missing heading",
            "task": {"details": "Some details"},
            "expected_error": "Missing required field: heading"
        },
        {
            "name": "Empty details",
            "task": {"heading": "Test task", "details": ""},
            "expected_error": "Field 'details' cannot be empty"
        },
        {
            "name": "Invalid deadline format",
            "task": {"heading": "Test task", "details": "Test details", "deadline": "invalid-date"},
            "expected_error": "Invalid deadline format"
        },
        {
            "name": "Invalid previous_chunks type",
            "task": {"heading": "Test task", "details": "Test details", "previous_chunks": "not-a-list"},
            "expected_error": "previous_chunks must be a list"
        }
    ]
    
    error_tests_passed = 0
    total_error_tests = len(error_test_cases)
    
    for test_case in error_test_cases:
        print(f"\n--- Error Test: {test_case['name']} ---")
        
        try:
            agent.get_next_chunk(test_case['task'])
            print(f"❌ Expected error but got success")
            
        except PlanningAgentError as e:
            if test_case['expected_error'] in str(e):
                print(f"✅ Correctly caught error: {e}")
                error_tests_passed += 1
            else:
                print(f"❌ Unexpected error: {e}")
        except Exception as e:
            print(f"❌ Unexpected exception: {e}")
    
    print(f"\nError handling tests: {error_tests_passed}/{total_error_tests} passed")
    return error_tests_passed == total_error_tests


def main():
    """Run all tests"""
    print("🎯 PlanningAgent Test Suite")
    print("=" * 50)
    
    # Test initialization
    init_success = test_planning_agent_initialization()
    
    # Test sample tasks (only if API key is available)
    if init_success:
        tasks_success = test_sample_tasks()
    else:
        tasks_success = False
        print("\n⚠️  Skipping sample task tests due to initialization failure")
    
    # Test error handling
    error_success = test_error_handling()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  Initialization: {'✅ Passed' if init_success else '❌ Failed'}")
    print(f"  Sample Tasks: {'✅ Passed' if tasks_success else '❌ Failed'}")
    print(f"  Error Handling: {'✅ Passed' if error_success else '❌ Failed'}")
    
    if init_success and tasks_success and error_success:
        print("\n🎉 All tests passed! PlanningAgent is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main()) 