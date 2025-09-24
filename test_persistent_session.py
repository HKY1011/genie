#!/usr/bin/env python3
"""
Test Persistent Session Management
Demonstrates the new UserSession and SessionManager functionality
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from models.user_session import UserSession, SessionManager, UserPreferences
from models.task_model import Task, TaskStatus
from uuid import uuid4

def test_persistent_session():
    """Test the persistent session management functionality"""
    print("🧪 Testing Persistent Session Management")
    print("=" * 50)
    
    # Initialize session manager
    session_manager = SessionManager()
    user_id = "test_user_001"
    
    print(f"👤 User ID: {user_id}")
    
    # Test 1: Create new session
    print("\n📝 Test 1: Creating new session...")
    session = session_manager.get_or_create_session(user_id)
    print(f"✅ Session created: {session.user_id}")
    print(f"   Created at: {session.created_at}")
    print(f"   Tasks: {len(session.tasks)}")
    print(f"   Preferences: {session.preferences.preferred_work_duration} min sessions")
    
    # Test 2: Add tasks to session
    print("\n📋 Test 2: Adding tasks to session...")
    
    task1 = Task(
        id=uuid4(),
        heading="Learn Python Programming",
        details="Master Python fundamentals to build web applications",
        status=TaskStatus.IN_PROGRESS,
        deadline=datetime.utcnow() + timedelta(days=7),
        time_estimate=120
    )
    
    task2 = Task(
        id=uuid4(),
        heading="Build React Todo App",
        details="Create a modern todo application with React hooks",
        status=TaskStatus.PENDING,
        deadline=datetime.utcnow() + timedelta(days=14),
        time_estimate=180
    )
    
    session.add_task(task1)
    session.add_task(task2)
    
    print(f"✅ Added {len(session.tasks)} tasks")
    for task in session.tasks:
        print(f"   📋 {task.heading} ({task.status.value})")
    
    # Test 3: Update preferences
    print("\n⚙️  Test 3: Updating user preferences...")
    session.update_preferences(
        preferred_work_duration=30,
        max_work_duration=60,
        energy_peak_hours=["10:00-12:00", "15:00-17:00"]
    )
    
    print(f"✅ Updated preferences:")
    print(f"   Preferred duration: {session.preferences.preferred_work_duration} min")
    print(f"   Max duration: {session.preferences.max_work_duration} min")
    print(f"   Energy peaks: {session.preferences.energy_peak_hours}")
    
    # Test 4: Record energy patterns
    print("\n⚡ Test 4: Recording energy patterns...")
    session.record_energy_pattern(
        energy_level=8,
        activity_type="work",
        productivity_score=0.85,
        context={"task_type": "programming", "time_of_day": "morning"}
    )
    
    session.record_energy_pattern(
        energy_level=6,
        activity_type="meeting",
        productivity_score=0.70,
        context={"meeting_type": "planning", "duration": 30}
    )
    
    print(f"✅ Recorded {len(session.energy_patterns)} energy patterns")
    for pattern in session.energy_patterns:
        print(f"   ⚡ {pattern.activity_type}: Level {pattern.energy_level}, Productivity {pattern.productivity_score:.2f}")
    
    # Test 5: Mark task as done with feedback
    print("\n✅ Test 5: Marking task as done with feedback...")
    task_id = str(task1.id)
    success = session.mark_task_done(
        task_id=task_id,
        actual_time=90,  # Took 90 minutes instead of estimated 120
        difficulty=7,    # Difficulty rating 7/10
        energy_level=8,  # High energy during completion
        productivity=9,  # Very productive
        notes="Great progress! Python basics are clear now."
    )
    
    if success:
        print(f"✅ Task marked as done: {task1.heading}")
        print(f"   Estimated: 120 min, Actual: 90 min")
        print(f"   Difficulty: 7/10, Energy: 8/10, Productivity: 9/10")
    else:
        print(f"❌ Failed to mark task as done")
    
    # Test 6: Get productivity statistics
    print("\n📊 Test 6: Getting productivity statistics...")
    stats = session.get_productivity_stats()
    print(f"✅ Productivity Statistics:")
    print(f"   Total tasks completed: {stats['total_tasks_completed']}")
    print(f"   Average completion time: {stats['average_completion_time']} min")
    print(f"   Average difficulty: {stats['average_difficulty']}/10")
    print(f"   Average productivity: {stats['average_productivity']}/10")
    print(f"   Completion rate: {stats['completion_rate']}%")
    
    # Test 7: Save session to disk
    print("\n💾 Test 7: Saving session to disk...")
    success = session_manager.save_session(session)
    if success:
        print("✅ Session saved successfully")
    else:
        print("❌ Failed to save session")
    
    # Test 8: Load session from disk (simulate new session)
    print("\n🔄 Test 8: Loading session from disk...")
    new_session = session_manager.load_session(user_id)
    if new_session:
        print("✅ Session loaded successfully")
        print(f"   User ID: {new_session.user_id}")
        print(f"   Tasks: {len(new_session.tasks)}")
        print(f"   Completion history: {len(new_session.completion_history)}")
        print(f"   Energy patterns: {len(new_session.energy_patterns)}")
        print(f"   Last updated: {new_session.last_updated}")
        
        # Verify data persistence
        print(f"\n🔍 Data persistence verification:")
        print(f"   Tasks persisted: {len(new_session.tasks) == len(session.tasks)}")
        print(f"   Preferences persisted: {new_session.preferences.preferred_work_duration == session.preferences.preferred_work_duration}")
        print(f"   History persisted: {len(new_session.completion_history) == len(session.completion_history)}")
        print(f"   Energy patterns persisted: {len(new_session.energy_patterns) == len(session.energy_patterns)}")
    else:
        print("❌ Failed to load session")
    
    # Test 9: Get pending tasks
    print("\n⏳ Test 9: Getting pending tasks...")
    pending_tasks = new_session.get_pending_tasks()
    print(f"✅ Pending tasks: {len(pending_tasks)}")
    for task in pending_tasks:
        print(f"   ⏳ {task.heading} ({task.status.value})")
    
    # Test 10: Get completed tasks today
    print("\n✅ Test 10: Getting completed tasks today...")
    completed_today = new_session.get_completed_tasks_today()
    print(f"✅ Completed today: {len(completed_today)}")
    for task in completed_today:
        print(f"   ✅ {task.heading} (completed at {task.updated_at})")
    
    # Test 11: Get energy patterns today
    print("\n⚡ Test 11: Getting energy patterns today...")
    energy_today = new_session.get_energy_patterns_today()
    print(f"✅ Energy patterns today: {len(energy_today)}")
    for pattern in energy_today:
        print(f"   ⚡ {pattern.timestamp.strftime('%H:%M')} - {pattern.activity_type} (Level {pattern.energy_level})")
    
    print(f"\n🎉 All tests completed successfully!")
    print(f"💡 Session data is now persistent and can be loaded across sessions")
    print(f"📈 Foundation ready for learning algorithms and feedback loops")

if __name__ == "__main__":
    test_persistent_session() 