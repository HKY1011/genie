#!/usr/bin/env python3
"""
Complete Calendar Integration Flow Test
Tests the full workflow: Task → Planning Agent → Orchestrator → Google Calendar
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
from agents.task_extraction_agent import TaskExtractionAgent
from models.task_model import Task, TaskStatus
from storage.json_store import JsonStore


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)


class CompleteCalendarFlowTest:
    """
    Test class for the complete calendar integration flow
    """
    
    def __init__(self):
        """Initialize the test system"""
        # Initialize storage
        self.store = JsonStore(storage_path="complete_flow_test.json")
        
        # Initialize agents
        self.task_extractor = TaskExtractionAgent()
        self.planner = PlanningAgent()
        self.orchestrator = GenieOrchestrator()
        
        # Initialize calendar API
        try:
            self.calendar_api = GoogleCalendarAPI()
            print("✅ Google Calendar API initialized")
        except GoogleCalendarAPIError as e:
            print(f"⚠️  Google Calendar API not available: {e}")
            self.calendar_api = None
        
        print("🚀 Complete Calendar Flow Test System initialized")
    
    def get_user_availability(self, days: int = 7) -> dict:
        """
        Get user availability for the next N days
        
        Args:
            days: Number of days to check
            
        Returns:
            Dictionary with availability information
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(days=days)
        
        if self.calendar_api:
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
        
        # Fallback availability
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
    
    def extract_and_create_task(self, user_input: str, user_id: str = "test_user") -> Task:
        """
        Extract task from user input and create it
        
        Args:
            user_input: Natural language task description
            user_id: User identifier
            
        Returns:
            Created task
        """
        print(f"\n🎯 Extracting task from: '{user_input}'")
        
        # Extract task using TaskExtractionAgent
        existing_tasks = self.store.list_tasks(user_id)
        extracted_tasks = self.task_extractor.extract_task(user_input, existing_tasks)
        
        # Get the first extracted task (or create a simple one if none)
        if extracted_tasks and len(extracted_tasks) > 0:
            extracted_task = extracted_tasks[0]
        else:
            # Fallback: create a simple task
            extracted_task = {
                'action': 'create',
                'task': {
                    'heading': user_input,
                    'details': user_input,
                    'time_estimate': 30
                }
            }
        
        # Create task in storage
        task_data = extracted_task.get('task', {})
        task = Task(
            heading=task_data.get('heading', user_input),
            details=task_data.get('details', user_input),
            time_estimate=task_data.get('time_estimate', 30),
            resource_link=task_data.get('resource_link'),
            deadline=task_data.get('deadline')
        )
        
        task_id = self.store.add_task(user_id, task)
        print(f"✅ Created task: {task_id}")
        print(f"   Heading: {task.heading}")
        print(f"   Time estimate: {task.time_estimate} minutes")
        
        return task
    
    def break_down_task(self, task: Task, user_id: str = "test_user") -> list:
        """
        Break down task into subtasks using real Planning Agent
        
        Args:
            task: Task to break down
            user_id: User identifier
            
        Returns:
            List of subtasks
        """
        print(f"\n🔧 Breaking down task: {task.heading}")
        
        # Get user availability for context
        availability = self.get_user_availability()
        
        # Use real PlanningAgent to generate subtasks
        task_dict = {
            'heading': task.heading,
            'details': task.details,
            'time_estimate': task.time_estimate,
            'resource_link': task.resource_link,
            'deadline': task.deadline.isoformat() if task.deadline else None
        }
        
        # Convert available_time_blocks to JSON-serializable format
        if availability.get('free_blocks'):
            serializable_blocks = []
            for block in availability['free_blocks']:
                serializable_block = {
                    'start': block['start'].isoformat() if hasattr(block['start'], 'isoformat') else str(block['start']),
                    'end': block['end'].isoformat() if hasattr(block['end'], 'isoformat') else str(block['end']),
                    'duration_minutes': block.get('duration_minutes', 0)
                }
                serializable_blocks.append(serializable_block)
            task_dict['available_time_blocks'] = serializable_blocks
        else:
            task_dict['available_time_blocks'] = []
        
        # Generate subtasks using real PlanningAgent
        task_id = str(task.id)
        subtasks_data = self.planner.generate_initial_subtasks(task_dict, task_id)
        
        # Convert subtasks data to Task objects
        subtasks = []
        for i, subtask_data in enumerate(subtasks_data):
            subtask = Task(
                heading=subtask_data['chunk_heading'],
                details=subtask_data['chunk_details'],
                time_estimate=subtask_data['estimated_time_minutes'],
                resource_link=subtask_data['resource']['url']
            )
            
            # Add subtask to parent task
            task.add_subtask(subtask)
            subtasks.append(subtask)
            
            print(f"   Subtask {i+1}: {subtask.heading} ({subtask.time_estimate} min)")
        
        # Update task in storage
        self.store.update_task(user_id, str(task.id), subtasks=task.subtasks)
        
        print(f"✅ Created {len(subtasks)} subtasks using real PlanningAgent")
        return subtasks
    
    def schedule_subtasks(self, task: Task, user_id: str = "test_user") -> list:
        """
        Schedule subtasks using Genie Orchestrator with sequential timing
        
        Args:
            task: Task with subtasks
            user_id: User identifier
            
        Returns:
            List of scheduled subtasks with timing
        """
        print(f"\n📅 Scheduling subtasks for: {task.heading}")
        
        # Get user availability
        availability = self.get_user_availability()
        
        scheduled_subtasks = []
        current_time = datetime.now()
        
        # Sort subtasks by priority (you can implement custom priority logic)
        sorted_subtasks = sorted(task.subtasks, key=lambda x: x.time_estimate or 30, reverse=True)
        
        for i, subtask in enumerate(sorted_subtasks):
            print(f"\n   Scheduling subtask {i+1}: {subtask.heading}")
            
            # Prepare tasks JSON for orchestrator
            all_tasks = self.store.list_tasks(user_id)
            all_tasks_json = json.dumps([task.to_dict() for task in all_tasks], indent=2)
            
            # Prepare user schedule JSON with current time context
            user_schedule = {
                "daily_schedule": [
                    {
                        "start_time": "09:00",
                        "end_time": "17:00",
                        "day_of_week": "daily",
                        "energy_level": "medium",
                        "focus_type": "deep_work"
                    }
                ],
                "preferences": {
                    "prefer_morning": True,
                    "avoid_late_hours": True
                },
                "timezone": "Asia/Kolkata",
                "current_time": current_time.isoformat()
            }
            user_schedule_json = json.dumps(user_schedule, indent=2)
            
            # Get orchestration recommendation
            recommendation = self.orchestrator.get_next_action(
                all_tasks_json=all_tasks_json,
                user_schedule_json=user_schedule_json
            )
            
            if recommendation and recommendation.get('next_chunk_id'):
                # Extract information from orchestrator response
                chunk_id = recommendation.get('next_chunk_id')
                scheduled_start = recommendation.get('scheduled_time_start')
                scheduled_end = recommendation.get('scheduled_time_end')
                estimated_time = recommendation.get('estimated_time_minutes', subtask.time_estimate or 30)
                
                # Parse orchestrator's scheduled times
                orchestrator_start = None
                orchestrator_end = None
                
                if scheduled_start:
                    try:
                        orchestrator_start = datetime.fromisoformat(scheduled_start.replace('Z', '+00:00'))
                        if orchestrator_start.tzinfo is not None:
                            orchestrator_start = orchestrator_start.replace(tzinfo=None)
                    except:
                        orchestrator_start = current_time
                else:
                    orchestrator_start = current_time
                
                if scheduled_end:
                    try:
                        orchestrator_end = datetime.fromisoformat(scheduled_end.replace('Z', '+00:00'))
                        if orchestrator_end.tzinfo is not None:
                            orchestrator_end = orchestrator_end.replace(tzinfo=None)
                    except:
                        orchestrator_end = orchestrator_start + timedelta(minutes=estimated_time)
                else:
                    orchestrator_end = orchestrator_start + timedelta(minutes=estimated_time)
                
                # Check if orchestrator's schedule conflicts with existing scheduled tasks
                optimal_slot = self.check_orchestrator_schedule(
                    orchestrator_start,
                    orchestrator_end,
                    availability['free_blocks'],
                    scheduled_subtasks
                )
                
                # Schedule in calendar if available
                event_id = None
                if self.calendar_api and optimal_slot['calendar_scheduled']:
                    event_id = self.schedule_subtask_in_calendar(
                        subtask=subtask,
                        start_time=optimal_slot['start_time'],
                        end_time=optimal_slot['end_time'],
                        user_id=user_id
                    )
                
                # Update subtask metadata
                subtask.metadata = subtask.metadata or {}
                subtask.metadata.update({
                    'scheduled_start': optimal_slot['start_time'].isoformat(),
                    'scheduled_end': optimal_slot['end_time'].isoformat(),
                    'calendar_event_id': event_id,
                    'orchestrator_score': recommendation.get('priority_score', 0),
                    'scheduled_by': 'Genie Orchestrator',
                    'chunk_id': chunk_id
                })
                
                scheduled_subtasks.append({
                    'subtask': subtask,
                    'scheduled_start': optimal_slot['start_time'],
                    'scheduled_end': optimal_slot['end_time'],
                    'calendar_event_id': event_id,
                    'score': recommendation.get('priority_score', 0)
                })
                
                print(f"     ✅ Scheduled: {optimal_slot['start_time'].strftime('%Y-%m-%d %H:%M')} - {optimal_slot['end_time'].strftime('%H:%M')}")
                if 'original_orchestrator_time' in optimal_slot:
                    print(f"     🎯 Orchestrator wanted: {optimal_slot['original_orchestrator_time']}")
                print(f"     📅 Calendar: {'✅' if event_id else '❌'}")
                print(f"     🎯 Score: {recommendation.get('priority_score', 0):.2f}")
                print(f"     📋 Chunk ID: {chunk_id}")
                print(f"     💡 Reason: {optimal_slot.get('reason', 'Scheduled')}")
            else:
                print(f"     ❌ No recommendation for subtask {i+1}")
        
        # Update task in storage
        self.store.update_task(user_id, str(task.id), subtasks=task.subtasks)
        
        return scheduled_subtasks
    
    def check_orchestrator_schedule(self, 
                                  orchestrator_start: datetime,
                                  orchestrator_end: datetime,
                                  free_blocks: list,
                                  existing_scheduled: list) -> dict:
        """
        Check if orchestrator's schedule conflicts with existing tasks or calendar
        
        Args:
            orchestrator_start: Start time proposed by orchestrator
            orchestrator_end: End time proposed by orchestrator
            free_blocks: Available time blocks from calendar
            existing_scheduled: List of already scheduled subtasks
            
        Returns:
            Dictionary with final schedule information
        """
        # Check for conflicts with existing scheduled tasks
        conflicts = []
        for scheduled in existing_scheduled:
            existing_start = scheduled['scheduled_start']
            existing_end = scheduled['scheduled_end']
            
            # Check for overlap
            if (orchestrator_start < existing_end and orchestrator_end > existing_start):
                conflicts.append(f"Conflicts with: {scheduled['subtask'].heading}")
        
        # If there are conflicts, find the next available time
        if conflicts:
            print(f"     ⚠️  Schedule conflicts detected: {', '.join(conflicts)}")
            
            # Find the latest end time of existing tasks
            if existing_scheduled:
                latest_end = max([s['scheduled_end'] for s in existing_scheduled])
                new_start = latest_end + timedelta(minutes=15)  # 15 min buffer
            else:
                new_start = datetime.now() + timedelta(minutes=5)
            
            # Ensure we're not scheduling in the past
            if new_start < datetime.now():
                new_start = datetime.now() + timedelta(minutes=5)
            
            # Calculate new end time maintaining the same duration
            duration = (orchestrator_end - orchestrator_start).total_seconds() / 60
            new_end = new_start + timedelta(minutes=duration)
            
            return {
                "start_time": new_start,
                "end_time": new_end,
                "calendar_scheduled": True,
                "score": 0.8,
                "reason": f"Rescheduled due to conflicts: {', '.join(conflicts)}",
                "original_orchestrator_time": f"{orchestrator_start.strftime('%H:%M')}-{orchestrator_end.strftime('%H:%M')}"
            }
        
        # Check if orchestrator's time fits within available free blocks
        if free_blocks:
            fits_in_free_block = False
            for free_block in free_blocks:
                block_start = free_block['start']
                block_end = free_block['end']
                
                # Ensure timezone consistency
                if block_start.tzinfo is not None:
                    block_start = block_start.replace(tzinfo=None)
                if block_end.tzinfo is not None:
                    block_end = block_end.replace(tzinfo=None)
                
                # Check if orchestrator's schedule fits in this block
                if (orchestrator_start >= block_start and orchestrator_end <= block_end):
                    fits_in_free_block = True
                    break
            
            if fits_in_free_block:
                return {
                    "start_time": orchestrator_start,
                    "end_time": orchestrator_end,
                    "calendar_scheduled": True,
                    "score": 1.0,
                    "reason": "Orchestrator schedule fits in available free block"
                }
            else:
                print(f"     ⚠️  Orchestrator schedule doesn't fit in free blocks")
                # Still use orchestrator's time but mark as potential conflict
                return {
                    "start_time": orchestrator_start,
                    "end_time": orchestrator_end,
                    "calendar_scheduled": True,
                    "score": 0.7,
                    "reason": "Orchestrator schedule used (may conflict with calendar)"
                }
        
        # No conflicts and no free blocks to check against
        return {
            "start_time": orchestrator_start,
            "end_time": orchestrator_end,
            "calendar_scheduled": True,
            "score": 0.9,
            "reason": "Orchestrator schedule accepted (no conflicts)"
        }
    
    def _round_to_nearest_quarter(self, dt: datetime) -> datetime:
        """
        Round datetime to nearest 15-minute interval
        
        Args:
            dt: Datetime to round
            
        Returns:
            Rounded datetime
        """
        minutes = dt.minute
        rounded_minutes = (minutes // 15) * 15
        if rounded_minutes == 60:
            rounded_minutes = 0
            dt = dt + timedelta(hours=1)
        
        return dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    
    def schedule_subtask_in_calendar(self, 
                                   subtask: Task,
                                   start_time: datetime,
                                   end_time: datetime,
                                   user_id: str) -> str:
        """
        Schedule a subtask in Google Calendar
        
        Args:
            subtask: Subtask to schedule
            start_time: Start time
            end_time: End time
            user_id: User identifier
            
        Returns:
            Google Calendar event ID or None
        """
        if not self.calendar_api:
            return None
        
        try:
            # Create calendar event
            event_id = self.calendar_api.create_event(
                summary=f"[Genie] {subtask.heading}",
                description=f"{subtask.details}\n\nSubtask of: {subtask.heading}\nUser: {user_id}",
                start_datetime=start_time,
                end_datetime=end_time,
                resource_link=subtask.resource_link
            )
            
            print(f"     📅 Created calendar event: {event_id}")
            return event_id
            
        except Exception as e:
            print(f"     ❌ Failed to create calendar event: {e}")
            return None
    
    def show_schedule_summary(self, user_id: str = "test_user"):
        """
        Show summary of scheduled tasks and calendar events
        
        Args:
            user_id: User identifier
        """
        print_section("Schedule Summary")
        
        # Get all tasks
        tasks = self.store.list_tasks(user_id)
        
        print(f"📊 Total tasks: {len(tasks)}")
        
        for task in tasks:
            print(f"\n📋 Task: {task.heading}")
            print(f"   Status: {task.status.value}")
            print(f"   Subtasks: {len(task.subtasks)}")
            
            for i, subtask in enumerate(task.subtasks):
                if subtask.metadata and subtask.metadata.get('scheduled_start'):
                    scheduled_start = subtask.metadata['scheduled_start']
                    calendar_id = subtask.metadata.get('calendar_event_id')
                    score = subtask.metadata.get('orchestrator_score', 0)
                    
                    print(f"     {i+1}. {subtask.heading}")
                    print(f"        📅 {scheduled_start[:16]}")
                    print(f"        🎯 Score: {score:.2f}")
                    print(f"        📱 Calendar: {'✅' if calendar_id else '❌'}")
        
        # Show calendar events if available
        if self.calendar_api:
            try:
                start_time = datetime.now()
                end_time = start_time + timedelta(days=7)
                
                events = self.calendar_api.list_events(start_time, end_time)
                genie_events = [e for e in events if '[Genie]' in e.get('summary', '')]
                
                print(f"\n📅 Calendar Events (Next 7 days):")
                print(f"   Total events: {len(events)}")
                print(f"   Genie events: {len(genie_events)}")
                
                for event in genie_events:
                    start = event['start'].get('dateTime', event['start'].get('date', 'Unknown'))
                    print(f"   🤖 {event['summary']} - {start[:16]}")
                    
            except Exception as e:
                print(f"   ⚠️  Error getting calendar events: {e}")


def test_complete_flow():
    """Test the complete calendar integration flow"""
    print_header("Complete Calendar Integration Flow Test")
    print("Testing: Task Extraction → Planning Agent → Orchestrator → Google Calendar")
    
    # Initialize test system
    test_system = CompleteCalendarFlowTest()
    user_id = "complete_flow_test_user"
    
    # Test tasks
    test_tasks = [
        "Build a React authentication system with JWT tokens",
        "Create a REST API for user management with Node.js and Express",
        "Design and implement a database schema for an e-commerce platform"
    ]
    
    all_scheduled_subtasks = []
    
    for i, task_input in enumerate(test_tasks):
        print_header(f"Processing Task {i+1}")
        
        try:
            # Step 1: Extract and create task
            task = test_system.extract_and_create_task(task_input, user_id)
            
            # Step 2: Break down into subtasks
            subtasks = test_system.break_down_task(task, user_id)
            
            # Step 3: Schedule subtasks
            scheduled_subtasks = test_system.schedule_subtasks(task, user_id)
            all_scheduled_subtasks.extend(scheduled_subtasks)
            
            print(f"\n✅ Task {i+1} completed successfully!")
            print(f"   Created {len(subtasks)} subtasks")
            print(f"   Scheduled {len(scheduled_subtasks)} subtasks")
            
        except Exception as e:
            print(f"❌ Error processing task {i+1}: {e}")
            import traceback
            traceback.print_exc()
    
    # Show final summary
    print_header("Final Results")
    test_system.show_schedule_summary(user_id)
    
    print(f"\n📊 Summary:")
    print(f"   Total tasks processed: {len(test_tasks)}")
    print(f"   Total subtasks scheduled: {len(all_scheduled_subtasks)}")
    print(f"   Calendar integration: {'✅ Active' if test_system.calendar_api else '❌ Not available'}")
    
    if all_scheduled_subtasks:
        print(f"\n🎯 Scheduled Subtasks:")
        for i, scheduled in enumerate(all_scheduled_subtasks[:5]):  # Show first 5
            subtask = scheduled['subtask']
            start_time = scheduled['scheduled_start']
            calendar_id = scheduled['calendar_event_id']
            
            print(f"   {i+1}. {subtask.heading}")
            print(f"      📅 {start_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"      📱 Calendar: {'✅' if calendar_id else '❌'}")
            print(f"      🎯 Score: {scheduled['score']:.2f}")
    
    print(f"\n🎉 Complete Calendar Flow Test finished!")
    print("✅ Tasks extracted and created")
    print("✅ Subtasks generated by Planning Agent")
    print("✅ Subtasks scheduled by Orchestrator")
    print("✅ Calendar events created (if API available)")


if __name__ == "__main__":
    test_complete_flow() 