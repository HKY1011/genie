#!/usr/bin/env python3
"""
Enhanced JsonStore for Genie - Comprehensive Persistent State Management

This module provides a robust, extensible storage solution for all Genie state:
- Tasks and subtasks with full metadata
- User sessions and preferences  
- Feedback and learning data
- Energy patterns and productivity analytics
- Multi-user support with session isolation
- Ready for future scaling to cloud/DB solutions

Data Structure:
{
  "users": {
    "user_id_1": {
      "session": {...},
      "tasks": {...},
      "feedback": {...},
      "analytics": {...}
    }
  },
  "system": {
    "version": "1.0",
    "last_backup": "...",
    "settings": {...}
  }
}
"""

import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
import logging

from models.task_model import Task, TaskStatus
from models.user_session import UserSession, SessionManager, UserPreferences, CompletionHistory, EnergyPattern

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JsonStoreError(Exception):
    """Custom exception for JsonStore operations"""
    pass


class JsonStore:
    """
    Enhanced JSON-based storage for comprehensive Genie state management
    
    Features:
    - Single file storage (progress.json) for all data
    - Multi-user support with session isolation
    - Automatic backup and recovery
    - Type-safe operations with validation
    - Extensible for future cloud/DB migration
    - Comprehensive error handling and logging
    """
    
    def __init__(self, storage_path: str = "progress.json", backup_dir: str = "backups"):
        """
        Initialize the enhanced JSON store
        
        Args:
            storage_path: Path to the main progress.json file
            backup_dir: Directory for automatic backups
        """
        self.storage_path = Path(storage_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data structure
        self._data = {
            "users": {},
            "system": {
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_backup": None,
                "settings": {
                    "auto_backup": True,
                    "backup_retention_days": 30,
                    "compression_enabled": False
                }
            }
        }
        
        # Load existing data or create new file
        self._load_state()
        logger.info(f"JsonStore initialized at {self.storage_path}")
    
    def _load_state(self) -> None:
        """Load state from JSON file with error handling"""
        if not self.storage_path.exists():
            logger.info(f"Creating new progress file at {self.storage_path}")
            self._save_state()
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
            # Validate and migrate data structure if needed
            self._data = self._validate_and_migrate_data(data)
            logger.info(f"Loaded state from {self.storage_path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON file: {e}")
            self._create_backup("corrupted")
            raise JsonStoreError(f"Corrupted progress file: {e}")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            raise JsonStoreError(f"Failed to load state: {e}")
    
    def _validate_and_migrate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data structure and migrate if needed"""
        # Ensure basic structure exists
        if "users" not in data:
            data["users"] = {}
        
        if "system" not in data:
            data["system"] = {
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_backup": None,
                "settings": {
                    "auto_backup": True,
                    "backup_retention_days": 30,
                    "compression_enabled": False
                }
            }
        
        # Migrate old task-only format if needed
        if "tasks" in data and "users" not in data:
            logger.info("Migrating old task-only format to new user-based format")
            data = self._migrate_old_format(data)
        
        return data
    
    def _migrate_old_format(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old task-only format to new user-based format"""
        new_data = {
            "users": {
                "default_user": {
                    "session": {
                        "user_id": "default_user",
                        "created_at": datetime.utcnow().isoformat(),
                        "last_updated": datetime.utcnow().isoformat(),
                        "preferences": UserPreferences().__dict__,
                        "completion_history": [],
                        "energy_patterns": [],
                        "current_focus_task": None,
                        "session_start_time": datetime.utcnow().isoformat(),
                        "total_focus_time": 0,
                        "tasks_completed_today": 0,
                        "total_focus_time_today": 0,
                        "streak_days": 0
                    },
                    "tasks": old_data.get("tasks", {}),
                    "feedback": [],
                    "analytics": {
                        "total_sessions": 1,
                        "last_session": datetime.utcnow().isoformat()
                    }
                }
            },
            "system": {
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_backup": None,
                "settings": {
                    "auto_backup": True,
                    "backup_retention_days": 30,
                    "compression_enabled": False
                }
            }
        }
        return new_data
    
    def _save_state(self) -> None:
        """Save state to JSON file with backup"""
        try:
            # Update system metadata
            self._data["system"]["last_updated"] = datetime.utcnow().isoformat()
            
            # Create backup before saving
            if self._data["system"]["settings"]["auto_backup"]:
                self._create_backup("auto")
            
            # Save to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"State saved to {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            raise JsonStoreError(f"Failed to save state: {e}")
    
    def _create_backup(self, reason: str = "manual") -> None:
        """Create a backup of the current state"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"progress_backup_{reason}_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            
            self._data["system"]["last_backup"] = backup_file.name
            logger.info(f"Backup created: {backup_file}")
            
            # Clean old backups
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    def _cleanup_old_backups(self) -> None:
        """Clean up old backup files"""
        try:
            retention_days = self._data["system"]["settings"]["backup_retention_days"]
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            for backup_file in self.backup_dir.glob("progress_backup_*.json"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.debug(f"Deleted old backup: {backup_file}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
    
    # ==================== USER SESSION MANAGEMENT ====================
    
    def get_or_create_user_session(self, user_id: str) -> UserSession:
        """
        Get existing user session or create new one
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            UserSession object
        """
        if user_id not in self._data["users"]:
            self._data["users"][user_id] = {
                "session": self._create_default_session(user_id),
                "tasks": {},
                "feedback": [],
                "analytics": {
                    "total_sessions": 1,
                    "last_session": datetime.utcnow().isoformat()
                }
            }
            self._save_state()
            logger.info(f"Created new session for user: {user_id}")
        
        session_data = self._data["users"][user_id]["session"]
        return UserSession.from_dict(session_data)
    
    def _create_default_session(self, user_id: str) -> Dict[str, Any]:
        """Create default session data for new user"""
        return {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "tasks": [],
            "preferences": UserPreferences().__dict__,
            "completion_history": [],
            "energy_patterns": [],
            "current_focus_task": None,
            "session_start_time": datetime.utcnow().isoformat(),
            "total_focus_time": 0,
            "tasks_completed_today": 0,
            "total_focus_time_today": 0,
            "streak_days": 0
        }
    
    def save_user_session(self, session: UserSession) -> bool:
        """
        Save user session to storage
        
        Args:
            session: UserSession object to save
            
        Returns:
            True if saved successfully
        """
        try:
            user_id = session.user_id
            self._data["users"][user_id]["session"] = session.to_dict()
            self._data["users"][user_id]["analytics"]["last_session"] = datetime.utcnow().isoformat()
            self._save_state()
            logger.debug(f"Session saved for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def delete_user_session(self, user_id: str) -> bool:
        """
        Delete user session and all associated data
        
        Args:
            user_id: User identifier to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if user_id in self._data["users"]:
                del self._data["users"][user_id]
                self._save_state()
                logger.info(f"Deleted session for user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    # ==================== TASK MANAGEMENT ====================
    
    def add_task(self, user_id: str, task: Task) -> str:
        """
        Add a task to user's task list
        
        Args:
            user_id: User identifier
            task: Task object to add
            
        Returns:
            Task ID as string
        """
        try:
            if user_id not in self._data["users"]:
                self.get_or_create_user_session(user_id)
            
            task_id = str(task.id)
            self._data["users"][user_id]["tasks"][task_id] = task.to_dict()
            
            # Also add to session tasks list
            session = self.get_or_create_user_session(user_id)
            session.add_task(task)
            self.save_user_session(session)
            
            self._save_state()
            logger.debug(f"Task added for user {user_id}: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            raise JsonStoreError(f"Failed to add task: {e}")
    
    def get_task(self, user_id: str, task_id: str) -> Optional[Task]:
        """
        Get a task by ID for specific user
        
        Args:
            user_id: User identifier
            task_id: Task ID as string
            
        Returns:
            Task object or None if not found
        """
        try:
            if user_id not in self._data["users"]:
                return None
            
            task_data = self._data["users"][user_id]["tasks"].get(task_id)
            if task_data:
                return Task.from_dict(task_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return None
    
    def update_task(self, user_id: str, task_id: str, **kwargs) -> bool:
        """
        Update a task by ID for specific user
        
        Args:
            user_id: User identifier
            task_id: Task ID as string
            **kwargs: Fields to update
            
        Returns:
            True if task was updated, False if not found
        """
        try:
            task = self.get_task(user_id, task_id)
            if not task:
                return False
            
            task.update(**kwargs)
            self._data["users"][user_id]["tasks"][task_id] = task.to_dict()
            
            # Update session task as well
            session = self.get_or_create_user_session(user_id)
            session_tasks = [t for t in session.tasks if str(t.id) != task_id]
            session_tasks.append(task)
            session.tasks = session_tasks
            self.save_user_session(session)
            
            self._save_state()
            logger.debug(f"Task updated for user {user_id}: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
        return False
    
    def delete_task(self, user_id: str, task_id: str) -> bool:
        """
        Delete a task by ID for specific user
        
        Args:
            user_id: User identifier
            task_id: Task ID as string
            
        Returns:
            True if task was deleted, False if not found
        """
        try:
            if user_id not in self._data["users"]:
                return False
            
            if task_id in self._data["users"][user_id]["tasks"]:
                del self._data["users"][user_id]["tasks"][task_id]
                
                # Remove from session as well
                session = self.get_or_create_user_session(user_id)
                session.remove_task(task_id)
                self.save_user_session(session)
                
                self._save_state()
                logger.debug(f"Task deleted for user {user_id}: {task_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
    
    def list_tasks(self, user_id: str) -> List[Task]:
        """
        Get all tasks for specific user
        
        Args:
            user_id: User identifier
        
        Returns:
            List of all tasks for the user
        """
        try:
            if user_id not in self._data["users"]:
                return []
            
            tasks = []
            for task_data in self._data["users"][user_id]["tasks"].values():
                tasks.append(Task.from_dict(task_data))
            return tasks
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return []
    
    def list_tasks_by_status(self, user_id: str, status: TaskStatus) -> List[Task]:
        """
        Get tasks filtered by status for specific user
        
        Args:
            user_id: User identifier
            status: TaskStatus enum value
            
        Returns:
            List of tasks with the specified status
        """
        return [task for task in self.list_tasks(user_id) if task.status == status]
    
    def search_tasks(self, user_id: str, query: str) -> List[Task]:
        """
        Search tasks by heading or details for specific user
        
        Args:
            user_id: User identifier
            query: Search query string
            
        Returns:
            List of tasks matching the search query
        """
        query_lower = query.lower()
        matching_tasks = []
        
        for task in self.list_tasks(user_id):
            if (query_lower in task.heading.lower() or 
                query_lower in task.details.lower()):
                matching_tasks.append(task)
        
        return matching_tasks
    
    # ==================== FEEDBACK AND ANALYTICS ====================
    
    def add_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> bool:
        """
        Add feedback data for user
        
        Args:
            user_id: User identifier
            feedback_data: Feedback data dictionary
        
        Returns:
            True if added successfully
        """
        try:
            if user_id not in self._data["users"]:
                self.get_or_create_user_session(user_id)
            
            feedback_data["timestamp"] = datetime.utcnow().isoformat()
            self._data["users"][user_id]["feedback"].append(feedback_data)
            self._save_state()
            logger.debug(f"Feedback added for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return False
    
    def get_feedback(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get feedback data for user
        
        Args:
            user_id: User identifier
            limit: Maximum number of feedback entries to return
            
        Returns:
            List of feedback data
        """
        try:
            if user_id not in self._data["users"]:
                return []
            
            feedback = self._data["users"][user_id]["feedback"]
            if limit:
                feedback = feedback[-limit:]
            return feedback
            
        except Exception as e:
            logger.error(f"Error getting feedback: {e}")
            return []
    
    def get_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with analytics data
        """
        try:
            session = self.get_or_create_user_session(user_id)
            tasks = self.list_tasks(user_id)
            
            analytics = {
                "user_id": user_id,
                "total_tasks": len(tasks),
                "pending_tasks": len([t for t in tasks if t.status == TaskStatus.PENDING]),
                "completed_tasks": len([t for t in tasks if t.status == TaskStatus.DONE]),
                "productivity_stats": session.get_productivity_stats(),
                "energy_patterns_today": len(session.get_energy_patterns_today()),
                "session_info": {
                    "created_at": session.created_at.isoformat(),
                    "last_updated": session.last_updated.isoformat(),
                    "total_focus_time": session.total_focus_time,
                    "streak_days": session.streak_days
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}
    
    # ==================== SYSTEM MANAGEMENT ====================
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get comprehensive storage information
        
        Returns:
            Dictionary with storage information
        """
        try:
            total_users = len(self._data["users"])
            total_tasks = sum(len(user_data["tasks"]) for user_data in self._data["users"].values())
            
            return {
                "storage_path": str(self.storage_path),
                "backup_dir": str(self.backup_dir),
                "file_size": self.storage_path.stat().st_size if self.storage_path.exists() else 0,
                "total_users": total_users,
                "total_tasks": total_tasks,
                "system_version": self._data["system"]["version"],
                "last_backup": self._data["system"]["last_backup"],
                "created_at": self._data["system"]["created_at"],
                "last_updated": self._data["system"].get("last_updated")
            }
            
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
            return {}
    
    def create_backup(self, reason: str = "manual") -> str:
        """
        Create a manual backup
        
        Args:
            reason: Reason for backup
            
        Returns:
            Backup filename
        """
        self._create_backup(reason)
        return self._data["system"]["last_backup"]
    
    def restore_from_backup(self, backup_filename: str) -> bool:
        """
        Restore state from backup file
        
        Args:
            backup_filename: Name of backup file to restore from
            
        Returns:
            True if restored successfully
        """
        try:
            backup_path = self.backup_dir / backup_filename
            if not backup_path.exists():
                raise JsonStoreError(f"Backup file not found: {backup_filename}")
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup data
            self._data = self._validate_and_migrate_data(backup_data)
            self._save_state()
            
            logger.info(f"Restored from backup: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            raise JsonStoreError(f"Failed to restore from backup: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List of backup information
        """
        try:
            backups = []
            for backup_file in self.backup_dir.glob("progress_backup_*.json"):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "reason": backup_file.name.split("_")[2] if "_" in backup_file.name else "unknown"
                })
            
            return sorted(backups, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def clear_all_data(self, user_id: Optional[str] = None) -> bool:
        """
        Clear all data for user or entire system
        
        Args:
            user_id: User to clear (None for all users)
            
        Returns:
            True if cleared successfully
        """
        try:
            if user_id:
                if user_id in self._data["users"]:
                    del self._data["users"][user_id]
                    logger.info(f"Cleared data for user: {user_id}")
            else:
                self._data["users"] = {}
                logger.info("Cleared all user data")
            
            self._save_state()
            return True
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return False
    
    def export_user_data(self, user_id: str, export_path: str) -> bool:
        """
        Export user data to separate file
        
        Args:
            user_id: User identifier
            export_path: Path to export file
            
        Returns:
            True if exported successfully
        """
        try:
            if user_id not in self._data["users"]:
                raise JsonStoreError(f"User not found: {user_id}")
            
            export_data = {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "data": self._data["users"][user_id]
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported user data to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return False
    
    def import_user_data(self, import_path: str) -> bool:
        """
        Import user data from file
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if imported successfully
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            user_id = import_data["user_id"]
            user_data = import_data["data"]
            
            self._data["users"][user_id] = user_data
            self._save_state()
            
            logger.info(f"Imported user data for: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing user data: {e}")
            return False


# ==================== LEGACY COMPATIBILITY ====================

class LegacyJsonStore(JsonStore):
    """
    Legacy JsonStore for backward compatibility
    Maps old task-only methods to new user-based methods
    """
    
    def __init__(self, storage_dir: str = "data"):
        """Initialize with default user for legacy compatibility"""
        super().__init__(storage_path=f"{storage_dir}/progress.json")
        self.default_user = "default_user"
    
    def add_task(self, task: Task) -> str:
        """Legacy method - adds task to default user"""
        return super().add_task(self.default_user, task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Legacy method - gets task from default user"""
        return super().get_task(self.default_user, task_id)
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Legacy method - updates task for default user"""
        return super().update_task(self.default_user, task_id, **kwargs)
    
    def delete_task(self, task_id: str) -> bool:
        """Legacy method - deletes task for default user"""
        return super().delete_task(self.default_user, task_id)
    
    def list_tasks(self) -> List[Task]:
        """Legacy method - lists tasks for default user"""
        return super().list_tasks(self.default_user)
    
    def list_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Legacy method - lists tasks by status for default user"""
        return [task for task in self.list_tasks() if task.status == status]
    
    def search_tasks(self, query: str) -> List[Task]:
        """Legacy method - searches tasks for default user"""
        query_lower = query.lower()
        matching_tasks = []
        
        for task in self.list_tasks():
            if (query_lower in task.heading.lower() or 
                query_lower in task.details.lower()):
                matching_tasks.append(task)
        
        return matching_tasks
    
    def get_task_count(self) -> int:
        """Legacy method - gets task count for default user"""
        return len(super().list_tasks(self.default_user))
    
    def clear_all_tasks(self):
        """Legacy method - clears all tasks for default user"""
        super().clear_all_data(self.default_user)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Legacy method - gets storage info"""
        info = super().get_storage_info()
        info["storage_dir"] = str(self.storage_path.parent)
        info["tasks_file"] = str(self.storage_path)
        return info 