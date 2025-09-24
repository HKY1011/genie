#!/usr/bin/env python3
"""
Google Calendar Integration Example for Genie
Demonstrates how to integrate Google Calendar API with Genie orchestrator
for automatic mini-task scheduling and availability management.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from integrations.google_calendar_api import GoogleCalendarAPI, GoogleCalendarAPIError
from agents.genieorchestrator_agent import GenieOrchestrator
from agents.planning_agent import PlanningAgent
from models.task_model import Task, TaskStatus
from storage.json_store import JsonStore


class CalendarIntegratedGenie:
    """
    Enhanced Genie system with Google Calendar integration
    
    This class demonstrates how to integrate Google Calendar API with
    Genie's task orchestration for automatic scheduling and availability management.
    """
    
    def __init__(self, storage_path: str = "progress.json"):
        """
        Initialize Calendar-integrated Genie system
        
        Args:
            storage_path: Path to the progress.json file
        """
        # Initialize storage
        self.store = JsonStore(storage_path=storage_path)
        
        # Initialize agents
        self.orchestrator = GenieOrchestrator()
        self.planner = PlanningAgent()
        
        # Initialize calendar API (will fail gracefully if no credentials)
        self.calendar_api = None
        try:
            self.calendar_api = GoogleCalendarAPI()
            print("✅ Google Calendar API initialized")
        except GoogleCalendarAPIError as e:
            print(f"⚠️  Google Calendar API not available: {e}")
            print("   Calendar integration will be disabled")
        
        print(f"🚀 Calendar-integrated Genie system initialized")
    
    def get_availability(self, start_time: datetime, end_time: datetime) -> dict:
        """
        Get calendar availability for scheduling
        
        Args:
            start_time: Start time for availability check
            end_time: End time for availability check
            
        Returns:
            Dictionary with availability information
        """
        if not self.calendar_api:
            # Fallback: return default availability
            return {
                "available": True,
                "free_blocks": [
                    {
                        "start": start_time,
                        "end": end_time,
                        "duration_minutes": int((end_time - start_time).total_seconds() / 60)
                    }
                ],
                "busy_blocks": [],
                "calendar_connected": False
            }
        
        try:
            free_busy = self.calendar_api.get_free_busy(start_time, end_time)
            return {
                "available": len(free_busy['free']) > 0,
                "free_blocks": free_busy['free'],
                "busy_blocks": free_busy['busy'],
                "calendar_connected": True
            }
        except Exception as e:
            print(f"⚠️  Error getting availability: {e}")
            return {
                "available": True,
                "free_blocks": [],
                "busy_blocks": [],
                "calendar_connected": False
            }
    
    def find_optimal_slot(self, 
                         task_duration_minutes: int,
                         start_time: datetime,
                         end_time: datetime,
                         user_preferences: dict = None) -> dict:
        """
        Find optimal time slot for a task based on calendar availability
        
        Args:
            task_duration_minutes: Duration of the task in minutes
            start_time: Earliest possible start time
            end_time: Latest possible end time
            user_preferences: User preferences for scheduling
            
        Returns:
            Dictionary with optimal slot information
        """
        availability = self.get_availability(start_time, end_time)
        
        if not availability['calendar_connected']:
            # Fallback: schedule immediately
            return {
                "start_time": start_time,
                "end_time": start_time + timedelta(minutes=task_duration_minutes),
                "calendar_scheduled": False,
                "reason": "Calendar not connected"
            }
        
        # Find the best free block
        best_slot = None
        best_score = 0
        
        for free_block in availability['free_blocks']:
            block_duration = free_block['duration_minutes']
            
            # Check if block is long enough
            if block_duration < task_duration_minutes:
                continue
            
            # Calculate score based on preferences
            score = self._calculate_slot_score(free_block, user_preferences)
            
            if score > best_score:
                best_score = score
                best_slot = free_block
        
        if best_slot:
            # Schedule at the beginning of the best slot
            slot_start = best_slot['start']
            slot_end = slot_start + timedelta(minutes=task_duration_minutes)
            
            return {
                "start_time": slot_start,
                "end_time": slot_end,
                "calendar_scheduled": True,
                "free_block_duration": best_slot['duration_minutes'],
                "score": best_score
            }
        else:
            # No suitable slot found
            return {
                "start_time": start_time,
                "end_time": start_time + timedelta(minutes=task_duration_minutes),
                "calendar_scheduled": False,
                "reason": "No suitable time slot found"
            }
    
    def _calculate_slot_score(self, free_block: dict, user_preferences: dict = None) -> float:
        """
        Calculate score for a time slot based on user preferences
        
        Args:
            free_block: Free time block information
            user_preferences: User scheduling preferences
            
        Returns:
            Score (higher is better)
        """
        if not user_preferences:
            return 1.0
        
        score = 1.0
        
        # Prefer longer blocks (more flexibility)
        score += free_block['duration_minutes'] / 60.0
        
        # Prefer morning hours (if specified)
        if user_preferences.get('prefer_morning', False):
            hour = free_block['start'].hour
            if 9 <= hour <= 11:
                score += 2.0
            elif 8 <= hour <= 12:
                score += 1.0
        
        # Prefer work hours
        hour = free_block['start'].hour
        if 9 <= hour <= 17:
            score += 1.5
        
        # Avoid late hours
        if hour >= 22 or hour <= 6:
            score -= 1.0
        
        return score
    
    def schedule_task_in_calendar(self, 
                                 task: Task,
                                 start_time: datetime,
                                 end_time: datetime,
                                 user_id: str = "default_user") -> str:
        """
        Schedule a task in Google Calendar
        
        Args:
            task: Task to schedule
            start_time: Start time for the task
            end_time: End time for the task
            user_id: User identifier
            
        Returns:
            Google Calendar event ID or None if failed
        """
        if not self.calendar_api:
            print("⚠️  Calendar API not available - skipping calendar scheduling")
            return None
        
        try:
            # Create calendar event
            event_id = self.calendar_api.create_event(
                summary=f"[Genie] {task.heading}",
                description=f"{task.details}\n\nTask ID: {task.id}\nUser: {user_id}",
                start_datetime=start_time,
                end_datetime=end_time,
                resource_link=task.resource_link
            )
            
            print(f"✅ Scheduled task in calendar: {event_id}")
            
            # Store event ID in task metadata
            task.metadata = task.metadata or {}
            task.metadata['google_calendar_event_id'] = event_id
            task.metadata['calendar_scheduled_at'] = start_time.isoformat()
            
            # Update task in storage
            self.store.update_task(user_id, str(task.id), metadata=task.metadata)
            
            return event_id
            
        except Exception as e:
            print(f"❌ Failed to schedule task in calendar: {e}")
            return None
    
    def update_calendar_event(self, 
                            task: Task,
                            new_start_time: datetime = None,
                            new_end_time: datetime = None,
                            user_id: str = "default_user") -> bool:
        """
        Update a task's calendar event
        
        Args:
            task: Task to update
            new_start_time: New start time (optional)
            new_end_time: New end time (optional)
            user_id: User identifier
            
        Returns:
            True if update successful
        """
        if not self.calendar_api:
            return False
        
        event_id = task.metadata.get('google_calendar_event_id') if task.metadata else None
        if not event_id:
            print("⚠️  No calendar event ID found for task")
            return False
        
        try:
            success = self.calendar_api.update_event(
                event_id=event_id,
                start_datetime=new_start_time,
                end_datetime=new_end_time
            )
            
            if success:
                print(f"✅ Updated calendar event: {event_id}")
                
                # Update task metadata
                if new_start_time:
                    task.metadata['calendar_scheduled_at'] = new_start_time.isoformat()
                    self.store.update_task(user_id, str(task.id), metadata=task.metadata)
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to update calendar event: {e}")
            return False
    
    def remove_calendar_event(self, task: Task, user_id: str = "default_user") -> bool:
        """
        Remove a task's calendar event
        
        Args:
            task: Task to remove from calendar
            user_id: User identifier
            
        Returns:
            True if removal successful
        """
        if not self.calendar_api:
            return False
        
        event_id = task.metadata.get('google_calendar_event_id') if task.metadata else None
        if not event_id:
            return True  # No event to remove
        
        try:
            success = self.calendar_api.delete_event(event_id)
            
            if success:
                print(f"✅ Removed calendar event: {event_id}")
                
                # Clean up task metadata
                if task.metadata:
                    task.metadata.pop('google_calendar_event_id', None)
                    task.metadata.pop('calendar_scheduled_at', None)
                    self.store.update_task(user_id, str(task.id), metadata=task.metadata)
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to remove calendar event: {e}")
            return False
    
    def process_task_with_calendar(self, 
                                 user_input: str,
                                 user_id: str = "default_user",
                                 user_preferences: dict = None) -> dict:
        """
        Process a task with calendar integration
        
        Args:
            user_input: Natural language task description
            user_id: User identifier
            user_preferences: User scheduling preferences
            
        Returns:
            Dictionary with processing results
        """
        print(f"\n🎯 Processing task with calendar integration: {user_input}")
        
        # Create task
        task = Task(
            heading=user_input,
            details=f"Task created from input: {user_input}",
            time_estimate=30  # Default 30 minutes
        )
        
        # Add task to storage
        task_id = self.store.add_task(user_id, task)
        print(f"✅ Created task: {task_id}")
        
        # Find optimal time slot
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)
        
        optimal_slot = self.find_optimal_slot(
            task_duration_minutes=task.time_estimate or 30,
            start_time=start_time,
            end_time=end_time,
            user_preferences=user_preferences
        )
        
        print(f"📅 Optimal slot found:")
        print(f"   Start: {optimal_slot['start_time']}")
        print(f"   End: {optimal_slot['end_time']}")
        print(f"   Calendar scheduled: {optimal_slot['calendar_scheduled']}")
        
        # Schedule in calendar if available
        event_id = None
        if optimal_slot['calendar_scheduled'] and self.calendar_api:
            event_id = self.schedule_task_in_calendar(
                task=task,
                start_time=optimal_slot['start_time'],
                end_time=optimal_slot['end_time'],
                user_id=user_id
            )
        
        # Update task with scheduling information
        task.metadata = task.metadata or {}
        task.metadata['scheduled_start'] = optimal_slot['start_time'].isoformat()
        task.metadata['scheduled_end'] = optimal_slot['end_time'].isoformat()
        task.metadata['calendar_integrated'] = self.calendar_api is not None
        
        self.store.update_task(user_id, str(task.id), metadata=task.metadata)
        
        return {
            "task_id": task_id,
            "task_heading": task.heading,
            "scheduled_start": optimal_slot['start_time'],
            "scheduled_end": optimal_slot['end_time'],
            "calendar_event_id": event_id,
            "calendar_integrated": self.calendar_api is not None,
            "slot_quality": optimal_slot.get('score', 0)
        }
    
    def get_user_schedule(self, user_id: str, days: int = 7) -> dict:
        """
        Get user's schedule including Genie tasks and calendar events
        
        Args:
            user_id: User identifier
            days: Number of days to look ahead
            
        Returns:
            Dictionary with schedule information
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(days=days)
        
        # Get Genie tasks
        tasks = self.store.list_tasks(user_id)
        scheduled_tasks = []
        
        for task in tasks:
            if task.metadata and task.metadata.get('scheduled_start'):
                scheduled_tasks.append({
                    "type": "genie_task",
                    "id": str(task.id),
                    "heading": task.heading,
                    "start": task.metadata['scheduled_start'],
                    "end": task.metadata.get('scheduled_end', ''),
                    "status": task.status.value,
                    "calendar_event_id": task.metadata.get('google_calendar_event_id')
                })
        
        # Get calendar events if available
        calendar_events = []
        if self.calendar_api:
            try:
                events = self.calendar_api.list_events(start_time, end_time)
                for event in events:
                    calendar_events.append({
                        "type": "calendar_event",
                        "id": event['id'],
                        "heading": event['summary'],
                        "start": event['start'].get('dateTime', event['start'].get('date')),
                        "end": event['end'].get('dateTime', event['end'].get('date')),
                        "is_genie_event": '🤖 Created by Genie AI Assistant' in event.get('description', '')
                    })
            except Exception as e:
                print(f"⚠️  Error getting calendar events: {e}")
        
        return {
            "user_id": user_id,
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "genie_tasks": scheduled_tasks,
            "calendar_events": calendar_events,
            "calendar_connected": self.calendar_api is not None
        }


