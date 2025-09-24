#!/usr/bin/env python3
"""
Test script for Task data model and JsonStore functionality
This script demonstrates and verifies data integrity and persistence.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from models.task_model import Task, TaskStatus
from storage.json_store import JsonStore


def test_task_creation():
    """Test basic task creation and properties"""
    print("=== Testing Task Creation ===")
    
    # Create a simple task
    task = Task(
        heading="Complete project documentation",
        details="Write comprehensive documentation for the genie_backend project",
        time_estimate=120,  # 2 hours
        resource_link="https://docs.python.org/3/"
    )
    
    print(f"Created task: {task}")
    print(f"Task ID: {task.id}")
    print(f"Status: {task.status}")
    print(f"Created at: {task.created_at}")
    print(f"Updated at: {task.updated_at}")
    print(f"Time estimate: {task.time_estimate} minutes")
    print(f"Resource link: {task.resource_link}")
    print()
    
    return task


def test_task_with_deadline():
    """Test task creation with deadline"""
    print("=== Testing Task with Deadline ===")
    
    deadline = datetime.utcnow() + timedelta(days=7)
    task = Task(
        heading="Review code changes",
        details="Review all pending pull requests and provide feedback",
        deadline=deadline,
        time_estimate=60,
        status=TaskStatus.IN_PROGRESS
    )
    
    print(f"Created task with deadline: {task}")
    print(f"Deadline: {task.deadline}")
    print(f"Status: {task.status}")
    print()
    
    return task


def test_subtasks():
    """Test task with subtasks"""
    print("=== Testing Subtasks ===")
    
    # Create main task
    main_task = Task(
        heading="Build web application",
        details="Create a full-stack web application with React frontend and Python backend",
        time_estimate=480  # 8 hours
    )
    
    # Create subtasks
    subtask1 = Task(
        heading="Set up project structure",
        details="Create directories and initialize git repository",
        time_estimate=30
    )
    
    subtask2 = Task(
        heading="Implement backend API",
        details="Create RESTful API endpoints using FastAPI",
        time_estimate=240
    )
    
    subtask3 = Task(
        heading="Build frontend components",
        details="Create React components for user interface",
        time_estimate=210
    )
    
    # Add subtasks to main task
    main_task.add_subtask(subtask1)
    main_task.add_subtask(subtask2)
    main_task.add_subtask(subtask3)
    
    print(f"Main task: {main_task}")
    print(f"Number of subtasks: {len(main_task.subtasks)}")
    for i, subtask in enumerate(main_task.subtasks, 1):
        print(f"  Subtask {i}: {subtask.heading} ({subtask.time_estimate} min)")
    print()
    
    return main_task


def test_task_serialization():
    """Test task serialization to/from dictionary"""
    print("=== Testing Task Serialization ===")
    
    # Create a complex task with subtasks
    task = test_subtasks()
    
    # Convert to dictionary
    task_dict = task.to_dict()
    print("Task converted to dictionary:")
    print(f"Keys: {list(task_dict.keys())}")
    print(f"Status: {task_dict['status']}")
    print(f"Number of subtasks: {len(task_dict['subtasks'])}")
    
    # Convert back to task
    reconstructed_task = Task.from_dict(task_dict)
    print(f"\nReconstructed task: {reconstructed_task}")
    print(f"Number of subtasks: {len(reconstructed_task.subtasks)}")
    print(f"Status: {reconstructed_task.status}")
    print()
    
    return task


def test_json_store():
    """Test JsonStore functionality"""
    print("=== Testing JsonStore ===")
    
    # Initialize store with test directory
    test_storage_dir = "test_data"
    store = JsonStore(storage_dir=test_storage_dir)
    
    print(f"Storage info: {store.get_storage_info()}")
    print(f"Initial task count: {store.get_task_count()}")
    
    # Create and add tasks
    task1 = Task(
        heading="Learn Python",
        details="Study Python programming language fundamentals",
        time_estimate=300,
        status=TaskStatus.IN_PROGRESS
    )
    
    task2 = Task(
        heading="Build API",
        details="Create REST API using FastAPI framework",
        time_estimate=180,
        status=TaskStatus.PENDING,
        deadline=datetime.utcnow() + timedelta(days=3)
    )
    
    task3 = Task(
        heading="Write tests",
        details="Create unit tests for all components",
        time_estimate=120,
        status=TaskStatus.DONE
    )
    
    # Add tasks to store
    task1_id = store.add_task(task1)
    task2_id = store.add_task(task2)
    task3_id = store.add_task(task3)
    
    print(f"Added tasks with IDs: {task1_id}, {task2_id}, {task3_id}")
    print(f"Total tasks after adding: {store.get_task_count()}")
    
    # Test retrieval
    retrieved_task = store.get_task(task1_id)
    print(f"Retrieved task: {retrieved_task}")
    
    # Test updating
    success = store.update_task(task1_id, status=TaskStatus.DONE, time_estimate=350)
    print(f"Update successful: {success}")
    
    updated_task = store.get_task(task1_id)
    print(f"Updated task status: {updated_task.status}")
    print(f"Updated time estimate: {updated_task.time_estimate}")
    
    # Test querying by status
    pending_tasks = store.list_tasks_by_status(TaskStatus.PENDING)
    done_tasks = store.list_tasks_by_status(TaskStatus.DONE)
    print(f"Pending tasks: {len(pending_tasks)}")
    print(f"Done tasks: {len(done_tasks)}")
    
    # Test search
    search_results = store.search_tasks("API")
    print(f"Search results for 'API': {len(search_results)}")
    for result in search_results:
        print(f"  - {result.heading}")
    
    # Test time estimate filtering
    short_tasks = store.get_tasks_by_time_estimate(max_minutes=150)
    long_tasks = store.get_tasks_by_time_estimate(min_minutes=200)
    print(f"Short tasks (≤150 min): {len(short_tasks)}")
    print(f"Long tasks (≥200 min): {len(long_tasks)}")
    
    # Test deadline filtering
    future_tasks = store.list_tasks_by_deadline(after_date=datetime.utcnow())
    print(f"Tasks with future deadlines: {len(future_tasks)}")
    
    print()
    return store


def test_persistence():
    """Test data persistence across store instances"""
    print("=== Testing Data Persistence ===")
    
    test_storage_dir = "test_data"
    
    # Create first store instance and add a task
    store1 = JsonStore(storage_dir=test_storage_dir)
    store1.clear_all_tasks()  # Start fresh
    
    task = Task(
        heading="Persistent task",
        details="This task should persist across store instances",
        time_estimate=90
    )
    
    task_id = store1.add_task(task)
    print(f"Added task with ID: {task_id}")
    print(f"Tasks in store1: {store1.get_task_count()}")
    
    # Create second store instance and verify task exists
    store2 = JsonStore(storage_dir=test_storage_dir)
    print(f"Tasks in store2: {store2.get_task_count()}")
    
    retrieved_task = store2.get_task(task_id)
    print(f"Retrieved task in store2: {retrieved_task}")
    print(f"Task heading: {retrieved_task.heading}")
    print(f"Task details: {retrieved_task.details}")
    
    # Update task in store2
    store2.update_task(task_id, status=TaskStatus.DONE)
    
    # Verify update in store1
    updated_task = store1.get_task(task_id)
    print(f"Task status in store1 after update in store2: {updated_task.status}")
    
    print()


def test_error_handling():
    """Test error handling scenarios"""
    print("=== Testing Error Handling ===")
    
    store = JsonStore(storage_dir="test_data")
    
    # Test getting non-existent task
    non_existent_task = store.get_task("non-existent-id")
    print(f"Non-existent task: {non_existent_task}")
    
    # Test updating non-existent task
    update_success = store.update_task("non-existent-id", status=TaskStatus.DONE)
    print(f"Update non-existent task: {update_success}")
    
    # Test deleting non-existent task
    delete_success = store.delete_task("non-existent-id")
    print(f"Delete non-existent task: {delete_success}")
    
    print()


def cleanup():
    """Clean up test data"""
    print("=== Cleaning Up ===")
    
    import shutil
    
    test_data_dir = Path("test_data")
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)
        print("Removed test data directory")
    
    print()


def main():
    """Run all tests"""
    print("Starting Task Model and JsonStore Tests")
    print("=" * 50)
    
    try:
        # Run all test functions
        test_task_creation()
        test_task_with_deadline()
        test_subtasks()
        test_task_serialization()
        test_json_store()
        test_persistence()
        test_error_handling()
        
        print("All tests completed successfully! ✅")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        cleanup()
    
    return 0


if __name__ == "__main__":
    exit(main()) 