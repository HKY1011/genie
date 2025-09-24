#!/usr/bin/env python3
"""
Test Simplified Planning Agent
Tests the new approach where Perplexity handles all complexity analysis and subtask count determination.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.planning_agent import PlanningAgent, PlanningAgentError


def test_perplexity_complexity_analysis():
    """Test that Perplexity handles complexity analysis"""
    print("🔍 Testing Perplexity Complexity Analysis")
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
            'name': 'Simple Task (No Subtasks)',
            'task': {
                'heading': 'Send email to client',
                'details': 'Send follow-up email to client about project status',
                'time_estimate': 15
            }
        },
        {
            'name': 'Medium Task (Few Subtasks)',
            'task': {
                'heading': 'Create login form',
                'details': 'Build a user authentication form with validation',
                'time_estimate': 60
            }
        },
        {
            'name': 'Complex Task (Many Subtasks)',
            'task': {
                'heading': 'Build full-stack e-commerce platform',
                'details': 'Develop a complete e-commerce system with user management, product catalog, shopping cart, and payment processing',
                'time_estimate': 480
            }
        }
    ]
    
    results = []
    
    for test_case in test_tasks:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"   Task: {test_case['task']['heading']}")
        
        try:
            task_id = f"test_{test_case['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}"
            
            # Generate subtasks using Perplexity
            subtasks = planner.generate_initial_subtasks(test_case['task'], task_id)
            
            print(f"   🔍 Perplexity Analysis Results:")
            print(f"      📊 Subtasks Generated: {len(subtasks)}")
            
            if len(subtasks) == 0:
                print(f"      💡 Decision: No subtasks needed - direct execution")
            elif len(subtasks) <= 5:
                print(f"      📋 Decision: {len(subtasks)} subtasks - no replenishment needed")
            else:
                print(f"      🔄 Decision: {len(subtasks)} subtasks - will replenish as needed")
            
            # Display subtasks if any
            for i, subtask in enumerate(subtasks[:3], 1):  # Show first 3
                print(f"      {i}. {subtask['chunk_heading']} ({subtask['estimated_time_minutes']} min)")
            
            if len(subtasks) > 3:
                print(f"      ... and {len(subtasks) - 3} more subtasks")
            
            results.append((test_case['name'], len(subtasks), True))
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((test_case['name'], 0, False))
    
    # Summary
    print(f"\n📊 Perplexity Analysis Summary:")
    print("=" * 40)
    
    for name, subtask_count, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {name}: {subtask_count} subtasks - {status}")
    
    return all(success for _, _, success in results)


def test_replenishment_logic():
    """Test the new replenishment logic (only when subtasks > 5)"""
    print("\n🔄 Testing Replenishment Logic")
    print("=" * 50)
    
    # Initialize PlanningAgent
    try:
        planner = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PlanningAgent: {e}")
        return False
    
    # Test task that should generate many subtasks
    test_task = {
        'heading': 'Master full-stack web development',
        'details': 'Learn complete web development including frontend, backend, database, deployment, and advanced concepts',
        'time_estimate': 600
    }
    
    task_id = "test_replenishment"
    
    print(f"📋 Testing replenishment with: {test_task['heading']}")
    
    try:
        # Generate initial subtasks
        subtasks = planner.generate_initial_subtasks(test_task, task_id)
        
        print(f"✅ Generated {len(subtasks)} initial subtasks")
        
        # Test replenishment logic
        if len(subtasks) > 5:
            print(f"📊 Task has {len(subtasks)} subtasks > 5 - replenishment will be enabled")
            
            # Complete first few subtasks and test replenishment
            for i in range(min(3, len(subtasks))):
                subtask = subtasks[i]
                print(f"\n✅ Marking subtask {subtask['chunk_order']} as completed...")
                
                new_subtask = planner.mark_subtask_completed(task_id, subtask['chunk_order'])
                
                if new_subtask:
                    print(f"🔄 Generated new subtask: {new_subtask['chunk_heading']}")
                else:
                    print("ℹ️  No new subtask generated")
            
            # Check final state
            final_subtasks = planner.get_visible_subtasks(task_id)
            print(f"\n📊 Final state: {len(final_subtasks)} visible subtasks")
            
        else:
            print(f"📊 Task has {len(subtasks)} subtasks ≤ 5 - no replenishment needed")
            
            # Test that no replenishment happens
            if subtasks:
                subtask = subtasks[0]
                print(f"\n✅ Marking subtask {subtask['chunk_order']} as completed...")
                
                new_subtask = planner.mark_subtask_completed(task_id, subtask['chunk_order'])
                
                if new_subtask:
                    print(f"⚠️  Unexpected: Generated new subtask despite ≤ 5 total")
                else:
                    print(f"✅ Correct: No replenishment (≤ 5 subtasks)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in replenishment test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zero_subtasks():
    """Test tasks that should have 0 subtasks"""
    print("\n🚫 Testing Zero Subtasks")
    print("=" * 50)
    
    # Initialize PlanningAgent
    try:
        planner = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PlanningAgent: {e}")
        return False
    
    # Test simple tasks that shouldn't need subtasks
    simple_tasks = [
        {
            'name': 'Send Email',
            'task': {
                'heading': 'Send email to John',
                'details': 'Send a quick email to John about the meeting tomorrow',
                'time_estimate': 5
            }
        },
        {
            'name': 'Make Phone Call',
            'task': {
                'heading': 'Call client',
                'details': 'Call the client to confirm the project timeline',
                'time_estimate': 10
            }
        }
    ]
    
    for test_case in simple_tasks:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"   Task: {test_case['task']['heading']}")
        
        try:
            task_id = f"test_zero_{test_case['name'].lower().replace(' ', '_')}"
            
            # Generate subtasks using Perplexity
            subtasks = planner.generate_initial_subtasks(test_case['task'], task_id)
            
            print(f"   🔍 Perplexity Decision:")
            print(f"      📊 Subtasks Generated: {len(subtasks)}")
            
            if len(subtasks) == 0:
                print(f"      ✅ Correct: No subtasks needed for simple task")
            else:
                print(f"      ℹ️  Perplexity decided {len(subtasks)} subtasks are needed")
                for i, subtask in enumerate(subtasks, 1):
                    print(f"         {i}. {subtask['chunk_heading']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """Run all tests"""
    print("🧪 Simplified Planning Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("Perplexity Complexity Analysis", test_perplexity_complexity_analysis),
        ("Replenishment Logic", test_replenishment_logic),
        ("Zero Subtasks", test_zero_subtasks)
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
        print("🚀 All tests passed! Simplified PlanningAgent is working correctly.")
        print("💡 Perplexity now handles all complexity analysis and subtask count determination.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    main() 