#!/usr/bin/env python3
"""
Test Enhanced Planning Agent
Tests the new batch subtask generation, complexity analysis, and context tracking features.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.planning_agent import PlanningAgent, PlanningAgentError


def test_task_complexity_analysis():
    """Test task complexity analysis functionality"""
    print("🔍 Testing Task Complexity Analysis")
    print("=" * 50)
    
    # Initialize PlanningAgent
    try:
        planner = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PlanningAgent: {e}")
        return False
    
    # Test cases with different complexity levels
    test_tasks = [
        {
            'name': 'Simple Task',
            'task': {
                'heading': 'Send email to client',
                'details': 'Send follow-up email to client about project status',
                'time_estimate': 15
            }
        },
        {
            'name': 'Medium Task',
            'task': {
                'heading': 'Create login form',
                'details': 'Build a user authentication form with validation',
                'time_estimate': 60
            }
        },
        {
            'name': 'Complex Task',
            'task': {
                'heading': 'Build full-stack e-commerce platform',
                'details': 'Develop a complete e-commerce system with user management, product catalog, shopping cart, and payment processing',
                'time_estimate': 480
            }
        }
    ]
    
    for test_case in test_tasks:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"   Task: {test_case['task']['heading']}")
        
        try:
            # Analyze complexity
            complexity = planner._analyze_task_complexity(test_case['task'])
            
            print(f"   🔍 Complexity Level: {complexity['complexity_level']}")
            print(f"   📊 Total Subtasks Needed: {complexity['total_subtasks_needed']}")
            print(f"   🎯 Initial Subtasks: {complexity['initial_subtasks']}")
            print(f"   💡 Reasoning: {complexity['reasoning']}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing complexity: {e}")
            return False
    
    print("\n✅ Task complexity analysis tests completed")
    return True


def test_batch_subtask_generation():
    """Test batch subtask generation functionality"""
    print("\n🔄 Testing Batch Subtask Generation")
    print("=" * 50)
    
    # Initialize PlanningAgent
    try:
        planner = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PlanningAgent: {e}")
        return False
    
    # Test task
    test_task = {
        'heading': 'Create React authentication system',
        'details': 'Build a complete authentication system with login, registration, and JWT token management',
        'time_estimate': 120
    }
    
    task_id = "test_task_001"
    
    print(f"📋 Testing batch generation for: {test_task['heading']}")
    
    try:
        # Generate initial subtasks
        subtasks = planner.generate_initial_subtasks(test_task, task_id)
        
        print(f"✅ Generated {len(subtasks)} initial subtasks")
        
        # Display generated subtasks
        for i, subtask in enumerate(subtasks, 1):
            print(f"\n   Subtask {i}:")
            print(f"      📝 Heading: {subtask['chunk_heading']}")
            print(f"      ⏱️  Time: {subtask['estimated_time_minutes']} minutes")
            print(f"      🔗 Resource: {subtask['resource']['title']}")
            print(f"      📋 Order: {subtask['chunk_order']}")
        
        # Test getting visible subtasks
        visible_subtasks = planner.get_visible_subtasks(task_id)
        print(f"\n👁️  Visible subtasks: {len(visible_subtasks)}")
        
        # Test marking subtask as completed
        if subtasks:
            first_subtask = subtasks[0]
            print(f"\n✅ Marking subtask {first_subtask['chunk_order']} as completed...")
            
            new_subtask = planner.mark_subtask_completed(task_id, first_subtask['chunk_order'])
            
            if new_subtask:
                print(f"🔄 Generated new subtask: {new_subtask['chunk_heading']}")
            else:
                print("ℹ️  No new subtask generated (pool still has enough)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in batch generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_tracking():
    """Test context tracking and subtask management"""
    print("\n🧠 Testing Context Tracking")
    print("=" * 50)
    
    # Initialize PlanningAgent
    try:
        planner = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PlanningAgent: {e}")
        return False
    
    # Test task
    test_task = {
        'heading': 'Learn Python web development',
        'details': 'Master Python web development with Flask and database integration',
        'time_estimate': 180
    }
    
    task_id = "test_task_002"
    
    print(f"📋 Testing context tracking for: {test_task['heading']}")
    
    try:
        # Generate initial subtasks
        subtasks = planner.generate_initial_subtasks(test_task, task_id)
        print(f"✅ Generated {len(subtasks)} initial subtasks")
        
        # Check internal state
        print(f"\n📊 Internal State:")
        print(f"   Subtask pools: {len(planner.subtask_pools)}")
        print(f"   Completed subtasks: {len(planner.completed_subtasks)}")
        print(f"   Visible subtasks: {len(planner.visible_subtasks)}")
        
        # Test completing multiple subtasks
        for i in range(min(3, len(subtasks))):
            subtask = subtasks[i]
            print(f"\n✅ Marking subtask {subtask['chunk_order']} as completed...")
            
            new_subtask = planner.mark_subtask_completed(task_id, subtask['chunk_order'])
            
            if new_subtask:
                print(f"🔄 Generated new subtask: {new_subtask['chunk_heading']}")
            else:
                print("ℹ️  No new subtask generated")
        
        # Check final state
        print(f"\n📊 Final State:")
        print(f"   Total subtasks in pool: {len(planner.subtask_pools[task_id])}")
        print(f"   Completed subtasks: {planner.completed_subtasks[task_id]}")
        print(f"   Visible subtasks: {len(planner.get_visible_subtasks(task_id))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in context tracking: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🧪 Enhanced Planning Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("Task Complexity Analysis", test_task_complexity_analysis),
        ("Batch Subtask Generation", test_batch_subtask_generation),
        ("Context Tracking", test_context_tracking)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🎯 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎉 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🚀 All tests passed! Enhanced PlanningAgent is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    main() 