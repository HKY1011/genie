#!/usr/bin/env python3
"""
Simple PlanningAgent Test
Demonstrates PlanningAgent functionality and structure.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from agents.planning_agent import PlanningAgent, PlanningAgentError

def demonstrate_planning_agent():
    """Demonstrate PlanningAgent structure and functionality"""
    print("🎯 PlanningAgent Demonstration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    print("📋 PlanningAgent Features:")
    print("  ✅ Breaks down high-level tasks into manageable chunks")
    print("  ✅ Uses Perplexity API for research and resource finding")
    print("  ✅ Provides specific, actionable steps (25-45 minutes)")
    print("  ✅ Recommends high-quality resources with exact sections")
    print("  ✅ Adapts to user feedback and deadline changes")
    print("  ✅ Validates input and output structures")
    
    print("\n📝 Input Structure:")
    print("  - heading: Task title (required)")
    print("  - details: Task description (required)")
    print("  - deadline: ISO 8601 deadline (optional)")
    print("  - previous_chunks: List of completed chunks (optional)")
    print("  - available_time_blocks: User's available time (optional)")
    print("  - corrections_or_feedback: User feedback (optional)")
    
    print("\n📤 Output Structure:")
    print("  - chunk_heading: Next step title")
    print("  - chunk_details: Detailed instructions")
    print("  - resource: Resource information (title, URL, type, etc.)")
    print("  - estimated_time_minutes: Time estimate (15-120 min)")
    print("  - chunk_order: Sequence number")
    print("  - deadline: Chunk-specific deadline (optional)")
    print("  - impossibility_warning: Warning if plan impossible (optional)")
    
    print("\n🔧 Error Handling:")
    print("  ✅ Input validation (required fields, data types)")
    print("  ✅ Response validation (structure, field types)")
    print("  ✅ API error handling (network, rate limits)")
    print("  ✅ JSON parsing error handling")
    
    # Test initialization (will fail without API key, but shows structure)
    print("\n🧪 Testing Initialization:")
    try:
        agent = PlanningAgent()
        print("  ✅ PlanningAgent initialized successfully")
        
        info = agent.get_agent_info()
        print(f"  📊 Agent Info: {info}")
        
    except PlanningAgentError as e:
        print(f"  ⚠️  Expected error (no API key): {e}")
        print("  💡 Add PERPLEXITY_API_KEY to .env file to test with real API")
        
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
    
    print("\n💡 Usage Example:")
    print("""
    # Initialize agent
    agent = PlanningAgent()
    
    # Create task
    task = {
        "heading": "Learn Python Programming",
        "details": "I want to learn Python from scratch to build web applications",
        "deadline": "2024-02-15T23:59:59",
        "previous_chunks": [],
        "corrections_or_feedback": ""
    }
    
    # Get next chunk
    chunk = agent.get_next_chunk(task)
    print(f"Next step: {chunk['chunk_heading']}")
    print(f"Time: {chunk['estimated_time_minutes']} minutes")
    print(f"Resource: {chunk['resource']['title']}")
    """)

if __name__ == "__main__":
    demonstrate_planning_agent() 