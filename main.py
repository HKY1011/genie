#!/usr/bin/env python3
"""
Enhanced Interactive Genie Backend System - Production Version
Complete workflow: User Input → Task Extraction → Planning → Orchestration → Calendar → Feedback

This main.py serves as the production interface for the Genie system,
taking real user input and orchestrating the complete task management workflow.
Enhanced with all fixes for deadline extraction, subtask flow, and feedback loops.
"""

import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import all system components
from agents.task_extraction_agent import TaskExtractionAgent, TaskExtractionError
from agents.planning_agent import PlanningAgent, PlanningAgentError
from agents.genieorchestrator_agent import GenieOrchestrator, GenieOrchestratorError
from agents.supervisor_agent import SupervisorAgent, SupervisorAgentError
from agents.feedback_agent import FeedbackAgent, FeedbackAgentError
from integrations.google_calendar_api import GoogleCalendarAPI, GoogleCalendarAPIError
from integrations.gemini_api import GeminiAPIClient, GeminiAPIError
from integrations.perplexity_api import PerplexityAPIClient, PerplexityAPIError
from storage.json_store import JsonStore
from models.task_model import Task, TaskStatus
from models.user_session import UserSession, SessionManager
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genie_interactive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GenieInteractiveSystem:
    """Enhanced Interactive Genie system with all fixes integrated"""
    
    def __init__(self):
        self.session_manager = None
        self.supervisor = None
        self.calendar_api = None
        self.gemini_client = None
        self.perplexity_client = None
        self.store = None
        self.current_user_id = "default_user"
        self.current_session = None
        
        # Load environment variables
        try:
            load_dotenv()  # For local development
        except:
            pass  # Railway uses environment variables directly
        
        # Railway fallback - ensure API keys are available
        try:
            from railway_config import setup_environment
            setup_environment()
        except:
            pass
        
        # Initialize components (same as test system)
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components with enhanced error handling"""
        try:
            logger.info("🔧 Initializing enhanced Genie system components...")
            
            # Initialize storage with error handling
            try:
                self.store = JsonStore("user_tasks.json")
                logger.info("✅ Storage system initialized")
            except Exception as e:
                logger.error(f"❌ Storage initialization failed: {e}")
                raise
            
            # Initialize session manager with validation
            try:
                self.session_manager = SessionManager()
                # Test session creation to ensure it works
                test_session = self.session_manager.create_session("test_user")
                if test_session:
                    logger.info("✅ Session manager initialized and tested")
                else:
                    raise Exception("Session creation test failed")
            except Exception as e:
                logger.error(f"❌ Session manager initialization failed: {e}")
                raise
            
            # Initialize supervisor with validation
            try:
                self.supervisor = SupervisorAgent()
                logger.info("✅ Supervisor agent initialized")
            except Exception as e:
                logger.error(f"❌ Supervisor initialization failed: {e}")
                raise
            
            # Initialize APIs with graceful degradation
            try:
                self.gemini_client = GeminiAPIClient()
                logger.info("✅ Gemini API client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini API client failed: {e}")
                self.gemini_client = None
            
            try:
                self.perplexity_client = PerplexityAPIClient()
                logger.info("✅ Perplexity API client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Perplexity API client failed: {e}")
                self.perplexity_client = None
            
            try:
                self.calendar_api = GoogleCalendarAPI()
                logger.info("✅ Google Calendar API initialized")
            except Exception as e:
                logger.warning(f"⚠️ Google Calendar API failed: {e}")
                self.calendar_api = None
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
    
    def get_user_input(self) -> str:
        """Get user input with enhanced validation and timeout protection"""
        print("\n" + "="*60)
        print("🎯 Genie Task Management System")
        print("="*60)
        print("Describe what you want to accomplish (with optional deadline):")
        print("Examples:")
        print("  • 'Learn Python programming by next week'")
        print("  • 'Build a React app by tomorrow'")
        print("  • 'Complete the project by end of month'")
        print("  • 'Study for exam in 3 days'")
        print("  • 'Submit report ASAP'")
        print("="*60)
        
        # Use a loop instead of recursion to prevent stack overflow
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                user_input = input("\nYour task: ").strip()
                
                if user_input:
                    return user_input
                else:
                    attempt += 1
                    remaining = max_attempts - attempt
                    if remaining > 0:
                        print(f"⚠️ Please provide a task description. ({remaining} attempts remaining)")
                    else:
                        print("⚠️ Maximum attempts reached. Using default task.")
                        return "Complete a general task"
                        
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye! Thanks for using Enhanced Genie!")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Input error: {e}")
                attempt += 1
                if attempt >= max_attempts:
                    print("⚠️ Input error occurred. Using default task.")
                    return "Complete a general task"
        
        # Fallback
        return "Complete a general task"
    
    def run_complete_workflow(self, user_input: str):
        """Run the complete enhanced workflow with timeout protection and error handling"""
        print(f"\n🚀 Starting enhanced workflow for: '{user_input}'")
        
        # Add timeout protection
        start_time = time.time()
        max_workflow_time = 300  # 5 minutes max
        
        # Validate session manager before proceeding
        if not self.session_manager:
            print("❌ Session manager not available. Cannot proceed.")
            return
        
        # Use supervisor to coordinate workflow
        if self.supervisor:
            print("🎯 Supervisor agent coordinating workflow...")
        
        try:
            # Step 1: Extract task with timeout protection
            print(f"\n🔍 Extracting task from: '{user_input}'")
            if time.time() - start_time > max_workflow_time:
                raise Exception("Workflow timeout exceeded")
                
            extraction_agent = TaskExtractionAgent()
            actions = extraction_agent.extract_task(user_input, existing_tasks=[])
            
            if not actions or len(actions) == 0:
                raise TaskExtractionError("Task extraction failed")
            
            action = actions[0]
            task_heading = action.get('heading', 'Unknown Task')
            task_details = action.get('details', '')
            extracted_deadline = action.get('deadline')
            
            # Ensure task_details is not empty for planning agent
            if not task_details or task_details.strip() == '':
                task_details = f'Complete the task: {task_heading}. This involves learning and implementing the required skills and knowledge.'
            
            print(f"✅ Task extracted: {task_heading}")
            if extracted_deadline:
                print(f"📅 Deadline detected: {extracted_deadline}")
            
            # Step 2: Plan subtasks with timeout protection
            print(f"\n📋 Planning subtasks for: '{task_heading}'")
            if time.time() - start_time > max_workflow_time:
                raise Exception("Workflow timeout exceeded")
                
            planning_agent = PlanningAgent()
            # Store planning agent for later use in orchestrator
            self.planning_agent = planning_agent
            
            # Generate initial subtasks for the task
            task_id = f"task_{self.current_user_id}_{int(time.time())}"
            initial_subtasks = planning_agent.generate_initial_subtasks({
                "heading": task_heading,
                "details": task_details,
                "deadline": extracted_deadline,
                "previous_chunks": [],
                "corrections_or_feedback": ""
            }, task_id)
            
            if not initial_subtasks:
                raise PlanningAgentError("Task planning failed")
            
            # Get the first subtask to display
            first_subtask = initial_subtasks[0] if initial_subtasks else None
            
            print(f"✅ Generated {len(initial_subtasks)} subtasks")
            print(f"✅ First subtask: {first_subtask['chunk_heading'] if first_subtask else 'None'}")
            
            # Step 3: Orchestrate scheduling with timeout protection
            print(f"\n🎯 Orchestrating schedule for: '{first_subtask['chunk_heading'] if first_subtask else 'Task'}'")
            if time.time() - start_time > max_workflow_time:
                raise Exception("Workflow timeout exceeded")
                
            orchestrator = GenieOrchestrator(prompt_file="prompts/genieorchestrator_ai.prompt")
            
            # Create orchestrator input data with ALL existing tasks + new task
            all_existing_tasks = []
            
            # Get all existing tasks from storage
            if self.store:
                try:
                    existing_tasks = self.store.list_tasks(self.current_user_id)
                    for existing_task in existing_tasks:
                        # Convert existing task to orchestrator format
                        task_dict = {
                            "id": str(existing_task.id),
                            "heading": existing_task.heading,
                            "details": existing_task.details,
                            "deadline": existing_task.deadline.isoformat() if existing_task.deadline else None,
                            "priority_score": existing_task.metadata.get('priority_score', 5.0),
                            "subtasks": []
                        }
                        
                        # Try to get subtasks from planning agent if available
                        try:
                            # Check if planning agent has subtasks for this task
                            if hasattr(self, 'planning_agent') and self.planning_agent:
                                task_id_str = str(existing_task.id)
                                if task_id_str in self.planning_agent.subtask_pools:
                                    subtasks = self.planning_agent.subtask_pools[task_id_str]
                                    # Limit to 5 subtasks as requested
                                    limited_existing_subtasks = subtasks[:5]
                                    task_dict["subtasks"] = [{
                                        "id": subtask.get('chunk_order', i + 1),
                                        "heading": subtask['chunk_heading'],
                                        "details": subtask['chunk_details'],
                                        "estimated_time_minutes": subtask['estimated_time_minutes'],
                                        "status": "done" if subtask.get('chunk_order', i + 1) in self.planning_agent.completed_subtasks.get(task_id_str, []) else "pending",
                                        "resource": subtask.get('resource'),
                                        "dependencies": subtask.get('dependencies', []),
                                        "user_feedback": ""
                                    } for i, subtask in enumerate(limited_existing_subtasks)]
                        except Exception as e:
                            logger.debug(f"Could not load subtasks for task {existing_task.id}: {e}")
                        
                        all_existing_tasks.append(task_dict)
                except Exception as e:
                    logger.warning(f"Failed to load existing tasks: {e}")
            
            # Add the new task with its subtasks (limit to 5 subtasks as requested)
            limited_subtasks = initial_subtasks[:5]  # Take only first 5 subtasks
            
            new_task = {
                "id": task_id,
                "heading": task_heading,
                "details": task_details,
                "deadline": extracted_deadline,
                "priority_score": 8.0,
                "subtasks": [{
                    "id": subtask.get('chunk_order', i + 1),
                    "heading": subtask['chunk_heading'],
                    "details": subtask['chunk_details'],
                    "estimated_time_minutes": subtask['estimated_time_minutes'],
                    "status": "pending",
                    "resource": subtask.get('resource'),
                    "dependencies": subtask.get('dependencies', []),
                    "user_feedback": ""
                } for i, subtask in enumerate(limited_subtasks)]
            }
            
            all_existing_tasks.append(new_task)
            
            orchestrator_tasks = {
                "tasks": all_existing_tasks
            }
            
            # Debug: Show what tasks are being considered by AI-driven system
            print(f"\n🧠 AI-Driven Brain-Aware Orchestrator Analysis:")
            print(f"   📊 Considering {len(all_existing_tasks)} tasks with up to 5 subtasks each")
            print(f"   🧠 Current energy level: {energy_level}")
            print(f"   ⏰ Time context: {datetime.now().strftime('%A, %H:%M')}")
            
            total_subtasks = sum(len(task.get('subtasks', [])) for task in all_existing_tasks)
            print(f"   🎯 Total subtasks for AI analysis: {total_subtasks}")
            
            for i, task in enumerate(all_existing_tasks, 1):
                subtask_count = len(task.get('subtasks', []))
                print(f"   {i}. {task['heading']} (Priority: {task['priority_score']}, Subtasks: {subtask_count}/5)")
                # Show first few subtasks
                for j, subtask in enumerate(task.get('subtasks', [])[:3], 1):
                    print(f"      {j}. {subtask['heading']} ({subtask['estimated_time_minutes']} min)")
                if len(task.get('subtasks', [])) > 3:
                    print(f"      ... and {len(task.get('subtasks', [])) - 3} more subtasks")
            
            # Get availability if calendar API is available
            availability = {"free": [], "busy": []}
            if self.calendar_api:
                try:
                    start_time_calendar = datetime.now()
                    end_time_calendar = start_time_calendar + timedelta(days=7)
                    free_busy = self.calendar_api.get_free_busy(start_time_calendar, end_time_calendar)
                    availability = free_busy
                    print("✅ Calendar availability retrieved")
                except Exception as e:
                    logger.warning(f"Failed to get calendar availability: {e}")
                    print("⚠️ Using default availability (no calendar integration)")
            
            # Enhanced user schedule with psychological and contextual information
            current_hour = datetime.now().hour
            energy_level = "high" if 9 <= current_hour <= 11 or 14 <= current_hour <= 16 else "medium" if 8 <= current_hour <= 18 else "low"
            
            orchestrator_schedule = {
                "availability": availability,
                "preferences": {
                    "work_hours": {"start": "09:00", "end": "17:00"},
                    "timezone": "UTC",
                    "energy_patterns": {
                        "current_energy": energy_level,
                        "peak_hours": ["09:00-11:00", "14:00-16:00"],
                        "low_energy_hours": ["13:00-14:00", "17:00-19:00"]
                    },
                    "cognitive_preferences": {
                        "preferred_task_duration": "25-45 minutes",
                        "focus_type": "deep_work",
                        "break_frequency": "every_90_minutes"
                    }
                },
                "current_time": datetime.now().isoformat(),
                "contextual_factors": {
                    "day_of_week": datetime.now().strftime("%A"),
                    "time_of_day": current_hour,
                    "energy_state": energy_level,
                    "focus_capacity": "high" if energy_level == "high" else "medium",
                    "motivation_level": "high",  # Could be learned from user feedback
                    "stress_level": "low"  # Could be learned from user feedback
                },
                "psychological_state": {
                    "procrastination_tendency": "low",  # Could be learned
                    "perfectionism_level": "medium",  # Could be learned
                    "social_energy": "medium",  # Could be learned
                    "creativity_peak": "morning"  # Could be learned
                }
            }
            
            # Convert to JSON with proper datetime handling
            def convert_datetime_to_iso(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime_to_iso(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime_to_iso(item) for item in obj]
                else:
                    return obj
            
            serializable_tasks = convert_datetime_to_iso(orchestrator_tasks)
            serializable_schedule = convert_datetime_to_iso(orchestrator_schedule)
            
            all_tasks_json = json.dumps(serializable_tasks, indent=2)
            user_schedule_json = json.dumps(serializable_schedule, indent=2)
            
            next_action = orchestrator.get_next_action(all_tasks_json, user_schedule_json)
            
            if not next_action:
                raise GenieOrchestratorError("Orchestrator failed to determine next action")
            
            print(f"✅ AI-Selected Next Action: {next_action.get('chunk_heading', 'Unknown')}")
            if next_action.get('scheduled_time_start'):
                print(f"   📅 Scheduled for: {next_action['scheduled_time_start']}")
            
            # Show AI analysis if available
            if next_action.get('ai_analysis'):
                ai_analysis = next_action['ai_analysis']
                print(f"\n🧠 AI Analysis:")
                if ai_analysis.get('psychological_factors'):
                    psych = ai_analysis['psychological_factors']
                    print(f"   💭 Motivation: {psych.get('motivation_score', 'N/A')}")
                    print(f"   🌊 Flow Potential: {psych.get('flow_potential', 'N/A')}")
                    print(f"   🧠 Cognitive Load: {psych.get('cognitive_load', 'N/A')}")
                    print(f"   ⚡ Energy Match: {psych.get('energy_match', 'N/A')}")
                
                if ai_analysis.get('adaptive_reasoning'):
                    reasoning = ai_analysis['adaptive_reasoning']
                    print(f"   🎯 Why This Choice: {reasoning.get('why_this_choice', 'N/A')[:100]}...")
                    print(f"   🔄 Contextual Fit: {reasoning.get('contextual_fit', 'N/A')[:100]}...")
            
            # Step 4: Create calendar event with error handling (ONLY for next 30-minute task)
            event_id = None
            if self.calendar_api and next_action.get('scheduled_time_start'):
                # Check if this is a task that should be scheduled (next 30 minutes or less)
                estimated_time = next_action.get('estimated_time_minutes', 30)
                start_time_event = datetime.fromisoformat(next_action['scheduled_time_start'].replace('Z', '+00:00'))
                end_time_event = datetime.fromisoformat(next_action['scheduled_time_end'].replace('Z', '+00:00'))
                
                # Only schedule if:
                # 1. Task is 30 minutes or less
                # 2. Task is scheduled within the next 2 hours (immediate focus)
                # 3. Task is not already in the past
                current_time = datetime.now()
                time_until_start = (start_time_event - current_time).total_seconds() / 60  # minutes
                
                should_schedule = (
                    estimated_time <= 30 and  # Only 30-minute or shorter tasks
                    time_until_start <= 120 and  # Only tasks starting within 2 hours
                    time_until_start >= -5  # Not more than 5 minutes in the past
                )
                
                if should_schedule:
                    print(f"\n📅 Creating calendar event for: '{next_action.get('chunk_heading', 'Task')}'")
                    print(f"   ⏱️  Duration: {estimated_time} minutes")
                    print(f"   🕐 Starts in: {int(time_until_start)} minutes")
                    
                    try:
                        event_id = self.calendar_api.create_event(
                            summary=f"[Genie] {next_action['chunk_heading']}",
                            description=f"Task: {task_heading}\n\n{next_action['chunk_details']}\n\nResource: {next_action['resource']['title']}",
                            start_datetime=start_time_event,
                            end_datetime=end_time_event
                        )
                        
                        if event_id:
                            print(f"✅ Calendar event created: {event_id}")
                        else:
                            print("❌ Failed to create calendar event")
                    
                    except Exception as e:
                        logger.error(f"Calendar event creation failed: {e}")
                        print(f"❌ Failed to create calendar event: {e}")
                else:
                    print(f"\n⏭️  Skipping calendar event creation:")
                    print(f"   ⏱️  Duration: {estimated_time} minutes (only scheduling ≤30 min tasks)")
                    print(f"   🕐 Starts in: {int(time_until_start)} minutes (only scheduling tasks starting within 2 hours)")
                    print(f"   📝 Task will be tracked in system but not added to calendar")
            
            # Step 5: Save to storage with session validation
            print(f"\n💾 Saving task to storage...")
            try:
                # Validate storage is available
                if not self.store:
                    raise Exception("Storage system not available")
                
                # Create Task object (simple, no complex parameters)
                task = Task(
                    heading=task_heading,
                    details=task_details,
                    time_estimate=first_subtask['estimated_time_minutes'] if first_subtask else 30
                )
                
                # Add task to storage
                self.store.add_task(self.current_user_id, task)
                print(f"✅ Task saved with ID: {task.id}")
                
                # Create or update user session with validation
                if self.session_manager:
                    try:
                        session = self.session_manager.create_session(self.current_user_id)
                        if not session:
                            raise Exception("Failed to create user session")
                            
                        session.current_focus_task = str(task.id)
                        
                        # Store planning and orchestration data
                        if not hasattr(session, 'task_planning_data'):
                            session.task_planning_data = {}
                        session.task_planning_data[str(task.id)] = {
                            'chunk': first_subtask,
                            'next_action': next_action,
                            'orchestrator_tasks': orchestrator_tasks,
                            'all_subtasks': initial_subtasks,
                            'planning_agent': planning_agent,
                            'task_id': task_id
                        }
                        
                        self.session_manager.save_session(session)
                        self.current_session = session
                        print(f"✅ User session created/updated")
                        
                    except Exception as e:
                        logger.error(f"Session management failed: {e}")
                        print(f"⚠️ Session management failed: {e}")
                        # Continue without session if it fails
                
            except Exception as e:
                logger.error(f"Task storage failed: {e}")
                print(f"❌ Failed to save task: {e}")
            
            # Step 6: Provide summary
            self._provide_workflow_summary(task_heading, task_details, first_subtask, next_action, event_id, initial_subtasks)
            
            # Step 7: Enhanced feedback loop with timeout protection
            if time.time() - start_time < max_workflow_time:
                self._provide_enhanced_feedback_loop(str(task.id), str(first_subtask.get('chunk_order', 1) if first_subtask else 1), planning_agent, task_id)
            
            print(f"\n🎉 Enhanced workflow completed successfully!")
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            print(f"❌ Workflow failed: {e}")
            print("Please try again or contact support if the issue persists.")
    
    def _provide_workflow_summary(self, task_heading: str, task_details: str, first_subtask: Dict[str, Any], next_action: Dict[str, Any], event_id: Optional[str], all_subtasks: List[Dict[str, Any]]):
        """Provide a comprehensive summary of the completed workflow"""
        print(f"\n" + "="*60)
        print("📋 ENHANCED WORKFLOW SUMMARY")
        print("="*60)
        print(f"🎯 Task: {task_heading}")
        print(f"📝 Details: {task_details[:100]}...")
        print(f"🔧 Next Action: {first_subtask['chunk_heading'] if first_subtask else 'Unknown'}")
        print(f"⏱️  Estimated Time: {first_subtask['estimated_time_minutes'] if first_subtask else 30} minutes")
        print(f"📊 Total Subtasks Generated: {len(all_subtasks)}")
        
        if next_action.get('scheduled_time_start'):
            print(f"📅 Scheduled: {next_action['scheduled_time_start']}")
        
        if event_id:
            print(f"📅 Calendar Event: Created (ID: {event_id})")
        
        if first_subtask and first_subtask.get('resource') and first_subtask['resource'].get('title'):
            print(f"📚 Resource: {first_subtask['resource']['title']}")
            if first_subtask['resource'].get('url'):
                print(f"🔗 URL: {first_subtask['resource']['url']}")
        else:
            print("📚 Resource: No specific resource provided")
        
        # Show all subtasks
        if all_subtasks:
            print(f"\n📋 All Subtasks ({len(all_subtasks)}):")
            for i, subtask in enumerate(all_subtasks, 1):
                print(f"  {i}. {subtask['chunk_heading']} ({subtask['estimated_time_minutes']} min)")
        
        print("="*60)
    
    def _provide_enhanced_feedback_loop(self, task_id: str, chunk_id: str, planning_agent: PlanningAgent, task_id_internal: str):
        """Provide enhanced feedback collection loop with timeout protection and error handling"""
        print(f"\n🔄 Enhanced Feedback Loop")
        print("After completing your task, you can provide feedback to improve future planning.")
        print("Commands:")
        print("  • 'done' - Mark task as completed and get next subtask")
        print("  • 'difficult' - Report task was more difficult than expected")
        print("  • 'easy' - Report task was easier than expected")
        print("  • 'skip' - Skip feedback for now")
        
        # Add timeout protection for feedback input
        max_feedback_attempts = 3
        feedback_attempt = 0
        
        while feedback_attempt < max_feedback_attempts:
            try:
                feedback_input = input("\nEnter feedback command: ").strip().lower()
                
                if feedback_input in ['done', 'difficult', 'easy', 'skip']:
                    break
                else:
                    feedback_attempt += 1
                    remaining = max_feedback_attempts - feedback_attempt
                    if remaining > 0:
                        print(f"❌ Invalid feedback command. ({remaining} attempts remaining)")
                    else:
                        print("⚠️ Maximum feedback attempts reached. Skipping feedback.")
                        return
                        
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye! Thanks for using Enhanced Genie!")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Feedback input error: {e}")
                feedback_attempt += 1
                if feedback_attempt >= max_feedback_attempts:
                    print("⚠️ Feedback input error occurred. Skipping feedback.")
                    return
        
        if feedback_input == 'skip':
            print("⏭️ Skipping feedback")
            return
        
        try:
            # Initialize enhanced feedback agent with timeout protection
            feedback_agent = FeedbackAgent()
            
            # Determine feedback type and content
            if feedback_input == 'done':
                feedback_type = "completion"
                feedback_text = "Task completed successfully"
                rating = 5
            elif feedback_input == 'difficult':
                feedback_type = "difficulty"
                feedback_text = "Task was more difficult than expected"
                rating = 3
            elif feedback_input == 'easy':
                feedback_type = "difficulty"
                feedback_text = "Task was easier than expected"
                rating = 4
            else:
                print("❌ Invalid feedback command")
                return
            
            # Prepare feedback data
            feedback = {
                "task_id": task_id,
                "chunk_id": chunk_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "rating": rating,
                "time_taken_minutes": 0
            }
            
            # Prepare current state
            current_state = {
                "user_id": self.current_user_id,
                "tasks": [],
                "current_focus_task": task_id,
                "session_start_time": datetime.now().isoformat()
            }
            
            # Process feedback with enhanced agent and timeout protection
            start_time = time.time()
            max_feedback_time = 60  # 1 minute max for feedback processing
            
            processed = feedback_agent.process_feedback(feedback, current_state)
            
            if time.time() - start_time > max_feedback_time:
                print("⚠️ Feedback processing timeout. Continuing without feedback.")
                return
            
            if processed and processed.get('success', False):
                print("✅ Enhanced feedback processed successfully")
                print(f"💬 {processed.get('motivational_message', 'Great job!')}")
                
                # Check if next subtask was generated with timeout protection
                if processed.get('should_trigger_next_subtask'):
                    next_subtask_data = processed.get('next_subtask_data')
                    
                    if next_subtask_data:
                        print(f"➡️  Next subtask: {next_subtask_data.get('chunk_heading', 'Unknown')}")
                        print(f"📝 Details: {next_subtask_data.get('chunk_details', '')[:100]}...")
                        print(f"⏱️  Estimated time: {next_subtask_data.get('estimated_time_minutes', 30)} minutes")
                    else:
                        # Try to get next subtask from planning agent with timeout protection
                        try:
                            if time.time() - start_time < max_feedback_time:
                                next_subtask = planning_agent.mark_subtask_completed(task_id_internal, int(chunk_id))
                                if next_subtask:
                                    print(f"➡️  Next subtask: {next_subtask['chunk_heading']}")
                                    print(f"📝 Details: {next_subtask['chunk_details'][:100]}...")
                                    print(f"⏱️  Estimated time: {next_subtask['estimated_time_minutes']} minutes")
                                else:
                                    print("🎉 All subtasks completed! Task finished.")
                            else:
                                print("⚠️ Planning agent timeout. Task completed!")
                        except Exception as e:
                            logger.warning(f"Failed to get next subtask from planning agent: {e}")
                            print("🎉 Task completed! No more subtasks available.")
                else:
                    print("🎯 Your feedback will help improve future task planning!")
            else:
                print("⚠️ Enhanced feedback processing failed")
                
        except Exception as e:
            logger.error(f"Enhanced feedback processing failed: {e}")
            print(f"❌ Failed to process enhanced feedback: {e}")
    
    def run_interactive_session(self):
        """Run the main interactive session with enhanced error handling and timeout protection"""
        print("🎉 Welcome to Enhanced Genie - Your AI Task Management Assistant!")
        print("I'll help you break down tasks, plan them, and schedule them in your calendar.")
        print("Enhanced with better deadline extraction, subtask flow, and feedback loops!")
        
        session_start_time = time.time()
        max_session_time = 3600  # 1 hour max session
        
        while True:
            try:
                # Check session timeout
                if time.time() - session_start_time > max_session_time:
                    print("\n⏰ Session timeout reached. Thank you for using Enhanced Genie!")
                    break
                
                # Get user input with timeout protection
                user_input = self.get_user_input()
                
                if not user_input.strip():
                    print("⚠️ Please provide a task description.")
                    continue
                
                # Validate session manager before running workflow
                if not self.session_manager:
                    print("❌ Session manager not available. Please restart the application.")
                    break
                
                # Run complete enhanced workflow
                self.run_complete_workflow(user_input)
                
                # Ask if user wants to continue with timeout protection
                print(f"\n" + "-"*40)
                continue_attempts = 0
                max_continue_attempts = 3
                
                while continue_attempts < max_continue_attempts:
                    try:
                        continue_input = input("Would you like to add another task? (y/n): ").strip().lower()
                        
                        if continue_input in ['y', 'yes', 'continue']:
                            break
                        elif continue_input in ['n', 'no', 'exit', 'quit']:
                            print("👋 Thanks for using Enhanced Genie! Have a productive day!")
                            return
                        else:
                            continue_attempts += 1
                            remaining = max_continue_attempts - continue_attempts
                            if remaining > 0:
                                print(f"⚠️ Please enter 'y' or 'n'. ({remaining} attempts remaining)")
                            else:
                                print("⚠️ Maximum attempts reached. Exiting session.")
                                return
                                
                    except (EOFError, KeyboardInterrupt):
                        print("\n\n👋 Goodbye! Thanks for using Enhanced Genie!")
                        return
                    except Exception as e:
                        logger.error(f"Continue input error: {e}")
                        continue_attempts += 1
                        if continue_attempts >= max_continue_attempts:
                            print("⚠️ Input error occurred. Exiting session.")
                            return
                
                # If we get here, user wants to continue
                continue
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using Enhanced Genie!")
                break
            except Exception as e:
                logger.error(f"Session error: {e}")
                print(f"❌ An error occurred: {e}")
                print("Please try again or contact support if the issue persists.")
                
                # Add a small delay to prevent rapid error loops
                time.sleep(2)

def main():
    """Main function to run the enhanced interactive Genie system"""
    try:
        # Initialize enhanced interactive system
        genie_system = GenieInteractiveSystem()
        
        # Run interactive session
        genie_system.run_interactive_session()
        
    except Exception as e:
        logger.error(f"❌ Enhanced system crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"❌ Enhanced system error: {e}")
        print("Please check your configuration and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 