#!/usr/bin/env python3
"""
Task Extraction Agent for Genie
Extracts and validates task actions from natural language user input.
Enhanced with better deadline extraction and validation.
"""

import sys
import json
import logging
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the project root to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.gemini_api import GeminiAPIClient, GeminiAPIError
from models.task_model import Task, TaskStatus

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskExtractionError(Exception):
    """Custom exception for TaskExtractionAgent errors"""
    pass


class TaskExtractionAgent:
    """
    Enhanced Task Extraction Agent that processes natural language user input.
    
    Handles rich, flexible multi-intent user inputs including:
    - Creating new main tasks and subtasks
    - Editing existing tasks and subtasks
    - Marking tasks or subtasks as done
    - Rescheduling tasks or subtasks
    - Adding subtasks to existing tasks or subtasks
    - Handling multiple actions in one user input
    - Enhanced deadline extraction from natural language
    """
    
    def __init__(self, api_key: Optional[str] = None, prompt_file: Optional[str] = None):
        """
        Initialize TaskExtractionAgent
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
            prompt_file: Path to prompt file (defaults to prompts/extract_task.prompt)
        """
        self.prompt_file = prompt_file or "prompts/extract_task.prompt"
        self.prompt_template = self._load_prompt_template()
        
        try:
            self.gemini_client = GeminiAPIClient(api_key=api_key)
        except ValueError as e:
            raise TaskExtractionError(f"Failed to initialize Gemini API client: {e}")
    
    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from file
        
        Returns:
            Prompt template as string
            
        Raises:
            TaskExtractionError: If prompt file cannot be loaded
        """
        try:
            prompt_path = Path(self.prompt_file)
            if not prompt_path.exists():
                raise TaskExtractionError(f"Prompt file not found: {self.prompt_file}")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
                
        except Exception as e:
            raise TaskExtractionError(f"Failed to load prompt template: {e}")
    
    def _convert_tasks_to_json(self, tasks: List[Task]) -> str:
        """
        Convert list of Task objects to JSON string for context
        
        Args:
            tasks: List of Task objects
            
        Returns:
            JSON string representation of tasks
        """
        try:
            # Convert tasks to dictionary format with full subtask structure
            tasks_data = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "heading": task.heading,
                    "details": task.details,
                    "status": task.status.value,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "time_estimate": task.time_estimate,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "subtasks": []
                }
                
                # Add subtasks if they exist
                if hasattr(task, 'subtasks') and task.subtasks:
                    for subtask in task.subtasks:
                        subtask_dict = {
                            "id": str(subtask.id),
                            "heading": subtask.heading,
                            "details": subtask.details,
                            "status": subtask.status.value,
                            "deadline": subtask.deadline.isoformat() if subtask.deadline else None,
                            "time_estimate": subtask.time_estimate,
                            "created_at": subtask.created_at.isoformat(),
                            "updated_at": subtask.updated_at.isoformat()
                        }
                        task_dict["subtasks"].append(subtask_dict)
                
                tasks_data.append(task_dict)
            
            return json.dumps(tasks_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error converting tasks to JSON: {e}")
            return "[]"
    
    def _format_prompt(self, user_input: str, existing_tasks: List[Task]) -> str:
        """
        Format the prompt with user input and existing tasks
        
        Args:
            user_input: Natural language user input
            existing_tasks: List of existing Task objects
            
        Returns:
            Formatted prompt string
        """
        existing_tasks_json = self._convert_tasks_to_json(existing_tasks)
        
        # Enhanced prompt with better deadline extraction guidance
        enhanced_prompt = self.prompt_template + f"""

**IMPORTANT DEADLINE EXTRACTION GUIDELINES:**

1. **Natural Language Deadline Detection:**
   - "by tomorrow" → tomorrow's date
   - "by next week" → next Monday
   - "by end of month" → last day of current month
   - "in 3 days" → current date + 3 days
   - "by Friday" → next Friday
   - "by 5pm today" → today at 5pm
   - "by next Monday" → next Monday
   - "within a week" → current date + 7 days
   - "by the end of this week" → this Friday
   - "ASAP" → current date + 1 day
   - "urgent" → current date + 1 day

2. **Date Format:**
   - Always return dates in ISO 8601 format: YYYY-MM-DDTHH:MM:SS
   - For dates without time, use: YYYY-MM-DDT00:00:00
   - For relative dates, calculate the actual date based on current date

3. **Validation:**
   - If deadline is unclear or ambiguous, set to null
   - If multiple deadlines mentioned, use the most specific one
   - If deadline is in the past, set to null

**User Input:**
\"\"\"{user_input}\"\"\"

