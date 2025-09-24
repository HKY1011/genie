#!/usr/bin/env python3
"""
Enhanced Planning Agent for Genie
Breaks down high-level tasks into specific, actionable chunks using Perplexity API.
Supports intelligent subtask generation, internal pool management, and context-aware planning.
Enhanced to generate multiple subtasks and manage progression properly.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dotenv import load_dotenv

from integrations.perplexity_api import PerplexityAPIClient, PerplexityAPIError

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class PlanningAgentError(Exception):
    """Custom exception for PlanningAgent errors"""
    pass


class PlanningAgent:
    """
    Enhanced Planning Agent that breaks down tasks into manageable chunks.
    
    Features:
    - Intelligent subtask generation (3-7 subtasks based on Perplexity analysis)
    - Internal subtask pool management
    - Context-aware generation (remembers completed subtasks)
    - Smart replenishment (only when needed)
    - Automatic subtask management
    - Enhanced progression tracking
    """
    
    def __init__(self, api_key: Optional[str] = None, prompt_file: Optional[str] = None):
        """
        Initialize PlanningAgent
        
        Args:
            api_key: Perplexity API key (defaults to environment variable)
            prompt_file: Path to prompt file (defaults to prompts/breakdown_chunk.prompt)
        """
        self.prompt_file = prompt_file or "prompts/breakdown_chunk.prompt"
        self.prompt_template = self._load_prompt_template()
        
        # Internal subtask pool management
        self.subtask_pools = {}  # task_id -> List[Dict] of all subtasks
        self.completed_subtasks = {}  # task_id -> List[int] of completed chunk orders
        self.visible_subtasks = {}  # task_id -> List[int] of currently visible chunk orders
        self.task_details = {}  # task_id -> Dict of original task details for context
        self.current_subtask_index = {}  # task_id -> current subtask index
        
        try:
            self.api_client = PerplexityAPIClient(api_key=api_key)
        except ValueError as e:
            raise PlanningAgentError(f"Failed to initialize API client: {e}")
    
    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from file
        
        Returns:
            Prompt template as string
            
        Raises:
            PlanningAgentError: If prompt file cannot be loaded
        """
        try:
            prompt_path = Path(self.prompt_file)
            if not prompt_path.exists():
                raise PlanningAgentError(f"Prompt file not found: {self.prompt_file}")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
                
        except Exception as e:
            raise PlanningAgentError(f"Failed to load prompt template: {e}")
    
    def _validate_task_input(self, task: Dict[str, Any]) -> None:
        """
        Validate the task input structure
        
        Args:
            task: Task dictionary to validate
            
        Raises:
            PlanningAgentError: If task structure is invalid
        """
        required_fields = ['heading', 'details']
        
        for field in required_fields:
            if field not in task:
                raise PlanningAgentError(f"Missing required field: {field}")
            
            if not task[field]:
                raise PlanningAgentError(f"Field '{field}' cannot be empty")
        
        # Validate optional fields if present
        if 'deadline' in task and task['deadline']:
            try:
                datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
            except ValueError:
                raise PlanningAgentError(f"Invalid deadline format: {task['deadline']}")
    
    def _validate_chunk_response(self, response: Dict[str, Any]) -> None:
        """
        Validate the chunk response structure
        
        Args:
            response: Response dictionary to validate
            
        Raises:
            PlanningAgentError: If response structure is invalid
        """
        required_fields = ['chunk_heading', 'chunk_details', 'estimated_time_minutes']
        
        for field in required_fields:
            if field not in response:
                raise PlanningAgentError(f"Missing required field in response: {field}")
            
            if not response[field]:
                raise PlanningAgentError(f"Field '{field}' cannot be empty")
        
        # Validate estimated_time_minutes is a number
        if not isinstance(response['estimated_time_minutes'], (int, float)):
            raise PlanningAgentError("estimated_time_minutes must be a number")
        
        if response['estimated_time_minutes'] <= 0:
            raise PlanningAgentError("estimated_time_minutes must be positive")
        
        # Log validation success for debugging
        logger.debug(f"Successfully validated subtask: {response.get('chunk_heading', 'Unknown')}")
    
    def _format_prompt(self, task: Dict[str, Any], batch_mode: bool = False) -> str:
        """
        Format the prompt for the API call
        
        Args:
            task: Task dictionary
            batch_mode: Whether to generate multiple subtasks
            
        Returns:
            Formatted prompt string
        """
        # Enhanced prompt for better subtask generation
        batch_instruction = "Generate 3-7 specific subtasks for this task. Each subtask should be:" if batch_mode else "Generate the next specific subtask for this task. The subtask should be:"
        
        batch_format = """
{
  "subtasks": [
    {
      "chunk_heading": "Specific action step",
      "chunk_details": "Detailed description of what to do",
      "estimated_time_minutes": 30,
      "resource": {
        "title": "Resource name",
        "url": "https://example.com",
        "type": "video|article|tool|practice",
        "focus_section": "Specific section to focus on",
        "paid": false
      },
      "chunk_order": 1,
      "dependencies": []
    }
  ]
}
"""
        
        single_format = """
{
  "chunk_heading": "Specific action step",
  "chunk_details": "Detailed description of what to do",
  "estimated_time_minutes": 30,
  "resource": {
    "title": "Resource name",
    "url": "https://example.com",
    "type": "video|article|tool|practice",
    "focus_section": "Specific section to focus on",
    "paid": false
  },
  "chunk_order": 1,
  "dependencies": []
}
"""
        
        output_format = batch_format if batch_mode else single_format
        
        enhanced_prompt = f"""
You are an expert task planning assistant for a personal productivity system called Genie.

Your job is to break down high-level tasks into specific, actionable subtasks that can be completed in focused time blocks.

**Task to Break Down:**
- Heading: {task['heading']}
- Details: {task['details']}
- Deadline: {task.get('deadline', 'No specific deadline')}

**Instructions:**
{batch_instruction}

1. **Specific and Actionable**: Clear, concrete steps that can be completed
2. **Time-Bounded**: Each subtask should take 15-60 minutes to complete
3. **Sequential**: Subtasks should build upon each other logically
4. **Resource-Aware**: Include relevant learning resources or tools needed
5. **Motivating**: Use encouraging, action-oriented language

**Previous Subtasks Completed:** {task.get('previous_chunks', [])}
**User Feedback:** {task.get('corrections_or_feedback', 'None')}

**Output Format (JSON):**
{output_format}

**Important Guidelines:**
- Make subtasks specific enough that someone can start immediately
- Include practical resources (tutorials, documentation, tools)
- Consider the user's skill level and available time
- Ensure logical progression between subtasks
- Use encouraging, motivating language

Output ONLY the JSON - no explanations or additional text.
"""
        return enhanced_prompt
    
    def _generate_subtask_id(self, task_id: str, chunk_order: int) -> str:
        """
        Generate a unique subtask ID
        
        Args:
            task_id: Task ID
            chunk_order: Chunk order number
            
        Returns:
            Unique subtask ID
        """
        return f"subtask_{task_id}_{chunk_order}"
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Enhanced JSON parsing with multiple fallback strategies
        
        Args:
            response_text: Raw response text from API
            
        Returns:
            Parsed JSON data
            
        Raises:
            PlanningAgentError: If all parsing strategies fail
        """
        import re
        
        # Strategy 1: Try to extract JSON from markdown code blocks
        json_str = response_text.strip()
        
        # Look for ```json blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', json_str, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Look for ``` blocks (any language)
        code_match = re.search(r'```\s*(.*?)\s*```', json_str, re.DOTALL)
        if code_match:
            json_str = code_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Try to find JSON object boundaries
        try:
            # Look for the first { and last }
            start = json_str.find('{')
            end = json_str.rfind('}')
            
            if start != -1 and end != -1 and end > start:
                json_str = json_str[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Try to fix common JSON issues
        try:
            # Remove any text before the first {
            start = json_str.find('{')
            if start != -1:
                json_str = json_str[start:]
            
            # Remove any text after the last }
            end = json_str.rfind('}')
            if end != -1:
                json_str = json_str[:end+1]
            
            # Try to fix trailing commas
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Strategy 4: Try to extract just the subtasks array if the main object is malformed
        try:
            subtasks_match = re.search(r'"subtasks"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
            if subtasks_match:
                subtasks_content = subtasks_match.group(1)
                # Try to parse individual subtask objects
                subtask_objects = re.findall(r'\{[^{}]*\}', subtasks_content)
                if subtask_objects:
                    # Create a minimal valid JSON structure
                    fixed_json = '{"subtasks": [' + ','.join(subtask_objects) + ']}'
                    return json.loads(fixed_json)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Strategy 5: Generate fallback subtasks if all parsing fails
        logger.warning(f"Failed to parse JSON response. Generating fallback subtasks. Response preview: {response_text[:200]}...")
        
        # Create fallback subtasks based on the task
        fallback_subtasks = [
            {
                "chunk_heading": "Research and gather information",
                "chunk_details": "Start by researching the topic and gathering relevant information and resources needed for the task.",
                "estimated_time_minutes": 30,
                "resource": {
                    "title": "General research resources",
                    "url": "https://example.com",
                    "type": "general",
                    "focus_section": "Research phase",
                    "paid": False
                },
                "chunk_order": 1,
                "dependencies": []
            },
            {
                "chunk_heading": "Plan and organize approach",
                "chunk_details": "Create a detailed plan and organize your approach to complete the task effectively and efficiently.",
                "estimated_time_minutes": 20,
                "resource": {
                    "title": "Planning tools",
                    "url": "https://example.com",
                    "type": "general",
                    "focus_section": "Planning phase",
                    "paid": False
                },
                "chunk_order": 2,
                "dependencies": [1]
            },
            {
                "chunk_heading": "Execute and implement",
                "chunk_details": "Execute the plan and implement the required actions to complete the task successfully.",
                "estimated_time_minutes": 45,
                "resource": {
                    "title": "Implementation resources",
                    "url": "https://example.com",
                    "type": "general",
                    "focus_section": "Implementation phase",
                    "paid": False
                },
                "chunk_order": 3,
                "dependencies": [1, 2]
            }
        ]
        
        return {"subtasks": fallback_subtasks}
    
    def generate_initial_subtasks(self, task: Dict[str, Any], task_id: str) -> List[Dict[str, Any]]:
        """
        Generate initial set of subtasks for a new task
        
        Args:
            task: Task dictionary
            task_id: Unique task ID
            
        Returns:
            List of subtask dictionaries
            
        Raises:
            PlanningAgentError: If generation fails
        """
        try:
            # Validate input
            self._validate_task_input(task)
            
            # Format prompt for batch generation
            prompt = self._format_prompt(task, batch_mode=True)
            
            # Call Perplexity API
            response_text = self.api_client.generate_content(prompt)
            
            # Debug: Log the raw response
            logger.info(f"Raw API response length: {len(response_text)}")
            logger.info(f"Raw API response preview: {response_text[:500]}...")
            
            # Parse JSON response with enhanced error handling
            response_data = self._parse_json_response(response_text)
            
            # Debug: Log the parsed response
            logger.info(f"Parsed response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
            
            # Extract subtasks
            if 'subtasks' not in response_data:
                raise PlanningAgentError("API response missing 'subtasks' field")
            
            subtasks = response_data['subtasks']
            
            # Validate and process each subtask with enhanced error handling
            processed_subtasks = []
            for i, subtask in enumerate(subtasks):
                try:
                    # Validate subtask structure
                    self._validate_chunk_response(subtask)
                    
                    # Add missing fields
                    processed_subtask = {
                        'chunk_heading': subtask['chunk_heading'],
                        'chunk_details': subtask['chunk_details'],
                        'estimated_time_minutes': subtask['estimated_time_minutes'],
                        'resource': subtask.get('resource', {
                            'title': 'General resources',
                            'url': 'https://example.com',
                            'type': 'general',
                            'focus_section': 'Complete the task',
                            'paid': False
                        }),
                        'chunk_order': i + 1,
                        'dependencies': subtask.get('dependencies', []),
                        'subtask_id': self._generate_subtask_id(task_id, i + 1),
                        'status': 'pending'
                    }
                    
                    processed_subtasks.append(processed_subtask)
                    
                except PlanningAgentError as e:
                    logger.warning(f"Invalid subtask {i+1}, using fallback: {e}")
                    # Create a fallback subtask for this position
                    fallback_subtask = {
                        'chunk_heading': f"Step {i+1}: Complete task component",
                        'chunk_details': f"Complete the {i+1}th component of the task: {task.get('heading', 'Unknown task')}",
                        'estimated_time_minutes': 30,
                        'resource': {
                            'title': 'General resources',
                            'url': 'https://example.com',
                            'type': 'general',
                            'focus_section': 'Task completion',
                            'paid': False
                        },
                        'chunk_order': i + 1,
                        'dependencies': [],
                        'subtask_id': self._generate_subtask_id(task_id, i + 1),
                        'status': 'pending'
                    }
                    processed_subtasks.append(fallback_subtask)
            
            # Store in internal pools
            self.subtask_pools[task_id] = processed_subtasks
            self.completed_subtasks[task_id] = []
            self.visible_subtasks[task_id] = [1]  # Show first subtask
            self.task_details[task_id] = task
            self.current_subtask_index[task_id] = 0
            
            return processed_subtasks
            
        except PerplexityAPIError as e:
            raise PlanningAgentError(f"API error: {e}")
        except Exception as e:
            raise PlanningAgentError(f"Unexpected error: {e}")
    
    def _generate_batch_subtasks(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a batch of subtasks (fallback method)
        
        Args:
            task: Task dictionary
            
        Returns:
            List of subtask dictionaries
        """
        # Fallback subtask generation based on task type
        task_heading = task['heading'].lower()
        
        if 'python' in task_heading or 'programming' in task_heading:
            return [
                {
                    'chunk_heading': 'Set up Python development environment',
                    'chunk_details': 'Install Python, set up IDE, and write first Hello World program',
                    'estimated_time_minutes': 30,
                    'resource': {
                        'title': 'Python Installation Guide',
                        'url': 'https://python.org/downloads',
                        'type': 'guide',
                        'focus_section': 'Installation',
                        'paid': False
                    },
                    'chunk_order': 1,
                    'dependencies': [],
                    'status': 'pending'
                },
                {
                    'chunk_heading': 'Learn Python basics and data types',
                    'chunk_details': 'Understand variables, strings, numbers, lists, and basic operations',
                    'estimated_time_minutes': 45,
                    'resource': {
                        'title': 'Python Tutorial',
                        'url': 'https://docs.python.org/3/tutorial/',
                        'type': 'tutorial',
                        'focus_section': 'Basic Types',
                        'paid': False
                    },
                    'chunk_order': 2,
                    'dependencies': [1],
                    'status': 'pending'
                },
                {
                    'chunk_heading': 'Practice with control structures',
                    'chunk_details': 'Learn if/else statements, loops, and functions',
                    'estimated_time_minutes': 60,
                    'resource': {
                        'title': 'Python Control Flow',
                        'url': 'https://docs.python.org/3/tutorial/controlflow.html',
                        'type': 'tutorial',
                        'focus_section': 'Control Flow',
                        'paid': False
                    },
                    'chunk_order': 3,
                    'dependencies': [2],
                    'status': 'pending'
                }
            ]
        elif 'react' in task_heading or 'web' in task_heading:
            return [
                {
                    'chunk_heading': 'Set up React project with authentication dependencies',
                    'chunk_details': 'Create new React app and install authentication libraries',
                    'estimated_time_minutes': 30,
                    'resource': {
                        'title': 'Create React App',
                        'url': 'https://create-react-app.dev',
                        'type': 'guide',
                        'focus_section': 'Getting Started',
                        'paid': False
                    },
                    'chunk_order': 1,
                    'dependencies': [],
                    'status': 'pending'
                },
                {
                    'chunk_heading': 'Create login and registration components',
                    'chunk_details': 'Build user interface components for authentication',
                    'estimated_time_minutes': 45,
                    'resource': {
                        'title': 'React Components Tutorial',
                        'url': 'https://react.dev/learn/components',
                        'type': 'tutorial',
                        'focus_section': 'Components',
                        'paid': False
                    },
                    'chunk_order': 2,
                    'dependencies': [1],
                    'status': 'pending'
                },
                {
                    'chunk_heading': 'Implement JWT token management',
                    'chunk_details': 'Add JWT authentication and token storage',
                    'estimated_time_minutes': 60,
                    'resource': {
                        'title': 'JWT Authentication',
                        'url': 'https://jwt.io',
                        'type': 'guide',
                        'focus_section': 'JWT Basics',
                        'paid': False
                    },
                    'chunk_order': 3,
                    'dependencies': [2],
                    'status': 'pending'
                }
            ]
        else:
            # Generic subtask generation
            return [
                {
                    'chunk_heading': f'Research and plan {task["heading"]}',
                    'chunk_details': f'Gather information and create a detailed plan for {task["heading"]}',
                    'estimated_time_minutes': 30,
                    'resource': {
                        'title': 'Research Resources',
                        'url': 'https://example.com',
                        'type': 'research',
                        'focus_section': 'Planning',
                        'paid': False
                    },
                    'chunk_order': 1,
                    'dependencies': [],
                    'status': 'pending'
                },
                {
                    'chunk_heading': f'Start implementing {task["heading"]}',
                    'chunk_details': f'Begin the actual work on {task["heading"]}',
                    'estimated_time_minutes': 45,
                    'resource': {
                        'title': 'Implementation Guide',
                        'url': 'https://example.com',
                        'type': 'guide',
                        'focus_section': 'Implementation',
                        'paid': False
                    },
                    'chunk_order': 2,
                    'dependencies': [1],
                    'status': 'pending'
                },
                {
                    'chunk_heading': f'Review and refine {task["heading"]}',
                    'chunk_details': f'Review the work done and make necessary improvements',
                    'estimated_time_minutes': 30,
                    'resource': {
                        'title': 'Review Checklist',
                        'url': 'https://example.com',
                        'type': 'checklist',
                        'focus_section': 'Review',
                        'paid': False
                    },
                    'chunk_order': 3,
                    'dependencies': [2],
                    'status': 'pending'
                }
            ]
    
    def get_visible_subtasks(self, task_id: str, max_visible: int = 5) -> List[Dict[str, Any]]:
        """
        Get currently visible subtasks for a task
        
        Args:
            task_id: Task ID
            max_visible: Maximum number of visible subtasks
            
        Returns:
            List of visible subtask dictionaries
        """
        if task_id not in self.subtask_pools:
            return []
        
        all_subtasks = self.subtask_pools[task_id]
        completed = self.completed_subtasks.get(task_id, [])
        
        # Filter out completed subtasks and get next few
        visible = []
        for subtask in all_subtasks:
            if subtask['chunk_order'] not in completed:
                visible.append(subtask)
                if len(visible) >= max_visible:
                    break
        
        return visible
    
    def mark_subtask_completed(self, task_id: str, chunk_order: int) -> Optional[Dict[str, Any]]:
        """
        Mark a subtask as completed and get the next one
        
        Args:
            task_id: Task ID
            chunk_order: Chunk order to mark as completed
            
        Returns:
            Next subtask dictionary or None if no more subtasks
        """
        if task_id not in self.subtask_pools:
            return None
        
        # Mark as completed
        if task_id not in self.completed_subtasks:
            self.completed_subtasks[task_id] = []
        
        if chunk_order not in self.completed_subtasks[task_id]:
            self.completed_subtasks[task_id].append(chunk_order)
        
        # Update current subtask index
        if task_id in self.current_subtask_index:
            self.current_subtask_index[task_id] += 1
        
        # Get next subtask
        return self._generate_next_subtask(task_id)
    
    def _generate_next_subtask(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate the next subtask for a task
        
        Args:
            task_id: Task ID
            
        Returns:
            Next subtask dictionary or None if no more subtasks
        """
        if task_id not in self.subtask_pools:
            return None
        
        all_subtasks = self.subtask_pools[task_id]
        completed = self.completed_subtasks.get(task_id, [])
        
        # Find next uncompleted subtask
        for subtask in all_subtasks:
            if subtask['chunk_order'] not in completed:
                return subtask
        
        # If no more subtasks in pool, don't generate more to avoid infinite loops
        # Just return None to indicate completion
        return None
    
    def get_next_chunk(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the next actionable chunk for a task (enhanced for multiple subtask generation)
        
        Args:
            task: Task dictionary with the following structure:
                - heading: str (required) - Task title
                - details: str (required) - Task description
                - deadline: str (optional) - ISO 8601 deadline
                - previous_chunks: List[Dict] (optional) - Completed chunks
                - available_time_blocks: List[Dict] (optional) - Available time slots
                - corrections_or_feedback: str (optional) - User feedback
                
        Returns:
            Dictionary containing the next chunk
            
        Raises:
            PlanningAgentError: If task processing fails
        """
        try:
            # Validate input
            self._validate_task_input(task)
            
            # Generate a unique task ID if not provided
            task_id = task.get('task_id', f"task_{int(datetime.now().timestamp())}")
            
            # Check if we already have subtasks for this task
            if task_id not in self.subtask_pools:
                # Generate initial subtasks
                self.generate_initial_subtasks(task, task_id)
            
            # Get the next available subtask
            next_subtask = self._generate_next_subtask(task_id)
            
            if not next_subtask:
                # If no next subtask, generate more
                try:
                    additional_subtasks = self._generate_batch_subtasks(task)
                    if additional_subtasks:
                        # Add to pool
                        all_subtasks = self.subtask_pools[task_id]
                        next_order = len(all_subtasks) + 1
                        for subtask in additional_subtasks:
                            subtask['chunk_order'] = next_order
                            subtask['subtask_id'] = self._generate_subtask_id(task_id, next_order)
                            all_subtasks.append(subtask)
                            next_order += 1
                        
                        next_subtask = additional_subtasks[0]
                    else:
                        # Fallback: create a generic continuation subtask
                        next_subtask = {
                            'chunk_heading': f"Continue with {task['heading']}",
                            'chunk_details': f"Continue working on {task['heading']} based on previous progress",
                            'resource': {
                                'title': 'Continue task execution',
                                'url': 'https://example.com',
                                'type': 'task',
                                'focus_section': 'Continue from where you left off',
                                'paid': False
                            },
                            'estimated_time_minutes': 30,
                            'chunk_order': len(self.subtask_pools.get(task_id, [])) + 1,
                            'subtask_id': self._generate_subtask_id(task_id, len(self.subtask_pools.get(task_id, [])) + 1),
                            'dependencies': [],
                            'status': 'pending'
                        }
                except Exception as e:
                    # Final fallback
                    next_subtask = {
                        'chunk_heading': f"Continue with {task['heading']}",
                        'chunk_details': f"Continue working on {task['heading']}",
                        'resource': {
                            'title': 'Continue task execution',
                            'url': 'https://example.com',
                            'type': 'task',
                            'focus_section': 'Continue from where you left off',
                            'paid': False
                        },
                        'estimated_time_minutes': 30,
                        'chunk_order': 1,
                        'subtask_id': self._generate_subtask_id(task_id, 1),
                        'dependencies': [],
                        'status': 'pending'
                    }
            
            # Validate response structure
            self._validate_chunk_response(next_subtask)
            
            return next_subtask
            
        except PerplexityAPIError as e:
            raise PlanningAgentError(f"API error: {e}")
        except Exception as e:
            raise PlanningAgentError(f"Unexpected error: {e}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for debugging
        
        Returns:
            Dictionary with agent information
        """
        return {
            "agent_type": "EnhancedPlanningAgent",
            "prompt_template_loaded": bool(self.prompt_template),
            "prompt_file": self.prompt_file,
            "api_client_info": self.api_client.get_client_info(),
            "subtask_pools_count": len(self.subtask_pools),
            "total_subtasks_managed": sum(len(pool) for pool in self.subtask_pools.values()),
            "tasks_with_subtasks": len([tid for tid, pool in self.subtask_pools.items() if len(pool) > 0]),
            "tasks_without_subtasks": len([tid for tid, pool in self.subtask_pools.items() if len(pool) == 0])
        }


def test_planning_agent():
    """
    Test function demonstrating the enhanced PlanningAgent capabilities
    """
    print("🧪 Testing Enhanced PlanningAgent")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize the agent
        agent = PlanningAgent()
        print("✅ PlanningAgent initialized successfully")
        
        # Test cases
        test_tasks = [
            {
                "heading": "Learn Python Programming",
                "details": "Master Python fundamentals to build web applications",
                "deadline": "2024-12-31T00:00:00"
            },
            {
                "heading": "Build React Todo App",
                "details": "Create a modern todo application with React hooks and authentication",
                "deadline": "2024-12-15T00:00:00"
            }
        ]
        
        for i, task in enumerate(test_tasks, 1):
            print(f"\n🔍 Testing Task {i}: {task['heading']}")
            try:
                # Test initial subtask generation
                subtasks = agent.generate_initial_subtasks(task, f"test_task_{i}")
                print(f"  ✅ Generated {len(subtasks)} initial subtasks")
                
                # Test getting next chunk
                next_chunk = agent.get_next_chunk(task)
                print(f"  ✅ Next chunk: {next_chunk['chunk_heading']}")
                print(f"  ⏱️  Estimated time: {next_chunk['estimated_time_minutes']} minutes")
                
                # Test marking subtask as completed
                if next_chunk:
                    next_subtask = agent.mark_subtask_completed(f"test_task_{i}", next_chunk['chunk_order'])
                    if next_subtask:
                        print(f"  ✅ Next subtask after completion: {next_subtask['chunk_heading']}")
                    else:
                        print(f"  ℹ️  No more subtasks after completion")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_planning_agent()
