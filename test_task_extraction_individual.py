#!/usr/bin/env python3
"""
Individual Task Extraction Test - Debug Script
Tests the task extraction agent in isolation to identify issues
"""

import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.task_extraction_agent import TaskExtractionAgent, TaskExtractionError
from integrations.gemini_api import GeminiAPIClient
from dotenv import load_dotenv

def test_task_extraction_individual():
    """Test task extraction agent individually"""
    print("🔍 Individual Task Extraction Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize task extraction agent
        print("1. Initializing TaskExtractionAgent...")
        extraction_agent = TaskExtractionAgent()
        print("✅ TaskExtractionAgent initialized successfully")
        
        # Test with a simple input
        test_input = "Build a React authentication system with JWT tokens"
        print(f"\n2. Testing with input: '{test_input}'")
        
        # Add delay to avoid rate limiting
        print("   ⏳ Waiting 2 seconds to avoid rate limiting...")
        time.sleep(2)
        
        # Test task extraction
        print("3. Calling extract_task...")
        actions = extraction_agent.extract_task(test_input, existing_tasks=[])
        
        print(f"4. Raw response: {actions}")
        print(f"   Type: {type(actions)}")
        print(f"   Length: {len(actions) if actions else 0}")
        
        if actions and len(actions) > 0:
            action = actions[0]
            print(f"\n5. First action details:")
            print(f"   Action type: {action.get('action_type', 'MISSING')}")
            print(f"   Action keys: {list(action.keys())}")
            
            # Check for task_data
            task_data = action.get('task_data', {})
            print(f"   Task data keys: {list(task_data.keys()) if task_data else 'NO TASK DATA'}")
            
            if task_data:
                print(f"   Task heading: {task_data.get('heading', 'MISSING')}")
                print(f"   Task details: {task_data.get('details', 'MISSING')[:100]}...")
            else:
                print("   ❌ No task_data found in action")
                
        else:
            print("❌ No actions returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_gemini_api_directly():
    """Test Gemini API directly to check for rate limiting"""
    print("\n🔍 Direct Gemini API Test")
    print("=" * 60)
    
    try:
        # Initialize Gemini API
        print("1. Initializing Gemini API...")
        gemini_client = GeminiAPIClient()
        print("✅ Gemini API initialized successfully")
        
        # Test simple request
        print("2. Testing simple request...")
        response = gemini_client.generate_content("Hello, this is a test.")
        print(f"✅ Simple request successful: {response[:100]}...")
        
        # Test with task extraction prompt
        print("3. Testing with task extraction prompt...")
        
        # Get the prompt template
        extraction_agent = TaskExtractionAgent()
        prompt = extraction_agent._format_prompt("Build a simple todo app", [])
        
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Prompt preview: {prompt[:200]}...")
        
        # Add delay
        print("   ⏳ Waiting 3 seconds to avoid rate limiting...")
        time.sleep(3)
        
        # Test with the actual prompt
        response = gemini_client.generate_content(prompt)
        print(f"✅ Task extraction prompt successful: {response[:200]}...")
        
        # Try to parse the response
        print("4. Attempting to parse response...")
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
                print(f"✅ Successfully parsed JSON: {parsed}")
            else:
                print("❌ No JSON found in response")
                print(f"   Response: {response}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"   Response: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_rate_limiting():
    """Test for rate limiting issues"""
    print("\n🔍 Rate Limiting Test")
    print("=" * 60)
    
    try:
        gemini_client = GeminiAPIClient()
        extraction_agent = TaskExtractionAgent()
        
        test_inputs = [
            "Build a React authentication system with JWT tokens",
            "Create a REST API for user management with Node.js and Express",
            "Design and implement a database schema for an e-commerce platform"
        ]
        
        for i, test_input in enumerate(test_inputs):
            print(f"\n{i+1}. Testing: '{test_input}'")
            
            try:
                # Add delay between requests
                if i > 0:
                    print("   ⏳ Waiting 5 seconds...")
                    time.sleep(5)
                
                actions = extraction_agent.extract_task(test_input, existing_tasks=[])
                
                if actions and len(actions) > 0:
                    action = actions[0]
                    action_type = action.get('action_type', 'unknown')
                    print(f"   ✅ Success - Action type: {action_type}")
                    
                    if action_type == 'unknown':
                        print(f"   ⚠️  Warning: Action type is 'unknown'")
                        print(f"   Action keys: {list(action.keys())}")
                else:
                    print(f"   ❌ No actions returned")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Individual Task Extraction Debug")
    print("=" * 80)
    
    # Run individual test
    test_task_extraction_individual()
    
    # Run direct API test
    test_gemini_api_directly()
    
    # Run rate limiting test
    test_rate_limiting()
    
    print("\n" + "=" * 80)
    print("🎯 Individual Task Extraction Debug Complete") 