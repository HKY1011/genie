#!/usr/bin/env python3
"""
Debug script for PlanningAgent to understand API response format
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.planning_agent import PlanningAgent, PlanningAgentError
from integrations.perplexity_api import PerplexityAPIClient
from dotenv import load_dotenv

def debug_planning_agent():
    """Debug the planning agent to understand response format"""
    print("🔍 Debugging PlanningAgent API Response")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Test with actual planning agent
        print("1. Testing with actual PlanningAgent...")
        planning_agent = PlanningAgent()
        
        # Test with a simple task
        test_task = {
            "heading": "Learn Python Programming",
            "details": "I want to learn Python from scratch to build web applications and data analysis projects. I have no prior programming experience.",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "previous_chunks": [],
            "corrections_or_feedback": ""
        }
        
        print("2. Calling PlanningAgent.get_next_chunk()...")
        try:
            result = planning_agent.get_next_chunk(test_task)
            print("✅ PlanningAgent succeeded!")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ PlanningAgent failed: {e}")
            
            # Now test the API directly with the same prompt
            print("\n3. Testing Perplexity API directly with same prompt...")
            perplexity = PerplexityAPIClient()
            
            # Get the actual prompt that planning agent uses
            prompt = planning_agent._format_prompt(test_task)
            
            print("4. Calling Perplexity API...")
            response = perplexity.generate_content(prompt)
            
            print("5. Raw API Response:")
            print(response)
            print("\n" + "="*60)
            
            # Try to parse the response
            print("6. Attempting to parse response...")
            try:
                # Try to extract JSON from markdown code blocks if present
                json_str = response.strip()
                
                # Look for JSON blocks marked with ```json
                if "```json" in json_str:
                    start = json_str.find("```json") + 7
                    end = json_str.find("```", start)
                    if end == -1:
                        end = len(json_str)
                    json_str = json_str[start:end].strip()
                elif "```" in json_str:
                    # Extract JSON from generic code block
                    start = json_str.find("```") + 3
                    end = json_str.find("```", start)
                    if end == -1:
                        end = len(json_str)
                    json_str = json_str[start:end].strip()
                
                parsed_response = json.loads(json_str)
                print("✅ Successfully parsed response:")
                print(json.dumps(parsed_response, indent=2))
                
                # Check for required fields
                required_fields = ['chunk_heading', 'chunk_details', 'resource', 'estimated_time_minutes', 'chunk_order']
                missing_fields = []
                for field in required_fields:
                    if field not in parsed_response:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                else:
                    print("✅ All required fields present")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                print("Raw response that failed to parse:")
                print(json_str)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_planning_agent() 