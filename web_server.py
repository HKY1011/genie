#!/usr/bin/env python3
"""
Enhanced Flask Web Server for Genie Task Management UI
Provides REST APIs and serves the web interface
Fixed to properly integrate with enhanced backend functionality.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Import our Genie system components
from main import GenieInteractiveSystem
from storage.json_store import JsonStore
from models.task_model import Task, TaskStatus

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Genie system
genie_system = None
store = None

def initialize_system():
    """Initialize the Genie system and storage"""
    global genie_system, store
    try:
        genie_system = GenieInteractiveSystem()
        store = genie_system.store
        logger.info("✅ Genie system initialized for web server")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Genie system: {e}")
        raise

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if system is responsive
        if store is None:
            return jsonify({"status": "unhealthy", "error": "Storage not initialized"}), 503
        
        # Basic system check
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "storage": "ok",
                "api": "ok"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks for the current user"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        tasks = store.list_tasks(user_id)
        
        # Convert tasks to JSON-serializable format
        task_list = []
        for task in tasks:
            task_data = {
                'id': str(task.id),
                'name': task.heading,
                'details': task.details,
                'status': task.status.value,
                'totalTime': task.time_estimate * 60 if task.time_estimate else 25 * 60,  # Convert to seconds
                'timeLeft': task.time_estimate * 60 if task.time_estimate else 25 * 60,
                'resources': 'Notes, Links',  # Placeholder
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
            task_list.append(task_data)
        
        return jsonify({
            'success': True,
            'tasks': task_list
        })
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task using the complete Genie workflow"""
    try:
        data = request.get_json()
        user_input = data.get('task_name', '').strip()
        user_id = data.get('user_id', 'default_user')
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'Task name is required'
            }), 400
        
        # Run the complete Genie workflow
        logger.info(f"Running complete workflow for user {user_id}: {user_input}")
        
        # Step 1: Extract task using enhanced TaskExtractionAgent
        from agents.task_extraction_agent import TaskExtractionAgent
        extraction_agent = TaskExtractionAgent()
        actions = extraction_agent.extract_task(user_input, existing_tasks=[])
        
        if not actions or len(actions) == 0:
            raise Exception("Failed to extract task from input")
        
        action = actions[0]
        task_heading = action.get('heading', 'Unknown Task')
        task_details = action.get('details', '')
        
        # Ensure task_details is not empty for planning agent
        if not task_details or task_details.strip() == '':
            task_details = f'Complete the task: {task_heading}. This involves learning and implementing the required skills and knowledge.'
        
        logger.info(f"✅ Task extracted: {task_heading}")
        
        # Step 2: Plan subtasks using enhanced PlanningAgent
        from agents.planning_agent import PlanningAgent
        planning_agent = PlanningAgent()
        
        # Generate initial subtasks for the task
        task_id = f"task_{user_id}_{int(time.time())}"
        initial_subtasks = planning_agent.generate_initial_subtasks({
            "heading": task_heading,
            "details": task_details,
            "deadline": action.get('deadline'),
            "previous_chunks": [],
            "corrections_or_feedback": ""
        }, task_id)
        
        if not initial_subtasks:
            raise Exception("Task planning failed")
        
        # Get the first subtask to display
        first_subtask = initial_subtasks[0] if initial_subtasks else None
        
        logger.info(f"✅ Generated {len(initial_subtasks)} subtasks")
        logger.info(f"✅ First subtask: {first_subtask['chunk_heading'] if first_subtask else 'None'}")
        
        # Step 3: Orchestrate scheduling using GenieOrchestrator
        from agents.genieorchestrator_agent import GenieOrchestrator
        orchestrator = GenieOrchestrator()
        
        # Create orchestrator input data
        orchestrator_tasks = {
            "tasks": [{
                "id": task_id,
                "heading": task_heading,
                "details": task_details,
                "deadline": action.get('deadline'),
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
                } for i, subtask in enumerate(initial_subtasks)]
            }]
        }
        
        # Get availability if calendar API is available
        availability = {"free": [], "busy": []}
        if genie_system.calendar_api:
            try:
                start_time = datetime.now()
                end_time = start_time + timedelta(days=7)
                free_busy = genie_system.calendar_api.get_free_busy(start_time, end_time)
                availability = free_busy
                logger.info("✅ Calendar availability retrieved")
            except Exception as e:
                logger.warning(f"Failed to get calendar availability: {e}")
        
        orchestrator_schedule = {
            "availability": availability,
            "preferences": {
                "work_hours": {"start": "09:00", "end": "17:00"},
                "timezone": "UTC"
            },
            "current_time": datetime.now().isoformat()
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
            raise Exception("Orchestrator failed to determine next action")
        
        logger.info(f"✅ Next action scheduled: {next_action.get('chunk_heading', 'Unknown')}")
        
        # Step 4: Create Task object and save to storage
        from models.task_model import Task
        task = Task(
            heading=task_heading,
            details=task_details,
            time_estimate=first_subtask['estimated_time_minutes'] if first_subtask else 30
        )
        
        # Add task to storage
        store.add_task(user_id, task)
        
        # Step 5: Store planning and orchestration data
        task_data = {
            'id': str(task.id),
            'name': task.heading,
            'details': task.details,
            'status': task.status.value,
            'totalTime': task.time_estimate * 60 if task.time_estimate else 25 * 60,
            'timeLeft': task.time_estimate * 60 if task.time_estimate else 25 * 60,
            'resources': first_subtask.get('resource', {}).get('title', 'Notes, Links') if first_subtask else 'Notes, Links',
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            # Store planning and orchestration data
            'chunk_data': first_subtask,
            'next_action': next_action,
            'orchestrator_tasks': orchestrator_tasks,
            'all_subtasks': initial_subtasks
        }
        
        # Create or update user session
        session = genie_system.session_manager.get_or_create_session(user_id)
        session.current_focus_task = str(task.id)
        
        # Store the planning and orchestration data
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
        
        # Save the session immediately
        genie_system.session_manager.save_session(session)
        
        # Also store in the main storage for persistence
        store.add_feedback(user_id, {
            'task_id': str(task.id),
            'planning_data': {
                'chunk': first_subtask,
                'next_action': next_action,
                'orchestrator_tasks': orchestrator_tasks,
                'all_subtasks': initial_subtasks,
                'task_id': task_id
            },
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'task': task_data,
            'message': 'Task created successfully using complete Genie AI workflow'
        })
            
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task (e.g., mark as complete)"""
    try:
        data = request.get_json()
        user_id = request.args.get('user_id', 'default_user')
        
        # Get the task
        task = store.get_task(user_id, task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        # Update task status
        if 'status' in data:
            new_status = TaskStatus(data['status'])
            store.update_task(user_id, task_id, status=new_status.value)
        
        # Update other fields if provided
        if 'details' in data:
            store.update_task(user_id, task_id, details=data['details'])
        
        if 'time_estimate' in data:
            store.update_task(user_id, task_id, time_estimate=data['time_estimate'])
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        # Delete the task
        store.delete_task(user_id, task_id)
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/available-hours', methods=['GET'])
def get_available_hours():
    """Get available hours for scheduling"""
    try:
        # Return default available hours
        available_hours = {
            "work_hours": {
                "start": "09:00",
                "end": "17:00"
            },
            "timezone": "UTC",
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }
        
        return jsonify({
            'success': True,
            'available_hours': available_hours
        })
        
    except Exception as e:
        logger.error(f"Error getting available hours: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for a completed task using the enhanced feedback system"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract and validate required fields
        task_id = data.get('task_id')
        chunk_id = data.get('chunk_id', '1')
        feedback_type = data.get('feedback_type', 'completion')
        feedback_text = data.get('feedback_text', 'Task completed')
        rating = data.get('rating', 5)
        user_id = data.get('user_id', 'default_user')
        
        # Map UI feedback types to API types
        feedback_type_mapping = {
            'done': 'completion',
            'difficult': 'difficulty',
            'easy': 'difficulty'
        }
        feedback_type = feedback_type_mapping.get(feedback_type, feedback_type)
        
        # If no task_id provided, try to get from current session
        if not task_id:
            session = genie_system.session_manager.get_or_create_session(user_id)
            if session.current_focus_task:
                task_id = session.current_focus_task
            else:
                return jsonify({
                    'success': False,
                    'error': 'No task ID provided and no current task in session'
                }), 400
        
        # Validate task exists
        task = store.get_task(user_id, task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': f'Task with ID {task_id} not found'
            }), 404
        
        # Process feedback using the enhanced feedback system
        from agents.feedback_agent import FeedbackAgent
        feedback_agent = FeedbackAgent()
        
        # Get current session for better context
        session = genie_system.session_manager.get_or_create_session(user_id)
        
        feedback = {
            "task_id": task_id,
            "chunk_id": chunk_id,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "rating": rating,
            "time_taken_minutes": 0
        }
        
        # Create comprehensive current state with error handling
        try:
            current_state = {
                "user_id": user_id,
                "tasks": [task.to_dict() for task in session.tasks] if hasattr(session, 'tasks') else [],
                "current_focus_task": session.current_focus_task,
                "session_start_time": session.session_start_time.isoformat() if session.session_start_time else datetime.now().isoformat(),
                "completion_history": [h.to_dict() for h in session.completion_history] if hasattr(session, 'completion_history') else [],
                "energy_patterns": [p.to_dict() for p in session.energy_patterns] if hasattr(session, 'energy_patterns') else []
            }
        except Exception as e:
            logger.warning(f"Error creating current state: {e}")
            current_state = {
                "user_id": user_id,
                "tasks": [],
                "current_focus_task": task_id,
                "session_start_time": datetime.now().isoformat()
            }
        
        # Process feedback using the enhanced feedback agent
        try:
            feedback_result = feedback_agent.process_feedback(feedback, current_state)
        except Exception as e:
            logger.error(f"Feedback agent error: {e}")
            feedback_result = {
                'success': True,
                'motivational_message': 'Feedback received!',
                'should_trigger_next_subtask': False
            }
        
        if feedback_result and feedback_result.get('success', False):
            # Update the task status if it's a completion feedback
            if feedback_type == 'completion':
                try:
                    store.update_task(user_id, task_id, status='done')
                except Exception as e:
                    logger.warning(f"Failed to update task status: {e}")
            
            # Store feedback in the session with error handling
            try:
                if hasattr(session, 'completion_history'):
                    from models.user_session import CompletionHistory
                    history = CompletionHistory(
                        task_id=task_id,
                        estimated_time=0,  # Will be updated from task
                        actual_time=0,  # Will be updated from feedback
                        difficulty_rating=rating,
                        energy_level=5,  # Default
                        productivity_rating=rating,
                        notes=feedback_text
                    )
                    session.completion_history.append(history)
                    genie_system.session_manager.save_session(session)
            except Exception as e:
                logger.warning(f"Failed to store feedback in session: {e}")
            
            # Check if we need to generate next subtask
            next_subtask_data = None
            if feedback_result.get('should_trigger_next_subtask'):
                next_subtask_data = feedback_result.get('next_subtask_data')
                
                # If feedback agent didn't generate next subtask, try planning agent
                if not next_subtask_data and session.current_focus_task:
                    try:
                        planning_data = session.task_planning_data.get(session.current_focus_task, {})
                        planning_agent = planning_data.get('planning_agent')
                        
                        if planning_agent:
                            # Mark current subtask as completed
                            next_subtask = planning_agent.mark_subtask_completed(
                                planning_data.get('task_id', task_id),
                                int(chunk_id)
                            )
                            
                            if next_subtask:
                                next_subtask_data = {
                                    "chunk_heading": next_subtask["chunk_heading"],
                                    "chunk_details": next_subtask["chunk_details"],
                                    "estimated_time_minutes": next_subtask["estimated_time_minutes"],
                                    "resource": next_subtask.get("resource", {}),
                                    "chunk_order": next_subtask.get("chunk_order", 1),
                                    "subtask_id": next_subtask.get("subtask_id", f"subtask_{task_id}_{next_subtask.get('chunk_order', 1)}"),
                                    "status": "pending"
                                }
                    except Exception as e:
                        logger.warning(f"Failed to generate next subtask: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Feedback processed successfully',
                'recommendations': feedback_result.get('recommendations', []),
                'motivational_message': feedback_result.get('motivational_message', 'Great job!'),
                'next_subtask': next_subtask_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to process feedback'
            }), 500
            
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/current-subtask', methods=['GET'])
def get_current_subtask():
    """Get the current active subtask from the enhanced planning system"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        # Get current session with error handling
        try:
            session = genie_system.session_manager.get_or_create_session(user_id)
        except Exception as e:
            logger.warning(f"Failed to get session: {e}")
            return jsonify({
                'success': True,
                'subtask': None,
                'message': 'No active session'
            })
        
        if not session.current_focus_task:
            return jsonify({
                'success': True,
                'subtask': None,
                'message': 'No active subtask'
            })
        
        # Get the current task with error handling
        try:
            current_task_id = session.current_focus_task
            current_task = store.get_task(user_id, current_task_id)
        except Exception as e:
            logger.warning(f"Failed to get current task: {e}")
            return jsonify({
                'success': True,
                'subtask': None,
                'message': 'Current task not found'
            })
        
        if not current_task:
            return jsonify({
                'success': True,
                'subtask': None,
                'message': 'Current task not found'
            })
        
        # Get the planning and orchestration data from session with error handling
        planning_data = None
        next_action = None
        chunk = None
        planning_agent = None
        
        try:
            # First try to get from session
            if hasattr(session, 'task_planning_data') and current_task_id in session.task_planning_data:
                planning_data = session.task_planning_data[current_task_id]
                next_action = planning_data.get('next_action')
                chunk = planning_data.get('chunk')
                planning_agent = planning_data.get('planning_agent')
            
            # If not in session, try to get from main storage
            if not planning_data:
                try:
                    feedback_data = store.get_feedback(user_id)
                    for feedback in feedback_data:
                        if feedback.get('task_id') == current_task_id and 'planning_data' in feedback:
                            planning_data = feedback['planning_data']
                            next_action = planning_data.get('next_action')
                            chunk = planning_data.get('chunk')
                            break
                except Exception as e:
                    logger.warning(f"Failed to get feedback data: {e}")
        except Exception as e:
            logger.warning(f"Failed to get planning data: {e}")
        
        # If we have a planning agent, try to get the next available subtask
        if planning_agent and planning_data:
            try:
                task_id = planning_data.get('task_id', current_task_id)
                
                # Get the next available subtask
                next_subtask = planning_agent._generate_next_subtask(task_id)
                
                if next_subtask:
                    subtask_data = {
                        'task_id': str(current_task.id),
                        'chunk_id': str(next_subtask.get('chunk_order', 1)),
                        'chunk_heading': next_subtask.get('chunk_heading', 'Continue task'),
                        'chunk_details': next_subtask.get('chunk_details', 'Continue working on the task'),
                        'status': 'pending',
                        'estimated_time_minutes': next_subtask.get('estimated_time_minutes', 30),
                        'time_left': next_subtask.get('estimated_time_minutes', 30),
                        'resource': next_subtask.get('resource', {}),
                        'scheduled_time_start': None,
                        'scheduled_time_end': None,
                        'priority_score': 8.0
                    }
                    
                    return jsonify({
                        'success': True,
                        'subtask': subtask_data
                    })
            except Exception as e:
                logger.warning(f"Failed to generate next subtask: {e}")
        
        # Fallback: Use chunk data if available
        if chunk:
            subtask_data = {
                'task_id': str(current_task.id),
                'chunk_id': str(chunk.get('chunk_order', 1)),
                'chunk_heading': chunk.get('chunk_heading', current_task.heading),
                'chunk_details': chunk.get('chunk_details', current_task.details),
                'status': 'pending',
                'estimated_time_minutes': chunk.get('estimated_time_minutes', current_task.time_estimate or 30),
                'time_left': chunk.get('estimated_time_minutes', current_task.time_estimate or 30),
                'resource': chunk.get('resource', {}),
                'scheduled_time_start': None,
                'scheduled_time_end': None,
                'priority_score': 8.0
            }
            
            return jsonify({
                'success': True,
                'subtask': subtask_data
            })
        
        # Final fallback: Create a basic subtask from the current task
        subtask_data = {
            'task_id': str(current_task.id),
            'chunk_id': '1',
            'chunk_heading': current_task.heading,
            'chunk_details': current_task.details,
            'status': current_task.status.value,
            'estimated_time_minutes': current_task.time_estimate or 30,
            'time_left': current_task.time_estimate or 30,
            'resource': {},
            'scheduled_time_start': None,
            'scheduled_time_end': None,
            'priority_score': 8.0
        }
        
        return jsonify({
            'success': True,
            'subtask': subtask_data
        })
        
    except Exception as e:
        logger.error(f"Error getting current subtask: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tasks/<task_id>/subtasks', methods=['GET'])
def get_task_subtasks(task_id):
    """Get all subtasks for a specific task"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        # Get the task
        task = store.get_task(user_id, task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        # Get session to access planning data
        session = genie_system.session_manager.get_or_create_session(user_id)
        
        # Try to get subtasks from planning data
        subtasks = []
        if hasattr(session, 'task_planning_data') and task_id in session.task_planning_data:
            planning_data = session.task_planning_data[task_id]
            all_subtasks = planning_data.get('all_subtasks', [])
            
            for subtask in all_subtasks:
                subtask_data = {
                    'id': subtask.get('subtask_id', f"subtask_{task_id}_{subtask.get('chunk_order', 1)}"),
                    'heading': subtask['chunk_heading'],
                    'details': subtask['chunk_details'],
                    'status': subtask.get('status', 'pending'),
                    'estimated_time_minutes': subtask['estimated_time_minutes'],
                    'resource': subtask.get('resource', {}),
                    'chunk_order': subtask.get('chunk_order', 1)
                }
                subtasks.append(subtask_data)
        
        # If no subtasks found, create a basic one from the task
        if not subtasks:
            subtasks = [{
                'id': f"subtask_{task_id}_1",
                'heading': task.heading,
                'details': task.details,
                'status': task.status.value,
                'estimated_time_minutes': task.time_estimate or 25,
                'resource': {},
                'chunk_order': 1
            }]
        
        return jsonify({
            'success': True,
            'subtasks': subtasks
        })
        
    except Exception as e:
        logger.error(f"Error getting task subtasks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """Health check endpoint"""
    try:
        # Check if system is initialized
        if not genie_system or not store:
            return jsonify({
                'success': False,
                'error': 'System not initialized'
            }), 500
        
        # Check storage
        try:
            store.list_tasks('test_user')
            storage_ok = True
        except:
            storage_ok = False
        
        # Check APIs
        api_status = {
            'gemini_api': genie_system.gemini_client is not None,
            'perplexity_api': genie_system.perplexity_client is not None,
            'calendar_api': genie_system.calendar_api is not None,
            'storage': storage_ok
        }
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'apis': api_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    try:
        # Initialize the system
        initialize_system()
        
        # Get port from environment (Railway sets PORT)
        port = int(os.environ.get('PORT', 5000))
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=port)
        
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        sys.exit(1) 