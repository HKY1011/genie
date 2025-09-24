#!/usr/bin/env python3
"""
Debug script to identify feedback API issues
"""

import requests
import json
import time

def test_feedback_api():
    """Test the feedback API to identify issues"""
    base_url = "http://127.0.0.1:8080"
    
    print("🔍 Debugging Feedback API Issues")
    print("=" * 50)
    
    # Test 1: Check current subtask first
    print("\n1. Checking current subtask...")
    try:
        response = requests.get(f"{base_url}/api/current-subtask")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Try different feedback payloads
    feedback_payloads = [
        {
            "feedback_type": "done",
            "feedback_text": "Task completed successfully",
            "rating": 5,
            "user_id": "test_user"
        },
        {
            "feedback_type": "done",
            "feedback_text": "Task completed successfully",
            "rating": 5
        },
        {
            "feedback_type": "done",
            "feedback_text": "Task completed successfully"
        },
        {
            "feedback_type": "done"
        },
        {
            "feedback_type": "difficult",
            "feedback_text": "This was harder than expected",
            "rating": 3,
            "user_id": "test_user"
        }
    ]
    
    print("\n2. Testing different feedback payloads...")
    for i, payload in enumerate(feedback_payloads, 1):
        print(f"\n   Test {i}: {payload}")
        try:
            response = requests.post(f"{base_url}/api/feedback", json=payload)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {json.dumps(data, indent=2)}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        time.sleep(1)
    
    # Test 3: Check what the feedback API expects
    print("\n3. Checking feedback API endpoint...")
    try:
        response = requests.get(f"{base_url}/api/feedback")
        print(f"   GET Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_feedback_api() 