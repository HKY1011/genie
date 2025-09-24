#!/usr/bin/env python3
"""
Debug script for GenieOrchestrator
Tests the orchestrator step by step to identify issues.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents.genieorchestrator_agent import GenieOrchestrator
from integrations.gemini_api import GeminiAPIClient
from dotenv import load_dotenv

def debug_orchestrator():
    """Debug the GenieOrchestrator step by step"""
    print("🔍 Debugging GenieOrchestrator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test 1: Check Gemini API directly
    print("\n1. Testing Gemini API directly...")
    try:
        gemini_client = GeminiAPIClient()
        print("✅ Gemini API client created")
        
        # Test simple prompt
        response = gemini_client.generate_content("Say 'Hello World'")
        print(f"✅ Gemini API response: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return
    
    # Test 2: Check GenieOrchestrator initialization
    print("\n2. Testing GenieOrchestrator initialization...")
    try:
        orchestrator = GenieOrchestrator()
        print("✅ GenieOrchestrator initialized")
        
        info = orchestrator.get_agent_info()
        print(f"📊 Agent info: {info}")
        
    except Exception as e:
        print(f"❌ GenieOrchestrator error: {e}")
        return
    
    # Test 3: Check prompt template
    print("\n3. Testing prompt template...")
    try:
        prompt_template = orchestrator.prompt_template
        print(f"✅ Prompt template loaded ({len(prompt_template)} characters)")
        print(f"📝 Template preview: {prompt_template[:200]}...")
        
    except Exception as e:
        print(f"❌ Prompt template error: {e}")
        return
    
    # Test 4: Create sample data
    print("\n4. Creating sample data...")
    try:
        # Simple test data
        all_tasks_json = json.dumps({
            "tasks": [
                {
                    "id": "task_1",
                    "heading": "Test Task",
                    "details": "A simple test task",
                    "deadline": "2024-02-15T23:59:59",
                    "priority_score": 8.0,
                    "subtasks": [
                        {
                            "id": "chunk_1",
                            "heading": "Test Chunk",
                            "details": "A simple test chunk",
                            "estimated_time_minutes": 30,
                            "status": "pending",
                            "resource": {
                                "title": "Test Resource",
                                "url": "https://example.com",
                                "type": "article",
                                "focus_section": "Section 1",
                                "paid": False
                            },
                            "dependencies": [],
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
                }
            ],
            "preferences": {
                "preferred_work_duration": 45,
                "max_work_duration": 90
            },
            "timezone": "UTC"
        })
        
        print("✅ Sample data created")
        print(f"📋 Tasks JSON length: {len(all_tasks_json)}")
        print(f"📅 Schedule JSON length: {len(user_schedule_json)}")
        
    except Exception as e:
        print(f"❌ Sample data error: {e}")
        return
    
    # Test 5: Test prompt formatting
    print("\n5. Testing prompt formatting...")
    try:
        formatted_prompt = orchestrator._format_prompt(all_tasks_json, user_schedule_json)
        print(f"✅ Prompt formatted ({len(formatted_prompt)} characters)")
        print(f"📝 Formatted prompt preview: {formatted_prompt[-200:]}...")
        
    except Exception as e:
        print(f"❌ Prompt formatting error: {e}")
        return
    
    # Test 6: Test API call with formatted prompt
    print("\n6. Testing API call with formatted prompt...")
    try:
        response_text = orchestrator.gemini_client.generate_content(formatted_prompt)
        print(f"✅ API response received ({len(response_text)} characters)")
        print(f"📝 Response preview: {response_text[:200]}...")
        
        if not response_text.strip():
            print("⚠️  Warning: Empty response from API")
        else:
            # Try to parse as JSON
            try:
                response_data = json.loads(response_text.strip())
                print("✅ Response parsed as JSON successfully")
                print(f"📊 Response keys: {list(response_data.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"📝 Raw response: {response_text}")
        
    except Exception as e:
        print(f"❌ API call error: {e}")
        return
    
    print("\n✅ Debug completed!")

if __name__ == "__main__":
    debug_orchestrator() 