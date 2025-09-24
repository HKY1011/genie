#!/usr/bin/env python3
"""
Supervisor Agent for Genie
Main orchestration loop that manages the feedback system and coordinates all agents.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

from agents.task_extraction_agent import TaskExtractionAgent, TaskExtractionError
from agents.feedback_agent import FeedbackAgent, FeedbackAgentError
from agents.genieorchestrator_agent import GenieOrchestrator, GenieOrchestratorError
from agents.planning_agent import PlanningAgent, PlanningAgentError
from models.user_session import UserSession, SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FeedbackEvent:
    """Structured feedback event for processing"""
    user_id: str
    user_input: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result of feedback processing"""
    success: bool
    user_message: str
    motivational_message: str
    next_action: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    confidence_score: float = 0.0


class SupervisorAgentError(Exception):
    """Custom exception for SupervisorAgent errors"""
    pass


class SupervisorAgent:
    """
    Supervisor Agent that orchestrates the complete feedback loop system.
    
    Flow:
    1. Receive user feedback (natural language)
    2. Extract structured actions via TaskExtractionAgent
    3. Process feedback and generate recommendations via FeedbackAgent
    4. Update system state and session
    5. Generate next action via GenieOrchestrator
    6. Return comprehensive response with motivational message
    """
    
    def __init__(self, session_manager: Optional[SessionManager] = None):
        """
        Initialize SupervisorAgent
        
        Args:
            session_manager: Session manager for persistent state
        """
        try:
            # Initialize all agents
            self.task_extractor = TaskExtractionAgent()
            self.feedback_agent = FeedbackAgent()
            self.orchestrator = GenieOrchestrator()
            self.planning_agent = PlanningAgent()
            
            # Session management
            self.session_manager = session_manager or SessionManager()
            
            logger.info("SupervisorAgent initialized successfully")
            
        except Exception as e:
            raise SupervisorAgentError(f"Failed to initialize SupervisorAgent: {e}")
    
    def process_user_feedback(self, user_input: str, user_id: str = "default") -> ProcessingResult:
        """
        Main method to process user feedback through the complete loop
        
        Args:
            user_input: Natural language user feedback
            user_id: User identifier for session management
            
        Returns:
            ProcessingResult with complete response
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Processing user feedback for user {user_id}: {user_input[:100]}...")
            
            # Step 1: Get or create user session
            session = self.session_manager.get_or_create_session(user_id)
            
            # Step 2: Extract structured actions from user input
            actions = self._extract_actions(user_input, session)
            if not actions:
                return ProcessingResult(
                    success=False,
                    user_message="I didn't understand that. Could you please rephrase?",
                    motivational_message="No worries! Let's try again.",
                    errors=["No actions extracted from user input"]
                )
            
            # Step 3: Process each action through the feedback loop
            results = []
            for action in actions:
                result = self._process_single_action(action, session)
                results.append(result)
            
            # Step 4: Update session with all changes
            self.session_manager.save_session(session)
            
            # Step 5: Generate next action recommendation
            next_action = self._generate_next_action(session)
            
            # Step 6: Compile final response
            final_result = self._compile_response(results, next_action, session)
            final_result.processing_time = time.time() - start_time
            
            logger.info(f"Feedback processing completed in {final_result.processing_time:.2f}s")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in feedback processing: {e}")
            return ProcessingResult(
                success=False,
                user_message="I encountered an error processing your feedback. Let me try again.",
                motivational_message="Don't worry, we'll get this sorted out!",
                errors=[str(e)],
                processing_time=time.time() - start_time
            )
    
    def _extract_actions(self, user_input: str, session: UserSession) -> List[Dict[str, Any]]:
        """Extract structured actions from user input"""
        try:
            # Convert session tasks to format expected by TaskExtractionAgent
            existing_tasks = session.tasks
            
            # Extract actions using TaskExtractionAgent
            actions = self.task_extractor.extract_task(user_input, existing_tasks)
            
            logger.info(f"Extracted {len(actions)} actions from user input")
            return actions
            
        except TaskExtractionError as e:
            logger.error(f"Task extraction error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in action extraction: {e}")
            return []
    
    def _process_single_action(self, action: Dict[str, Any], session: UserSession) -> Dict[str, Any]:
        """Process a single action through the feedback loop"""
        try:
            # Create current state for feedback processing
            current_state = self._create_current_state(session)
            
            # Process feedback and get recommendations
            feedback_result = self.feedback_agent.process_feedback(action, current_state)
            
            # Apply recommendations to session
            self._apply_recommendations(feedback_result, session)
            
            # Update session based on action
            self._update_session_from_action(action, session)
            
            return {
                "action": action,
                "feedback_result": feedback_result,
                "success": feedback_result.get("success", False)
            }
            
        except Exception as e:
            logger.error(f"Error processing action {action.get('action', 'unknown')}: {e}")
            return {
                "action": action,
                "feedback_result": {"success": False, "error": str(e)},
                "success": False
            }
    
    def _create_current_state(self, session: UserSession) -> Dict[str, Any]:
        """Create current state dictionary for feedback processing"""
        return {
            "user_id": session.user_id,
            "tasks": [task.to_dict() for task in session.tasks],
            "completion_history": [h.to_dict() for h in session.completion_history],
            "energy_patterns": [p.to_dict() for p in session.energy_patterns],
            "preferences": session.preferences.__dict__,
            "current_focus_task": session.current_focus_task,
            "total_focus_time": session.total_focus_time,
            "tasks_completed_today": session.tasks_completed_today,
            "total_focus_time_today": session.total_focus_time_today,
            "streak_days": session.streak_days
        }
    
    def _apply_recommendations(self, feedback_result: Dict[str, Any], session: UserSession) -> None:
        """Apply feedback recommendations to the session"""
        try:
            recommendations = feedback_result.get("recommendations", [])
            
            for rec in recommendations:
                action_type = rec.get("action_type")
                
                if action_type == "adjust_time":
                    # Apply time adjustments to future tasks
                    self._apply_time_adjustments(rec, session)
                
                elif action_type == "split_chunk":
                    # Flag for planning agent to split chunks
                    logger.info(f"Flagging chunk for splitting: {rec.get('reasoning', '')}")
                
                elif action_type == "merge_chunks":
                    # Flag for planning agent to merge chunks
                    logger.info(f"Flagging chunks for merging: {rec.get('reasoning', '')}")
                
                elif action_type == "reschedule":
                    # Flag for orchestrator to reschedule
                    logger.info(f"Flagging for rescheduling: {rec.get('reasoning', '')}")
            
        except Exception as e:
            logger.error(f"Error applying recommendations: {e}")
    
    def _apply_time_adjustments(self, recommendation: Dict[str, Any], session: UserSession) -> None:
        """Apply time adjustments to future tasks"""
        try:
            adjustment = recommendation.get("time_adjustment", 0)
            target_chunk_id = recommendation.get("target_chunk_id")
            
            if target_chunk_id:
                # Apply to specific chunk
                for task in session.tasks:
                    for subtask in task.subtasks:
                        if str(subtask.id) == target_chunk_id and subtask.time_estimate:
                            new_estimate = max(5, subtask.time_estimate + adjustment)
                            subtask.time_estimate = new_estimate
                            logger.info(f"Adjusted time for chunk {target_chunk_id}: {new_estimate} min")
                            return
            
            # Apply to all pending tasks if no specific target
            for task in session.tasks:
                if task.status.value in ["pending", "in_progress"] and task.time_estimate:
                    new_estimate = max(5, task.time_estimate + adjustment)
                    task.time_estimate = new_estimate
                    logger.info(f"Adjusted time for task {task.heading}: {new_estimate} min")
            
        except Exception as e:
            logger.error(f"Error applying time adjustments: {e}")
    
    def _update_session_from_action(self, action: Dict[str, Any], session: UserSession) -> None:
        """Update session based on the action"""
        try:
            action_type = action.get("action")
            
            if action_type == "mark_done":
                target_task = action.get("target_task")
                if target_task:
                    # Find and mark task as done
                    for task in session.tasks:
                        if (str(task.id) == target_task or 
                            task.heading.lower() in target_task.lower() or 
                            target_task == "last_task"):
                            
                            # Mark task and all subtasks as done
                            task.status.value = "done"
                            task.updated_at = datetime.utcnow()
                            
                            for subtask in task.subtasks:
                                subtask.status.value = "done"
                                subtask.updated_at = datetime.utcnow()
                            
                            # Record completion with feedback data
                            actual_time = action.get("actual_time", task.time_estimate or 30)
                            difficulty = action.get("difficulty", 5)
                            productivity = action.get("productivity", 7)
                            
                            session.mark_task_done(
                                task_id=str(task.id),
                                actual_time=actual_time,
                                difficulty=difficulty,
                                energy_level=action.get("energy_level", 7),
                                productivity=productivity,
                                notes=action.get("notes")
                            )
                            
                            logger.info(f"Marked task as done: {task.heading}")
                            break
            
            elif action_type == "add":
                # Create new task
                from models.task_model import Task, TaskStatus
                from uuid import uuid4
                
                new_task = Task(
                    id=uuid4(),
                    heading=action["heading"],
                    details=action["details"],
                    deadline=datetime.fromisoformat(action["deadline"]) if action.get("deadline") else None,
                    status=TaskStatus.PENDING
                )
                
                session.add_task(new_task)
                logger.info(f"Added new task: {new_task.heading}")
            
            elif action_type == "edit":
                target_task = action.get("target_task")
                if target_task:
                    for task in session.tasks:
                        if (str(task.id) == target_task or 
                            task.heading.lower() in target_task.lower() or 
                            target_task == "last_task"):
                            
                            if "heading" in action:
                                task.heading = action["heading"]
                            if "details" in action:
                                task.details = action["details"]
                            if "deadline" in action and action["deadline"]:
                                task.deadline = datetime.fromisoformat(action["deadline"])
                            
                            task.updated_at = datetime.utcnow()
                            logger.info(f"Updated task: {task.heading}")
                            break
            
            elif action_type == "add_subtask":
                target_task = action.get("target_task")
                subtask_data = action.get("subtask", {})
                
                if target_task and subtask_data:
                    for task in session.tasks:
                        if (str(task.id) == target_task or 
                            task.heading.lower() in target_task.lower() or 
                            target_task == "last_task"):
                            
                            from models.task_model import Task, TaskStatus
                            from uuid import uuid4
                            
                            new_subtask = Task(
                                id=uuid4(),
                                heading=subtask_data["heading"],
                                details=subtask_data["details"],
                                deadline=datetime.fromisoformat(subtask_data["deadline"]) if subtask_data.get("deadline") else None,
                                status=TaskStatus.PENDING
                            )
                            
                            task.subtasks.append(new_subtask)
                            task.updated_at = datetime.utcnow()
                            logger.info(f"Added subtask to {task.heading}: {new_subtask.heading}")
                            break
            
        except Exception as e:
            logger.error(f"Error updating session from action: {e}")
    
    def _generate_next_action(self, session: UserSession) -> Optional[Dict[str, Any]]:
        """Generate next action recommendation using GenieOrchestrator"""
        try:
            # Convert session to JSON format expected by orchestrator
            all_tasks_json = json.dumps({
                "tasks": [task.to_dict() for task in session.tasks]
            }, indent=2)
            
            # Create user schedule from preferences
            user_schedule_json = json.dumps({
                "daily_schedule": [
                    {
                        "start_time": "09:00",
                        "end_time": "17:00",
                        "day_of_week": "daily",
                        "energy_level": "high",
                        "focus_type": "deep_work"
                    }
                ],
                "preferences": {
                    "preferred_work_duration": session.preferences.preferred_work_duration,
                    "max_work_duration": session.preferences.max_work_duration,
                    "break_duration": session.preferences.break_duration,
                    "energy_peak_hours": session.preferences.energy_peak_hours,
                    "avoid_work_hours": session.preferences.avoid_work_hours,
                    "timezone": session.preferences.timezone
                }
            }, indent=2)
            
            # Get next action from orchestrator
            next_action = self.orchestrator.get_next_action(all_tasks_json, user_schedule_json)
            
            logger.info(f"Generated next action: {next_action.get('chunk_heading', 'Unknown')}")
            return next_action
            
        except GenieOrchestratorError as e:
            logger.error(f"Orchestrator error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating next action: {e}")
            return None
    
    def _compile_response(self, results: List[Dict[str, Any]], next_action: Optional[Dict[str, Any]], session: UserSession) -> ProcessingResult:
        """Compile final response from all processing results"""
        try:
            # Collect all motivational messages
            motivational_messages = []
            errors = []
            recommendations = []
            
            for result in results:
                feedback_result = result.get("feedback_result", {})
                if feedback_result.get("success"):
                    motivational_messages.append(feedback_result.get("motivational_message", ""))
                    recommendations.extend(feedback_result.get("recommendations", []))
                else:
                    errors.append(feedback_result.get("error", "Unknown error"))
            
            # Combine motivational messages
            if motivational_messages:
                motivational_message = " ".join(motivational_messages)
            else:
                motivational_message = "Great work! Keep moving forward."
            
            # Create user message
            if next_action:
                user_message = f"Next up: {next_action.get('chunk_heading', 'Continue with your tasks')}"
                if next_action.get('estimated_time_minutes'):
                    user_message += f" (estimated {next_action['estimated_time_minutes']} minutes)"
            else:
                user_message = "All caught up! Take a break or add new tasks."
            
            # Calculate confidence score
            confidence_scores = [r.get("feedback_result", {}).get("confidence_score", 0.0) for r in results]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            return ProcessingResult(
                success=len(errors) == 0,
                user_message=user_message,
                motivational_message=motivational_message,
                next_action=next_action,
                recommendations=recommendations,
                errors=errors,
                confidence_score=avg_confidence
            )
            
        except Exception as e:
            logger.error(f"Error compiling response: {e}")
            return ProcessingResult(
                success=False,
                user_message="I processed your feedback but encountered an issue.",
                motivational_message="Let's keep going!",
                errors=[str(e)]
            )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for debugging"""
        return {
            "agent_type": "SupervisorAgent",
            "task_extractor_info": self.task_extractor.get_agent_info(),
            "feedback_agent_info": self.feedback_agent.get_agent_info(),
            "orchestrator_info": self.orchestrator.get_agent_info(),
            "planning_agent_info": self.planning_agent.get_agent_info(),
            "session_manager_available": bool(self.session_manager)
        }

