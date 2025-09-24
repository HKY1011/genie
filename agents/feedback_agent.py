#!/usr/bin/env python3
"""
Enhanced Feedback Agent for Genie
Processes user feedback and provides adaptive recommendations for task management.
Enhanced to properly trigger next subtask generation and manage feedback loops.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from integrations.gemini_api import GeminiAPIClient, GeminiAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FeedbackRecommendation:
    """Structured recommendation from feedback processing"""
    action_type: str  # "adjust_time", "split_chunk", "merge_chunks", "reschedule", "update_resources", "next_subtask"
    target_chunk_id: Optional[str] = None
    time_adjustment: Optional[int] = None  # minutes
    difficulty_adjustment: Optional[int] = None  # 1-10 scale
    motivational_message: str = ""
    confidence_score: float = 0.0  # 0.0-1.0
    reasoning: str = ""
    requires_planning_agent: bool = False
    requires_orchestrator: bool = False
    next_subtask_data: Optional[Dict[str, Any]] = None


@dataclass
class FeedbackContext:
    """Context for feedback processing"""
    user_id: str
    task_id: str
    feedback_type: str  # "completion", "difficulty", "time", "priority", "deadline", "multi_intent"
    chunk_id: Optional[str] = None
    feedback_data: Dict[str, Any] = field(default_factory=dict)
    user_history: List[Dict[str, Any]] = field(default_factory=list)
    current_state: Dict[str, Any] = field(default_factory=dict)


class FeedbackAgentError(Exception):
    """Custom exception for FeedbackAgent errors"""
    pass


class FeedbackAgent:
    """
    Enhanced Feedback Agent that processes user feedback and provides adaptive recommendations.
    
    Handles:
    - Time estimation adjustments based on completion patterns
    - Chunk difficulty assessment and resizing recommendations
    - Motivational messaging based on user patterns
    - Multi-intent feedback processing
    - Learning from user behavior patterns
    - Proper next subtask generation after feedback
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FeedbackAgent
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
        """
        try:
            self.gemini_client = GeminiAPIClient(api_key=api_key)
        except ValueError as e:
            raise FeedbackAgentError(f"Failed to initialize Gemini API client: {e}")
        
        # Load motivational templates
        self.motivational_templates = self._load_motivational_templates()
        
        # Feedback processing rules
        self.feedback_rules = self._initialize_feedback_rules()
    
    def _load_motivational_templates(self) -> Dict[str, List[str]]:
        """Load motivational message templates"""
        return {
            "completion": [
                "🎉 Excellent work! You're making great progress on this task.",
                "✅ Well done! Every completed chunk brings you closer to your goal.",
                "🚀 Fantastic! You're building momentum and staying on track.",
                "💪 Great job! Your consistency is paying off.",
                "🌟 Outstanding! You're demonstrating real progress and focus."
            ],
            "difficulty_overcome": [
                "🔥 You conquered a challenging task! That's real growth.",
                "💎 You turned a difficult situation into a learning opportunity.",
                "🏆 Impressive! You handled that complexity with skill.",
                "🎯 You navigated through the difficulty with determination.",
                "⭐ You showed resilience and problem-solving skills!"
            ],
            "time_optimization": [
                "⚡ You're getting more efficient! Your time management is improving.",
                "🎯 Great time optimization! You're learning to work smarter.",
                "💡 Excellent efficiency! You're finding better ways to work.",
                "🚀 Impressive speed! You're mastering this skill quickly.",
                "⚡ Outstanding time management! You're becoming more productive."
            ],
            "encouragement": [
                "💪 Keep going! You're doing great work.",
                "🌟 You've got this! Every step forward counts.",
                "🎯 Stay focused! You're making real progress.",
                "🔥 You're on fire! Keep that momentum going.",
                "⭐ You're doing amazing! Trust the process."
            ]
        }
    
    def _initialize_feedback_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize feedback processing rules"""
        return {
            "completion": {
                "triggers_next_subtask": True,
                "time_adjustment_factor": 0.9,  # Slightly reduce time estimates
                "difficulty_adjustment": 0,
                "motivational_type": "completion"
            },
            "difficulty": {
                "triggers_next_subtask": True,
                "time_adjustment_factor": 1.2,  # Increase time estimates
                "difficulty_adjustment": 1,
                "motivational_type": "difficulty_overcome"
            },
            "easy": {
                "triggers_next_subtask": True,
                "time_adjustment_factor": 0.8,  # Reduce time estimates
                "difficulty_adjustment": -1,
                "motivational_type": "time_optimization"
            },
            "time": {
                "triggers_next_subtask": False,
                "time_adjustment_factor": 1.0,
                "difficulty_adjustment": 0,
                "motivational_type": "encouragement"
            }
        }
    
    def process_feedback(self, feedback_json: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback and generate recommendations
        
        Args:
            feedback_json: Feedback data from user
            current_state: Current system state
            
        Returns:
            Dictionary with processed feedback results
            
        Raises:
            FeedbackAgentError: If processing fails
        """
        try:
            # Create feedback context
            context = self._create_feedback_context(feedback_json, current_state)
            
            # Determine feedback type
            feedback_type = self._determine_feedback_type(feedback_json)
            
            # Process based on feedback type
            if feedback_type == "completion":
                recommendations = self._process_completion_feedback(context)
            elif feedback_type == "difficulty":
                recommendations = self._process_difficulty_feedback(context)
            elif feedback_type == "easy":
                recommendations = self._process_easy_feedback(context)
            elif feedback_type == "time":
                recommendations = self._process_time_feedback(context)
            else:
                recommendations = self._process_generic_feedback(context)
            
            # Generate motivational message
            motivational_message = self._generate_motivational_message(context, recommendations)
            
            # Determine next actions
            next_actions = self._determine_next_actions(recommendations)
            
            # Calculate overall confidence
            confidence = self._calculate_overall_confidence(recommendations)
            
            # Check if we need to trigger next subtask generation
            should_trigger_next_subtask = any(
                rec.action_type == "next_subtask" for rec in recommendations
            )
            
            result = {
                "success": True,
                "feedback_type": feedback_type,
                "recommendations": [rec.__dict__ for rec in recommendations],
                "motivational_message": motivational_message,
                "next_actions": next_actions,
                "confidence_score": confidence,
                "should_trigger_next_subtask": should_trigger_next_subtask,
                "next_subtask_data": None
            }
            
            # If we should trigger next subtask, generate it
            if should_trigger_next_subtask:
                next_subtask = self._generate_next_subtask(context)
                if next_subtask:
                    result["next_subtask_data"] = next_subtask
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            raise FeedbackAgentError(f"Failed to process feedback: {e}")
    
    def _create_feedback_context(self, feedback_json: Dict[str, Any], current_state: Dict[str, Any]) -> FeedbackContext:
        """Create feedback context from input data"""
        return FeedbackContext(
            user_id=current_state.get("user_id", "default_user"),
            task_id=feedback_json.get("task_id", ""),
            feedback_type=feedback_json.get("feedback_type", "completion"),
            chunk_id=feedback_json.get("chunk_id"),
            feedback_data=feedback_json,
            user_history=current_state.get("completion_history", []),
            current_state=current_state
        )
    
    def _determine_feedback_type(self, feedback_json: Dict[str, Any]) -> str:
        """Determine the type of feedback based on input"""
        feedback_type = feedback_json.get("feedback_type", "").lower()
        
        if feedback_type in ["completion", "done", "complete"]:
            return "completion"
        elif feedback_type in ["difficulty", "difficult", "hard"]:
            return "difficulty"
        elif feedback_type in ["easy", "simple", "quick"]:
            return "easy"
        elif feedback_type in ["time", "duration"]:
            return "time"
        else:
            return "completion"  # Default to completion
    
    def _process_completion_feedback(self, context: FeedbackContext) -> List[FeedbackRecommendation]:
        """Process completion feedback"""
        recommendations = []
        
        # Add completion recommendation
        recommendations.append(FeedbackRecommendation(
            action_type="next_subtask",
            target_chunk_id=context.chunk_id,
            motivational_message="Task completed successfully!",
            confidence_score=0.9,
            reasoning="User marked task as completed, should proceed to next subtask",
            requires_planning_agent=True
        ))
        
        # Add time adjustment if needed
        if context.feedback_data.get("time_taken_minutes"):
            actual_time = context.feedback_data["time_taken_minutes"]
            estimated_time = context.feedback_data.get("estimated_time_minutes", 30)
            
            if actual_time < estimated_time * 0.8:
                # Completed faster than estimated
                recommendations.append(FeedbackRecommendation(
                    action_type="adjust_time",
                    time_adjustment=-int(estimated_time * 0.1),
                    confidence_score=0.7,
                    reasoning=f"Completed in {actual_time} minutes vs estimated {estimated_time} minutes"
                ))
            elif actual_time > estimated_time * 1.2:
                # Took longer than estimated
                recommendations.append(FeedbackRecommendation(
                    action_type="adjust_time",
                    time_adjustment=int(estimated_time * 0.2),
                    confidence_score=0.7,
                    reasoning=f"Took {actual_time} minutes vs estimated {estimated_time} minutes"
                ))
        
        return recommendations
    
    def _process_difficulty_feedback(self, context: FeedbackContext) -> List[FeedbackRecommendation]:
        """Process difficulty feedback"""
        recommendations = []
        
        # Add difficulty adjustment recommendation
        recommendations.append(FeedbackRecommendation(
            action_type="adjust_difficulty",
            difficulty_adjustment=1,
            confidence_score=0.8,
            reasoning="User found task difficult, should adjust difficulty for future tasks"
        ))
        
        # Add next subtask recommendation
        recommendations.append(FeedbackRecommendation(
            action_type="next_subtask",
            target_chunk_id=context.chunk_id,
            motivational_message="You overcame a challenging task!",
            confidence_score=0.9,
            reasoning="User completed difficult task, should proceed to next subtask",
            requires_planning_agent=True
        ))
        
        return recommendations
    
    def _process_easy_feedback(self, context: FeedbackContext) -> List[FeedbackRecommendation]:
        """Process easy feedback"""
        recommendations = []
        
        # Add difficulty adjustment recommendation
        recommendations.append(FeedbackRecommendation(
            action_type="adjust_difficulty",
            difficulty_adjustment=-1,
            confidence_score=0.8,
            reasoning="User found task easy, should increase difficulty for future tasks"
        ))
        
        # Add next subtask recommendation
        recommendations.append(FeedbackRecommendation(
            action_type="next_subtask",
            target_chunk_id=context.chunk_id,
            motivational_message="Great efficiency!",
            confidence_score=0.9,
            reasoning="User completed easy task, should proceed to next subtask",
            requires_planning_agent=True
        ))
        
        return recommendations
    
    def _process_time_feedback(self, context: FeedbackContext) -> List[FeedbackRecommendation]:
        """Process time-related feedback"""
        recommendations = []
        
        # Add time adjustment recommendation
        recommendations.append(FeedbackRecommendation(
            action_type="adjust_time",
            time_adjustment=0,
            confidence_score=0.6,
            reasoning="Time feedback received, may need time adjustments"
        ))
        
        return recommendations
    
    def _process_generic_feedback(self, context: FeedbackContext) -> List[FeedbackRecommendation]:
        """Process generic feedback"""
        recommendations = []
        
        # Add generic next subtask recommendation
        recommendations.append(FeedbackRecommendation(
            action_type="next_subtask",
            target_chunk_id=context.chunk_id,
            motivational_message="Feedback received!",
            confidence_score=0.7,
            reasoning="Generic feedback received, proceed to next subtask",
            requires_planning_agent=True
        ))
        
        return recommendations
    
    def _generate_motivational_message(self, context: FeedbackContext, recommendations: List[FeedbackRecommendation]) -> str:
        """Generate motivational message based on feedback and recommendations"""
        import random
        
        # Determine motivational type
        motivational_type = "encouragement"  # Default
        
        for rec in recommendations:
            if rec.action_type == "next_subtask":
                if "difficult" in context.feedback_type:
                    motivational_type = "difficulty_overcome"
                elif "easy" in context.feedback_type:
                    motivational_type = "time_optimization"
                elif "completion" in context.feedback_type:
                    motivational_type = "completion"
                break
        
        # Get motivational templates
        templates = self.motivational_templates.get(motivational_type, self.motivational_templates["encouragement"])
        
        # Select random template
        base_message = random.choice(templates)
        
        # Add personalization
        personalized_message = self._add_personalization(context, base_message)
        
        return personalized_message
    
    def _add_personalization(self, context: FeedbackContext, base_message: str) -> str:
        """Add personalization to motivational message"""
        # Add user-specific elements if available
        if context.user_id and context.user_id != "default_user":
            base_message = f"Hey there! {base_message}"
        
        # Add task-specific elements
        if context.task_id:
            base_message += f" You're making great progress on your tasks!"
        
        return base_message
    
    def _determine_next_actions(self, recommendations: List[FeedbackRecommendation]) -> List[str]:
        """Determine next actions based on recommendations"""
        actions = []
        
        for rec in recommendations:
            if rec.action_type == "next_subtask":
                actions.append("Generate next subtask")
            elif rec.action_type == "adjust_time":
                actions.append("Adjust time estimates")
            elif rec.action_type == "adjust_difficulty":
                actions.append("Adjust difficulty level")
            elif rec.action_type == "update_resources":
                actions.append("Update learning resources")
        
        return actions
    
    def _calculate_overall_confidence(self, recommendations: List[FeedbackRecommendation]) -> float:
        """Calculate overall confidence score"""
        if not recommendations:
            return 0.0
        
        total_confidence = sum(rec.confidence_score for rec in recommendations)
        return total_confidence / len(recommendations)
    
    def _generate_next_subtask(self, context: FeedbackContext) -> Optional[Dict[str, Any]]:
        """
        Generate next subtask after feedback processing
        
        Args:
            context: Feedback context
            
        Returns:
            Next subtask data or None
        """
        try:
            # Import planning agent to generate next subtask
            from agents.planning_agent import PlanningAgent
            
            planning_agent = PlanningAgent()
            
            # Create task context for next subtask generation
            task_context = {
                "heading": f"Continue task {context.task_id}",
                "details": f"Continue working on the task based on feedback: {context.feedback_type}",
                "previous_chunks": [context.chunk_id] if context.chunk_id else [],
                "corrections_or_feedback": context.feedback_data.get("feedback_text", ""),
                "task_id": context.task_id
            }
            
            # Generate next subtask
            next_subtask = planning_agent.get_next_chunk(task_context)
            
            if next_subtask:
                return {
                    "chunk_heading": next_subtask["chunk_heading"],
                    "chunk_details": next_subtask["chunk_details"],
                    "estimated_time_minutes": next_subtask["estimated_time_minutes"],
                    "resource": next_subtask.get("resource", {}),
                    "chunk_order": next_subtask.get("chunk_order", 1),
                    "subtask_id": next_subtask.get("subtask_id", f"subtask_{context.task_id}_{next_subtask.get('chunk_order', 1)}"),
                    "status": "pending"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating next subtask: {e}")
            return None
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for debugging
        
        Returns:
            Dictionary with agent information
        """
        return {
            "agent_type": "EnhancedFeedbackAgent",
            "gemini_client_info": self.gemini_client.get_client_info(),
            "motivational_templates_count": len(self.motivational_templates),
            "feedback_rules_count": len(self.feedback_rules)
        }


def test_feedback_agent():
    """
    Test function demonstrating the enhanced FeedbackAgent capabilities
    """
    print("🧪 Testing Enhanced FeedbackAgent")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Initialize the agent
        agent = FeedbackAgent()
        print("✅ FeedbackAgent initialized successfully")
        
        # Test cases
        test_feedbacks = [
            {
                "feedback_json": {
                    "task_id": "test_task_1",
                    "chunk_id": "chunk_1",
                    "feedback_type": "completion",
                    "feedback_text": "Completed successfully",
                    "rating": 5,
                    "time_taken_minutes": 25
                },
                "current_state": {
                    "user_id": "test_user",
                    "current_focus_task": "test_task_1",
                    "completion_history": []
                }
            },
            {
                "feedback_json": {
                    "task_id": "test_task_2",
                    "chunk_id": "chunk_2",
                    "feedback_type": "difficult",
                    "feedback_text": "This was harder than expected",
                    "rating": 3,
                    "time_taken_minutes": 45
                },
                "current_state": {
                    "user_id": "test_user",
                    "current_focus_task": "test_task_2",
                    "completion_history": []
                }
            },
            {
                "feedback_json": {
                    "task_id": "test_task_3",
                    "chunk_id": "chunk_3",
                    "feedback_type": "easy",
                    "feedback_text": "This was easier than expected",
                    "rating": 4,
                    "time_taken_minutes": 20
                },
                "current_state": {
                    "user_id": "test_user",
                    "current_focus_task": "test_task_3",
                    "completion_history": []
                }
            }
        ]
        
        for i, test_case in enumerate(test_feedbacks, 1):
            print(f"\n🔍 Testing Feedback {i}: {test_case['feedback_json']['feedback_type']}")
            try:
                result = agent.process_feedback(
                    test_case['feedback_json'],
                    test_case['current_state']
                )
                
                print(f"  ✅ Feedback processed successfully")
                print(f"  📝 Feedback type: {result['feedback_type']}")
                print(f"  💬 Motivational message: {result['motivational_message'][:50]}...")
                print(f"  🎯 Should trigger next subtask: {result['should_trigger_next_subtask']}")
                print(f"  📊 Confidence score: {result['confidence_score']:.2f}")
                
                if result.get('next_subtask_data'):
                    print(f"  ➡️  Next subtask: {result['next_subtask_data']['chunk_heading']}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_feedback_agent() 