def demo_calendar_integration():
    """Demonstrate calendar integration with Genie"""
    print("🎯 Calendar Integration Demo")
    print("=" * 50)
    
    # Initialize the system
    system = CalendarIntegratedGenie("calendar_demo_progress.json")
    
    # Demo user
    user_id = "calendar_demo_user"
    
    print(f"\n👤 Working with user: {user_id}")
    
    # Demo 1: Process tasks with calendar integration
    print("\n📝 Demo 1: Processing Tasks with Calendar Integration")
    print("-" * 50)
    
    tasks = [
        "Learn React hooks and state management",
        "Build authentication system for the app",
        "Write unit tests for the backend API"
    ]
    
    user_preferences = {
        "prefer_morning": True,
        "avoid_late_hours": True
    }
    
    results = []
    for task_input in tasks:
        result = system.process_task_with_calendar(
            user_input=task_input,
            user_id=user_id,
            user_preferences=user_preferences
        )
        results.append(result)
        
        print(f"Task: {result['task_heading']}")
        print(f"  Scheduled: {result['scheduled_start'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  Calendar: {'✅' if result['calendar_integrated'] else '❌'}")
        print(f"  Event ID: {result['calendar_event_id'] or 'N/A'}")
        print()
    
    # Demo 2: Get user schedule
    print("\n📅 Demo 2: User Schedule Overview")
    print("-" * 50)
    
    schedule = system.get_user_schedule(user_id, days=7)
    
    print(f"Schedule for {schedule['user_id']}:")
    print(f"Period: {schedule['period']['start'][:10]} to {schedule['period']['end'][:10]}")
    print(f"Calendar connected: {schedule['calendar_connected']}")
    
    print(f"\nGenie Tasks ({len(schedule['genie_tasks'])}):")
    for task in schedule['genie_tasks']:
        print(f"  📋 {task['heading']} - {task['start'][:16]}")
    
    print(f"\nCalendar Events ({len(schedule['calendar_events'])}):")
    for event in schedule['calendar_events']:
        icon = "🤖" if event['is_genie_event'] else "📅"
        print(f"  {icon} {event['heading']} - {event['start'][:16]}")
    
    # Demo 3: Availability checking
    print("\n⏰ Demo 3: Availability Checking")
    print("-" * 50)
    
    start_time = datetime.now()
    end_time = start_time + timedelta(days=3)
    
    availability = system.get_availability(start_time, end_time)
    
    print(f"Availability for next 3 days:")
    print(f"Calendar connected: {availability['calendar_connected']}")
    print(f"Free blocks: {len(availability['free_blocks'])}")
    print(f"Busy blocks: {len(availability['busy_blocks'])}")
    
    if availability['free_blocks']:
        print("\nAvailable time blocks:")
        for i, block in enumerate(availability['free_blocks'][:5]):
            print(f"  {i+1}. {block['start'].strftime('%Y-%m-%d %H:%M')} - "
                  f"{block['end'].strftime('%H:%M')} ({block['duration_minutes']} min)")
    
    print("\n🎉 Calendar Integration Demo Complete!")
    print("✅ Tasks processed with calendar integration")
    print("✅ Schedule overview generated")
    print("✅ Availability checking working")
    
    if system.calendar_api:
        print("✅ Google Calendar API fully integrated")
    else:
        print("⚠️  Google Calendar API not available (check credentials)")


if __name__ == "__main__":
    demo_calendar_integration() 