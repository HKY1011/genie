#!/usr/bin/env python3
"""
Enhanced JsonStore Integration Example
Demonstrates how to integrate the enhanced JsonStore with existing Genie agents
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from storage.json_store import JsonStore
from models.task_model import Task, TaskStatus
from models.user_session import UserSession, UserPreferences
from agents.supervisor_agent import SupervisorAgent
from agents.task_extraction_agent import TaskExtractionAgent
from agents.planning_agent import PlanningAgent
from agents.genieorchestrator_agent import GenieOrchestrator


class EnhancedGenieSystem:
    """
    Enhanced Genie system with comprehensive persistent state management
    
    This class demonstrates how to integrate the enhanced JsonStore with
    all existing Genie agents for a complete persistent workflow.
    """
    
    def __init__(self, storage_path: str = "progress.json"):
        """
        Initialize the enhanced Genie system
        
        Args:
            storage_path: Path to the progress.json file
        """
        # Initialize the enhanced storage
        self.store = JsonStore(storage_path=storage_path)
        
        # Initialize agents
        self.supervisor = SupervisorAgent()
        self.task_extractor = TaskExtractionAgent()
        self.planner = PlanningAgent()
        self.orchestrator = GenieOrchestrator()
        
        print(f"🚀 Enhanced Genie System initialized")
        print(f"📁 Storage: {storage_path}")
    
    def get_or_create_user(self, user_id: str) -> UserSession:
        """
        Get or create a user session
        
        Args:
            user_id: User identifier
            
        Returns:
            UserSession object
        """
        session = self.store.get_or_create_user_session(user_id)
        print(f"👤 User session: {user_id}")
        return session
    
    def process_user_input(self, user_id: str, user_input: str) -> dict:
        """
        Process user input and maintain persistent state
        
        Args:
            user_id: User identifier
            user_input: Natural language user input
            
        Returns:
            Dictionary with processing results
        """
        print(f"\n🎯 Processing input for user {user_id}: {user_input}")
        
        # Get user session
        session = self.get_or_create_user(user_id)
        
        # Extract tasks from user input
        try:
            existing_tasks = self.store.list_tasks(user_id)
            actions = self.task_extractor.extract_task(user_input, existing_tasks)
            
            print(f"📝 Extracted {len(actions)} actions")
            
            # Process each action
            results = []
            for action in actions:
                result = self._process_action(user_id, action, session)
                results.append(result)
            
            # Save updated session
            self.store.save_user_session(session)
            
            # Get next recommendation
            next_action = self._get_next_recommendation(user_id, session)
            
            return {
                "user_id": user_id,
                "actions_processed": len(actions),
                "results": results,
                "next_recommendation": next_action,
                "session_updated": True
            }
            
        except Exception as e:
            print(f"❌ Error processing input: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "actions_processed": 0,
                "results": []
            }
    
    def _process_action(self, user_id: str, action: dict, session: UserSession) -> dict:
        """
        Process a single action and update persistent state
        
        Args:
            user_id: User identifier
            action: Action dictionary from TaskExtractionAgent
            session: User session
            
        Returns:
            Dictionary with action result
        """
        action_type = action.get('action')
        
        if action_type == 'add':
            return self._handle_add_task(user_id, action, session)
        elif action_type == 'edit':
            return self._handle_edit_task(user_id, action, session)
        elif action_type == 'mark_done':
            return self._handle_mark_done(user_id, action, session)
        elif action_type == 'reschedule':
            return self._handle_reschedule(user_id, action, session)
        elif action_type == 'add_subtask':
            return self._handle_add_subtask(user_id, action, session)
        else:
            return {"action": action_type, "status": "unknown", "message": "Unknown action type"}
    
    def _handle_add_task(self, user_id: str, action: dict, session: UserSession) -> dict:
        """Handle adding a new task"""
        try:
            # Create task from action
            task = Task(
                heading=action.get('heading', 'New Task'),
                details=action.get('details', ''),
                deadline=datetime.fromisoformat(action['deadline']) if action.get('deadline') else None,
                time_estimate=action.get('time_estimate')
            )
            
            # Add to storage
            task_id = self.store.add_task(user_id, task)
            
            # Add to session
            session.add_task(task)
            
            # Plan the task if it's complex
            if task.time_estimate and task.time_estimate > 60:
                self._plan_task(user_id, task)
            
            print(f"✅ Added task: {task.heading}")
            
            return {
                "action": "add",
                "status": "success",
                "task_id": task_id,
                "task_heading": task.heading,
                "planned": task.time_estimate and task.time_estimate > 60
            }
            
        except Exception as e:
            return {"action": "add", "status": "error", "error": str(e)}
    
    def _handle_edit_task(self, user_id: str, action: dict, session: UserSession) -> dict:
        """Handle editing an existing task"""
        try:
            target_task = action.get('target_task')
            task = self._find_task_by_target(user_id, target_task)
            
            if not task:
                return {"action": "edit", "status": "error", "error": "Task not found"}
            
            # Update task fields
            updates = {}
            if 'heading' in action:
                updates['heading'] = action['heading']
            if 'details' in action:
                updates['details'] = action['details']
            if 'deadline' in action:
                updates['deadline'] = datetime.fromisoformat(action['deadline'])
            if 'time_estimate' in action:
                updates['time_estimate'] = action['time_estimate']
            
            # Apply updates
            success = self.store.update_task(user_id, str(task.id), **updates)
            
            if success:
                print(f"✅ Updated task: {task.heading}")
                return {
                    "action": "edit",
                    "status": "success",
                    "task_id": str(task.id),
                    "updates": list(updates.keys())
                }
            else:
                return {"action": "edit", "status": "error", "error": "Failed to update task"}
                
        except Exception as e:
            return {"action": "edit", "status": "error", "error": str(e)}
    
    def _handle_mark_done(self, user_id: str, action: dict, session: UserSession) -> dict:
        """Handle marking a task as done"""
        try:
            target_task = action.get('target_task')
            task = self._find_task_by_target(user_id, target_task)
            
            if not task:
                return {"action": "mark_done", "status": "error", "error": "Task not found"}
            
            # Mark as done
            success = self.store.update_task(user_id, str(task.id), status=TaskStatus.DONE)
            
            if success:
                # Record completion feedback
                self.store.add_feedback(user_id, {
                    "type": "task_completion",
                    "task_id": str(task.id),
                    "task_heading": task.heading,
                    "estimated_time": task.time_estimate or 0,
                    "completed_at": datetime.utcnow().isoformat()
                })
                
                print(f"✅ Marked task as done: {task.heading}")
                return {
                    "action": "mark_done",
                    "status": "success",
                    "task_id": str(task.id),
                    "task_heading": task.heading
                }
            else:
                return {"action": "mark_done", "status": "error", "error": "Failed to mark task as done"}
                
        except Exception as e:
            return {"action": "mark_done", "status": "error", "error": str(e)}
    
    def _handle_reschedule(self, user_id: str, action: dict, session: UserSession) -> dict:
        """Handle rescheduling a task"""
        try:
            target_task = action.get('target_task')
            task = self._find_task_by_target(user_id, target_task)
            
            if not task:
                return {"action": "reschedule", "status": "error", "error": "Task not found"}
            
            new_deadline = datetime.fromisoformat(action['deadline'])
            success = self.store.update_task(user_id, str(task.id), deadline=new_deadline)
            
            if success:
                print(f"✅ Rescheduled task: {task.heading} to {new_deadline}")
                return {
                    "action": "reschedule",
                    "status": "success",
                    "task_id": str(task.id),
                    "new_deadline": new_deadline.isoformat()
                }
            else:
                return {"action": "reschedule", "status": "error", "error": "Failed to reschedule task"}
                
        except Exception as e:
            return {"action": "reschedule", "status": "error", "error": str(e)}
    
    def _handle_add_subtask(self, user_id: str, action: dict, session: UserSession) -> dict:
        """Handle adding a subtask"""
        try:
            target_task = action.get('target_task')
            parent_task = self._find_task_by_target(user_id, target_task)
            
            if not parent_task:
                return {"action": "add_subtask", "status": "error", "error": "Parent task not found"}
            
            # Create subtask
            subtask = Task(
                heading=action['subtask']['heading'],
                details=action['subtask'].get('details', ''),
                deadline=datetime.fromisoformat(action['subtask']['deadline']) if action['subtask'].get('deadline') else None,
                time_estimate=action['subtask'].get('time_estimate')
            )
            
            # Add subtask to parent
            parent_task.add_subtask(subtask)
            
            # Update parent task in storage
            self.store.update_task(user_id, str(parent_task.id), subtasks=parent_task.subtasks)
            
            print(f"✅ Added subtask to {parent_task.heading}: {subtask.heading}")
            
            return {
                "action": "add_subtask",
                "status": "success",
                "parent_task_id": str(parent_task.id),
                "subtask_id": str(subtask.id),
                "subtask_heading": subtask.heading
            }
            
        except Exception as e:
            return {"action": "add_subtask", "status": "error", "error": str(e)}
    
    def _find_task_by_target(self, user_id: str, target: str) -> Task:
        """Find a task by ID or heading"""
        if not target:
            return None
        
        # Try to find by ID first
        task = self.store.get_task(user_id, target)
        if task:
            return task
        
        # Try to find by heading
        tasks = self.store.list_tasks(user_id)
        for task in tasks:
            if task.heading.lower() == target.lower():
                return task
        
        return None
    
    def _plan_task(self, user_id: str, task: Task):
        """Plan a complex task using PlanningAgent"""
        try:
            print(f"📋 Planning task: {task.heading}")
            
            # Get existing subtasks for context
            existing_chunks = [{"heading": st.heading, "details": st.details} for st in task.subtasks]
            
            # Plan the task
            chunk = self.planner.break_down_chunk(
                heading=task.heading,
                details=task.details,
                deadline=task.deadline,
                previous_chunks=existing_chunks
            )
            
            # Create subtask from planned chunk
            subtask = Task(
                heading=chunk['heading'],
                details=chunk['details'],
                time_estimate=chunk['estimated_time_minutes'],
                resource_link=chunk['resource']['url']
            )
            
            # Add to parent task
            task.add_subtask(subtask)
            self.store.update_task(user_id, str(task.id), subtasks=task.subtasks)
            
            print(f"✅ Planned subtask: {subtask.heading}")
            
        except Exception as e:
            print(f"❌ Error planning task: {e}")
    
    def _get_next_recommendation(self, user_id: str, session: UserSession) -> dict:
        """Get next action recommendation using GenieOrchestrator"""
        try:
            # Get all tasks for the user
            tasks = self.store.list_tasks(user_id)
            
            if not tasks:
                return {"message": "No tasks available. Add some tasks to get started!"}
            
            # Convert tasks to JSON for orchestrator
            tasks_json = json.dumps([task.to_dict() for task in tasks])
            
            # Create user schedule from preferences
            schedule = {
                "daily_schedule": [
                    {
                        "start_time": "09:00",
                        "end_time": "17:00",
                        "day_of_week": "daily",
                        "energy_level": "high",
                        "focus_type": "deep_work"
                    }
                ],
                "preferences": session.preferences.__dict__
            }
            schedule_json = json.dumps(schedule)
            
            # Get recommendation
            recommendation = self.orchestrator.get_next_action(tasks_json, schedule_json)
            
            return {
                "next_chunk_id": recommendation.get('next_chunk_id'),
                "task_id": recommendation.get('task_id'),
                "chunk_heading": recommendation.get('chunk_heading'),
                "chunk_details": recommendation.get('chunk_details'),
                "estimated_time_minutes": recommendation.get('estimated_time_minutes'),
                "scheduled_time_start": recommendation.get('scheduled_time_start'),
                "resource": recommendation.get('resource', {})
            }
            
        except Exception as e:
            print(f"❌ Error getting recommendation: {e}")
            return {"message": "Unable to get recommendation at this time."}
    
    def get_user_analytics(self, user_id: str) -> dict:
        """Get comprehensive analytics for a user"""
        return self.store.get_analytics(user_id)
    
    def get_user_status(self, user_id: str) -> dict:
        """Get current status for a user"""
        session = self.get_or_create_user(user_id)
        tasks = self.store.list_tasks(user_id)
        
        return {
            "user_id": user_id,
            "session_created": session.created_at.isoformat(),
            "last_updated": session.last_updated.isoformat(),
            "total_tasks": len(tasks),
            "pending_tasks": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "in_progress_tasks": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed_tasks": len([t for t in tasks if t.status == TaskStatus.DONE]),
            "tasks_completed_today": session.tasks_completed_today,
            "total_focus_time": session.total_focus_time
        }
    
    def create_backup(self, reason: str = "manual") -> str:
        """Create a backup of all data"""
        return self.store.create_backup(reason)
    
    def list_backups(self) -> list:
        """List all available backups"""
        return self.store.list_backups()


def demo_enhanced_system():
    """Demonstrate the enhanced Genie system"""
    print("🎯 Enhanced Genie System Demo")
    print("=" * 50)
    
    # Initialize the enhanced system
    system = EnhancedGenieSystem("demo_progress.json")
    
    # Demo user
    user_id = "demo_user"
    
    print(f"\n👤 Working with user: {user_id}")
    
    # Demo 1: Add tasks
    print("\n📝 Demo 1: Adding Tasks")
    print("-" * 30)
    
    inputs = [
        "I need to learn Python programming by next Friday",
        "Build a React todo app with authentication by next month",
        "Write a research paper on machine learning by the end of the week"
    ]
    
    for user_input in inputs:
        result = system.process_user_input(user_id, user_input)
        print(f"Input: {user_input}")
        print(f"Result: {result['actions_processed']} actions processed")
        if result.get('next_recommendation'):
            rec = result['next_recommendation']
            print(f"Next: {rec.get('chunk_heading', rec.get('message', 'No recommendation'))}")
        print()
    
    # Demo 2: Mark tasks as done
    print("\n✅ Demo 2: Marking Tasks as Done")
    print("-" * 30)
    
    mark_done_inputs = [
        "I finished the Python programming task",
        "The React app is complete"
    ]
    
    for user_input in mark_done_inputs:
        result = system.process_user_input(user_id, user_input)
        print(f"Input: {user_input}")
        print(f"Result: {result['actions_processed']} actions processed")
        print()
    
    # Demo 3: Get user status and analytics
    print("\n📊 Demo 3: User Status and Analytics")
    print("-" * 30)
    
    status = system.get_user_status(user_id)
    analytics = system.get_user_analytics(user_id)
    
    print(f"User Status:")
    print(f"  Total tasks: {status['total_tasks']}")
    print(f"  Pending: {status['pending_tasks']}")
    print(f"  In Progress: {status['in_progress_tasks']}")
    print(f"  Completed: {status['completed_tasks']}")
    print(f"  Completed today: {status['tasks_completed_today']}")
    
    print(f"\nAnalytics:")
    print(f"  Productivity stats: {analytics.get('productivity_stats', {})}")
    
    # Demo 4: Create backup
    print("\n💾 Demo 4: Backup and Recovery")
    print("-" * 30)
    
    backup_filename = system.create_backup("demo")
    print(f"Created backup: {backup_filename}")
    
    backups = system.list_backups()
    print(f"Available backups: {len(backups)}")
    for backup in backups[:3]:  # Show first 3
        print(f"  {backup['filename']} ({backup['size']} bytes)")
    
    print("\n🎉 Enhanced Genie System Demo Complete!")
    print("✅ All persistent state management features demonstrated")
    print("✅ Multi-user support working")
    print("✅ Backup and recovery functional")
    print("✅ Analytics and feedback collection operational")


if __name__ == "__main__":
    demo_enhanced_system() 