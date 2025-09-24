#!/usr/bin/env python3
"""
GenieOrchestrator Agent
Manages the user's entire task ecosystem and recommends the best next actionable mini-task.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from integrations.gemini_api import GeminiAPIClient, GeminiAPIError

# Load environment variables
load_dotenv()


class GenieOrchestratorError(Exception):
    """Custom exception for GenieOrchestrator errors"""
    pass


class GenieOrchestrator:
    """
    GenieOrchestrator manages task prioritization and scheduling.
    
    Analyzes all user tasks, their subtasks, and user availability to recommend
    the single best next actionable mini-task chunk to work on.
    """
    
    def __init__(self, api_key: Optional[str] = None, prompt_file: Optional[str] = None):
        """
        Initialize GenieOrchestrator
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
            prompt_file: Path to prompt file (defaults to prompts/genieorchestrator.prompt)
        """
        self.prompt_file = prompt_file or "prompts/genieorchestrator.prompt"
        self.prompt_template = self._load_prompt_template()
        
        try:
            self.gemini_client = GeminiAPIClient(api_key=api_key)
        except ValueError as e:
            raise GenieOrchestratorError(f"Failed to initialize Gemini API client: {e}")
    
    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from file
        
        Returns:
            Prompt template as string
            
        Raises:
            GenieOrchestratorError: If prompt file cannot be loaded
        """
        try:
            prompt_path = Path(self.prompt_file)
            if not prompt_path.exists():
                raise GenieOrchestratorError(f"Prompt file not found: {self.prompt_file}")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
                
        except Exception as e:
            raise GenieOrchestratorError(f"Failed to load prompt template: {e}")
    
    def _validate_input_json(self, json_str: str, name: str) -> None:
        """
        Validate that input JSON string is valid
        
        Args:
            json_str: JSON string to validate
            name: Name of the JSON input for error messages
            
        Raises:
            GenieOrchestratorError: If JSON is invalid
        """
        if not json_str or not json_str.strip():
            raise GenieOrchestratorError(f"{name} cannot be empty")
        
        try:
            json.loads(json_str)
        except json.JSONDecodeError as e:
            raise GenieOrchestratorError(f"Invalid JSON in {name}: {e}")
    
    def _validate_orchestrator_response(self, response: Dict[str, Any]) -> None:
        """
        Validate the orchestrator response structure
        
        Args:
            response: Response dictionary to validate
            
        Raises:
            GenieOrchestratorError: If response structure is invalid
        """
        required_fields = [
            'next_chunk_id', 'task_id', 'chunk_heading', 'chunk_details',
            'resource', 'estimated_time_minutes', 'scheduled_time_start',
            'scheduled_time_end', 'progress_summary', 'priority_score',
            'warnings'
        ]
        
        for field in required_fields:
            if field not in response:
                raise GenieOrchestratorError(f"Missing required field in response: {field}")
        
        # Validate resource structure
        if 'resource' in response:
            resource = response['resource']
            resource_fields = ['title', 'url', 'type', 'focus_section', 'paid']
            
            for field in resource_fields:
                if field not in resource:
                    raise GenieOrchestratorError(f"Missing required resource field: {field}")
            
            # Validate boolean fields
            if not isinstance(resource['paid'], bool):
                raise GenieOrchestratorError("resource.paid must be a boolean")
        
        # Validate progress_summary structure
        if 'progress_summary' in response:
            progress = response['progress_summary']
            progress_fields = ['completed_chunks', 'total_chunks']
            
            for field in progress_fields:
                if field not in progress:
                    raise GenieOrchestratorError(f"Missing required progress_summary field: {field}")
            
            # Validate numeric fields
            if not isinstance(progress['completed_chunks'], int):
                raise GenieOrchestratorError("progress_summary.completed_chunks must be an integer")
            
            if not isinstance(progress['total_chunks'], int):
                raise GenieOrchestratorError("progress_summary.total_chunks must be an integer")
        
        # Validate numeric fields
        if not isinstance(response['estimated_time_minutes'], int):
            raise GenieOrchestratorError("estimated_time_minutes must be an integer")
        
        if not isinstance(response['priority_score'], (int, float)):
            raise GenieOrchestratorError("priority_score must be a number")
        
        # Validate time estimate range
        if response['estimated_time_minutes'] < 15 or response['estimated_time_minutes'] > 180:
            raise GenieOrchestratorError("estimated_time_minutes should be between 15 and 180 minutes")
        
        # Validate priority score range
        if response['priority_score'] < 0 or response['priority_score'] > 10:
            raise GenieOrchestratorError("priority_score should be between 0 and 10")
        
        # Validate datetime formats
        try:
            datetime.fromisoformat(response['scheduled_time_start'].replace('Z', '+00:00'))
            datetime.fromisoformat(response['scheduled_time_end'].replace('Z', '+00:00'))
        except ValueError:
            raise GenieOrchestratorError("scheduled_time_start and scheduled_time_end must be valid ISO 8601 format")
    
    def _format_prompt(self, all_tasks_json: str, user_schedule_json: str) -> str:
        """
        Format the prompt with task and schedule data
        
        Args:
            all_tasks_json: JSON string containing all tasks and subtasks
            user_schedule_json: JSON string containing user availability and preferences
            
        Returns:
            Formatted prompt string
        """
        # Replace placeholders in the prompt template
        formatted_prompt = self.prompt_template.replace(
            '<all_tasks_json>', all_tasks_json
        ).replace(
            '<user_schedule_json>', user_schedule_json
        )
        
        return formatted_prompt
    
    def get_next_action(self, all_tasks_json: str, user_schedule_json: str) -> Dict[str, Any]:
        """
        Get the next best actionable mini-task chunk
        
        Args:
            all_tasks_json: JSON string containing all tasks and their subtasks with structure:
                - List of tasks, each with:
                  - id: Unique task identifier
                  - heading: Task title
                  - details: Task description
                  - deadline: ISO 8601 deadline (optional)
                  - priority_score: Numeric priority (0-10)
                  - subtasks: List of chunks with:
                    - id: Unique chunk identifier
                    - heading: Chunk title
                    - details: Chunk instructions
                    - estimated_time_minutes: Time estimate
                    - status: "done" or "pending"
                    - resource: Resource information
                    - dependencies: List of chunk IDs this depends on
                    - user_feedback: User feedback about difficulty/time
            
            user_schedule_json: JSON string containing user availability with structure:
                - daily_schedule: List of time blocks with:
                  - start_time: "HH:MM" format
                  - end_time: "HH:MM" format
                  - day_of_week: Day name or "daily"
                  - energy_level: "high", "medium", "low"
                  - focus_type: "deep_work", "light_work", "break"
                - preferences: User preferences
                - timezone: User timezone
                
        Returns:
            Dictionary containing the next chunk with structure:
                - next_chunk_id: ID of the recommended chunk
                - task_id: ID of the parent task
                - chunk_heading: Chunk title
                - chunk_details: Detailed instructions
                - resource: Resource information
                - estimated_time_minutes: Time estimate
                - scheduled_time_start: ISO 8601 start time
                - scheduled_time_end: ISO 8601 end time
                - deadline: Parent task deadline
                - progress_summary: Progress information
                - priority_score: Calculated priority score
                - warnings: Any warnings or conflicts
                
        Raises:
            GenieOrchestratorError: If task processing fails
        """
        try:
            # Validate input JSON
            self._validate_input_json(all_tasks_json, "all_tasks_json")
            self._validate_input_json(user_schedule_json, "user_schedule_json")
            
            # Format prompt
            prompt = self._format_prompt(all_tasks_json, user_schedule_json)
            
            # Call Gemini API
            response_text = self.gemini_client.generate_content(prompt)
            
            # Parse JSON response
            try:
                # Try to extract JSON from markdown code blocks if present
                json_str = response_text.strip()
                
                # Look for JSON blocks marked with ```json
                if "```json" in json_str:
                    start = json_str.find("```json") + 7
                    end = json_str.find("```", start)
                    if end == -1:
                        end = len(json_str)
                    json_str = json_str[start:end].strip()
                elif "```" in json_str:
                    # Extract JSON from generic code block
                    start = json_str.find("```") + 3
                    end = json_str.find("```", start)
                    if end == -1:
                        end = len(json_str)
                    json_str = json_str[start:end].strip()
                
                response_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise GenieOrchestratorError(f"Failed to parse API response as JSON: {e}\nResponse: {response_text[:200]}...")
            
            # Validate response structure
            self._validate_orchestrator_response(response_data)
            
            return response_data
            
        except GeminiAPIError as e:
            raise GenieOrchestratorError(f"API error: {e}")
        except Exception as e:
            raise GenieOrchestratorError(f"Unexpected error: {e}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for debugging
        
        Returns:
            Dictionary with agent information
        """
        return {
            "agent_type": "GenieOrchestrator",
            "prompt_template_loaded": bool(self.prompt_template),
            "prompt_file": self.prompt_file,
            "gemini_client_info": self.gemini_client.get_client_info()
        } 