**Existing Tasks JSON:**
{existing_tasks_json}
"""
        return enhanced_prompt
    
    def _validate_action(self, action: Dict[str, Any]) -> None:
        """
        Validate action structure and content
        
        Args:
            action: Action dictionary to validate
            
        Raises:
            TaskExtractionError: If action is invalid
        """
        if not isinstance(action, dict):
            raise TaskExtractionError("Action must be a dictionary")
        
        if 'action' not in action:
            raise TaskExtractionError("Action must have 'action' field")
        
        action_type = action['action']
        
        # Validate based on action type
        if action_type == 'add':
            required_fields = ['heading']
            for field in required_fields:
                if field not in action or not action[field]:
                    raise TaskExtractionError(f"Add action missing required field: {field}")
            
            # Validate deadline format if present
            if 'deadline' in action and action['deadline']:
                self._validate_deadline_format(action['deadline'])
        
        elif action_type == 'edit':
            required_fields = ['target_task']
            for field in required_fields:
                if field not in action:
                    raise TaskExtractionError(f"Edit action missing required field: {field}")
            
            # Validate deadline format if present
            if 'deadline' in action and action['deadline']:
                self._validate_deadline_format(action['deadline'])
        
        elif action_type == 'mark_done':
            if 'target_task' not in action:
                raise TaskExtractionError("Mark done action missing target_task field")
        
        elif action_type == 'reschedule':
            required_fields = ['target_task', 'deadline']
            for field in required_fields:
                if field not in action:
                    raise TaskExtractionError(f"Reschedule action missing required field: {field}")
            
            self._validate_deadline_format(action['deadline'])
        
        elif action_type == 'add_subtask':
            required_fields = ['target_task', 'subtask']
            for field in required_fields:
                if field not in action:
                    raise TaskExtractionError(f"Add subtask action missing required field: {field}")
            
            if not isinstance(action['subtask'], dict):
                raise TaskExtractionError("Subtask must be a dictionary")
            
            if 'heading' not in action['subtask']:
                raise TaskExtractionError("Subtask missing heading field")
            
            # Validate subtask deadline if present
            if 'deadline' in action['subtask'] and action['subtask']['deadline']:
                self._validate_deadline_format(action['subtask']['deadline'])
        
        else:
            raise TaskExtractionError(f"Unknown action type: {action_type}")
    
    def _validate_deadline_format(self, deadline: str) -> None:
        """
        Validate deadline format
        
        Args:
            deadline: Deadline string to validate
            
        Raises:
            TaskExtractionError: If deadline format is invalid
        """
        try:
            # Try to parse as ISO 8601
            datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        except ValueError:
            raise TaskExtractionError(f"Invalid deadline format: {deadline}. Must be ISO 8601 format.")
    
    def _parse_api_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse API response and extract actions
        
        Args:
            response_text: Raw API response text
            
        Returns:
            List of action dictionaries
            
        Raises:
            TaskExtractionError: If parsing fails
        """
        try:
            # Clean the response text
            cleaned_response = response_text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in cleaned_response:
                start = cleaned_response.find("```json") + 7
                end = cleaned_response.find("```", start)
                if end == -1:
                    end = len(cleaned_response)
                cleaned_response = cleaned_response[start:end].strip()
            elif "```" in cleaned_response:
                start = cleaned_response.find("```") + 3
                end = cleaned_response.find("```", start)
                if end == -1:
                    end = len(cleaned_response)
                cleaned_response = cleaned_response[start:end].strip()
            
            # Parse JSON
            actions = json.loads(cleaned_response)
            
            # Ensure it's a list
            if not isinstance(actions, list):
                actions = [actions]
            
            # Validate each action
            for action in actions:
                self._validate_action(action)
            
            return actions
            
        except json.JSONDecodeError as e:
            raise TaskExtractionError(f"Failed to parse API response as JSON: {e}\nResponse: {response_text[:200]}...")
        except Exception as e:
            raise TaskExtractionError(f"Unexpected error parsing response: {e}")
    
    def extract_task(self, user_input: str, existing_tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Extract task actions from natural language user input
        
        Args:
            user_input: Natural language user input
            existing_tasks: List of existing Task objects for context
            
        Returns:
            List of action dictionaries describing user intents
            
        Raises:
            TaskExtractionError: If extraction fails
        """
        try:
            if not user_input or not user_input.strip():
                raise TaskExtractionError("User input cannot be empty")
            
            logger.info(f"Processing user input: {user_input[:100]}...")
            
            # Format the prompt with enhanced deadline extraction guidance
            prompt = self._format_prompt(user_input, existing_tasks)
            
            # Call Gemini API
            logger.info("Calling Gemini API for task extraction...")
            response_text = self.gemini_client.generate_content(prompt)
            
            # Parse the response
            logger.info("Parsing API response...")
            actions = self._parse_api_response(response_text)
            
            # Post-process actions to enhance deadline extraction
            for action in actions:
                if 'deadline' in action and action['deadline']:
                    action['deadline'] = self._enhance_deadline_extraction(action['deadline'], user_input)
                
                if action.get('action') == 'add_subtask' and 'subtask' in action:
                    if 'deadline' in action['subtask'] and action['subtask']['deadline']:
                        action['subtask']['deadline'] = self._enhance_deadline_extraction(action['subtask']['deadline'], user_input)
            
            logger.info(f"Successfully extracted {len(actions)} actions")
            return actions
            
        except GeminiAPIError as e:
            raise TaskExtractionError(f"API error: {e}")
        except Exception as e:
            raise TaskExtractionError(f"Unexpected error: {e}")
    
    def _enhance_deadline_extraction(self, deadline: str, user_input: str) -> str:
        """
        Enhance deadline extraction with additional natural language processing
        
        Args:
            deadline: Current deadline string
            user_input: Original user input for context
            
        Returns:
            Enhanced deadline string
        """
        try:
            # If deadline is already a valid ISO format, return as is
            datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            return deadline
        except ValueError:
            # Try to extract deadline from user input using regex patterns
            patterns = [
                r'by\s+(tomorrow|next\s+week|end\s+of\s+month|friday|monday|tuesday|wednesday|thursday|saturday|sunday)',
                r'in\s+(\d+)\s+days?',
                r'within\s+(\d+)\s+days?',
                r'by\s+(\d{1,2}):(\d{2})\s*(am|pm)?\s*(today|tomorrow)?',
                r'asap|urgent',
                r'by\s+the\s+end\s+of\s+(this\s+week|next\s+week|the\s+month)'
            ]
            
            user_input_lower = user_input.lower()
            current_date = datetime.now()
            
            for pattern in patterns:
                match = re.search(pattern, user_input_lower)
                if match:
                    if 'tomorrow' in match.group():
                        return (current_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
                    elif 'next week' in match.group():
                        # Next Monday
                        days_ahead = 7 - current_date.weekday()
                        if days_ahead <= 0:
                            days_ahead += 7
                        return (current_date + timedelta(days=days_ahead)).strftime('%Y-%m-%dT00:00:00')
                    elif 'end of month' in match.group():
                        # Last day of current month
                        if current_date.month == 12:
                            last_day = datetime(current_date.year + 1, 1, 1) - timedelta(days=1)
                        else:
                            last_day = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
                        return last_day.strftime('%Y-%m-%dT00:00:00')
                    elif 'asap' in match.group() or 'urgent' in match.group():
                        return (current_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
                    elif 'in' in match.group() and 'days' in match.group():
                        days = int(match.group(1))
                        return (current_date + timedelta(days=days)).strftime('%Y-%m-%dT00:00:00')
                    elif 'within' in match.group() and 'days' in match.group():
                        days = int(match.group(1))
                        return (current_date + timedelta(days=days)).strftime('%Y-%m-%dT00:00:00')
            
            # If no pattern matches, return null
            return None
            
        except Exception as e:
            logger.warning(f"Error enhancing deadline extraction: {e}")
            return None
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for debugging
        
        Returns:
            Dictionary with agent information
        """
        return {
            "agent_type": "EnhancedTaskExtractionAgent",
            "prompt_template_loaded": bool(self.prompt_template),
            "prompt_file": self.prompt_file,
            "gemini_client_info": self.gemini_client.get_client_info()
        }


def test_task_extraction_agent():
    """
    Test function demonstrating the upgraded TaskExtractionAgent capabilities
    """
    print("🧪 Testing Enhanced TaskExtractionAgent")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize the agent
        agent = TaskExtractionAgent()
        print("✅ TaskExtractionAgent initialized successfully")
        
        # Test cases with deadline extraction
        test_cases = [
            "Learn Python programming by next week",
            "Build a React app by tomorrow",
            "Complete the project by end of month",
            "Study for exam in 3 days",
            "Submit report ASAP",
            "Create presentation by Friday",
            "Finish documentation within a week"
        ]
        
        for test_input in test_cases:
            print(f"\n🔍 Testing: '{test_input}'")
            try:
                actions = agent.extract_task(test_input, existing_tasks=[])
                for action in actions:
                    print(f"  ✅ Action: {action['action']}")
                    print(f"  📝 Heading: {action.get('heading', 'N/A')}")
                    print(f"  📅 Deadline: {action.get('deadline', 'None')}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_task_extraction_agent()
