#!/usr/bin/env python3
"""
User Session Model for Genie
Manages persistent user state, preferences, and learning data.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from uuid import uuid4, UUID

from models.task_model import Task, TaskStatus


@dataclass
class UserPreferences:
    """User preferences and settings"""
    preferred_work_duration: int = 45  # minutes
    max_work_duration: int = 90  # minutes
    break_duration: int = 15  # minutes
    energy_peak_hours: List[str] = field(default_factory=lambda: ["09:00-11:00", "14:00-16:00"])
    avoid_work_hours: List[str] = field(default_factory=list)
    timezone: str = "UTC"
    notification_preferences: Dict[str, bool] = field(default_factory=lambda: {
        "task_reminders": True,
        "break_reminders": True,
        "deadline_warnings": True,
        "completion_celebrations": True
    })


@dataclass
class CompletionHistory:
    """Historical data about task completions"""
    task_id: str
    estimated_time: int  # minutes
    actual_time: int  # minutes
    difficulty_rating: int  # 1-10
    energy_level: int  # 1-10
    productivity_rating: int  # 1-10
    completed_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "task_id": self.task_id,
            "estimated_time": self.estimated_time,
            "actual_time": self.actual_time,
            "difficulty_rating": self.difficulty_rating,
            "energy_level": self.energy_level,
            "productivity_rating": self.productivity_rating,
            "completed_at": self.completed_at.isoformat(),
            "notes": self.notes
        }


@dataclass
class EnergyPattern:
    """User's energy level patterns"""
    timestamp: datetime
    energy_level: int  # 1-10
    activity_type: str  # "work", "break", "meeting", etc.
    productivity_score: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "energy_level": self.energy_level,
            "activity_type": self.activity_type,
            "productivity_score": self.productivity_score,
            "context": self.context
        }


@dataclass
class UserSession:
    """Complete user session with persistent state"""
    
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Core data
    tasks: List[Task] = field(default_factory=list)
    preferences: UserPreferences = field(default_factory=UserPreferences)
    
    # Learning data
    completion_history: List[CompletionHistory] = field(default_factory=list)
    energy_patterns: List[EnergyPattern] = field(default_factory=list)
    
    # Session state
    current_focus_task: Optional[str] = None
    session_start_time: Optional[datetime] = None
    total_focus_time: int = 0  # minutes
    
    # Analytics
    tasks_completed_today: int = 0
    total_focus_time_today: int = 0
    streak_days: int = 0
    
    def __post_init__(self):
        """Initialize session state"""
        if not self.session_start_time:
            self.session_start_time = datetime.utcnow()
    
    def add_task(self, task: Task) -> None:
        """Add a task to the session"""
        self.tasks.append(task)
        self.last_updated = datetime.utcnow()
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID"""
        for i, task in enumerate(self.tasks):
            if str(task.id) == task_id:
                del self.tasks[i]
                self.last_updated = datetime.utcnow()
                return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if str(task.id) == task_id:
                return task
        return None
    
    def mark_task_done(self, task_id: str, actual_time: int, difficulty: int, 
                      energy_level: int, productivity: int, notes: Optional[str] = None) -> bool:
        """Mark a task as done and record completion data"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        # Update task status
        task.status = TaskStatus.DONE
        task.updated_at = datetime.utcnow()
        
        # Record completion history
        history = CompletionHistory(
            task_id=task_id,
            estimated_time=task.time_estimate or 0,
            actual_time=actual_time,
            difficulty_rating=difficulty,
            energy_level=energy_level,
            productivity_rating=productivity,
            notes=notes
        )
        self.completion_history.append(history)
        
        # Update analytics
        self.tasks_completed_today += 1
        self.total_focus_time_today += actual_time
        
        self.last_updated = datetime.utcnow()
        return True
    
    def record_energy_pattern(self, energy_level: int, activity_type: str, 
                            productivity_score: float, context: Optional[Dict[str, Any]] = None) -> None:
        """Record energy level pattern"""
        pattern = EnergyPattern(
            timestamp=datetime.utcnow(),
            energy_level=energy_level,
            activity_type=activity_type,
            productivity_score=productivity_score,
            context=context or {}
        )
        self.energy_patterns.append(pattern)
        self.last_updated = datetime.utcnow()
    
    def update_preferences(self, **kwargs) -> None:
        """Update user preferences"""
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        self.last_updated = datetime.utcnow()
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        return [task for task in self.tasks if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
    
    def get_completed_tasks_today(self) -> List[Task]:
        """Get tasks completed today"""
        today = datetime.utcnow().date()
        return [
            task for task in self.tasks 
            if task.status == TaskStatus.DONE and task.updated_at.date() == today
        ]
    
    def get_productivity_stats(self) -> Dict[str, Any]:
        """Get productivity statistics"""
        if not self.completion_history:
            return {
                "total_tasks_completed": 0,
                "average_completion_time": 0,
                "average_difficulty": 0,
                "average_productivity": 0,
                "completion_rate": 0
            }
        
        total_tasks = len(self.completion_history)
        avg_time = sum(h.actual_time for h in self.completion_history) / total_tasks
        avg_difficulty = sum(h.difficulty_rating for h in self.completion_history) / total_tasks
        avg_productivity = sum(h.productivity_rating for h in self.completion_history) / total_tasks
        
        # Calculate completion rate (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_completions = [h for h in self.completion_history if h.completed_at >= thirty_days_ago]
        completion_rate = len(recent_completions) / max(1, len([t for t in self.tasks if t.created_at >= thirty_days_ago]))
        
        return {
            "total_tasks_completed": total_tasks,
            "average_completion_time": round(avg_time, 1),
            "average_difficulty": round(avg_difficulty, 1),
            "average_productivity": round(avg_productivity, 1),
            "completion_rate": round(completion_rate * 100, 1)
        }
    
    def get_energy_patterns_today(self) -> List[EnergyPattern]:
        """Get energy patterns for today"""
        today = datetime.utcnow().date()
        return [p for p in self.energy_patterns if p.timestamp.date() == today]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization"""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "tasks": [task.to_dict() for task in self.tasks],
            "preferences": asdict(self.preferences),
            "completion_history": [h.to_dict() for h in self.completion_history],
            "energy_patterns": [p.to_dict() for p in self.energy_patterns],
            "current_focus_task": self.current_focus_task,
            "session_start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "total_focus_time": self.total_focus_time,
            "tasks_completed_today": self.tasks_completed_today,
            "total_focus_time_today": self.total_focus_time_today,
            "streak_days": self.streak_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create session from dictionary"""
        # Convert tasks
        tasks = []
        for task_data in data.get('tasks', []):
            tasks.append(Task.from_dict(task_data))
        
        # Convert completion history
        completion_history = []
        for hist_data in data.get('completion_history', []):
            history = CompletionHistory(
                task_id=hist_data['task_id'],
                estimated_time=hist_data['estimated_time'],
                actual_time=hist_data['actual_time'],
                difficulty_rating=hist_data['difficulty_rating'],
                energy_level=hist_data['energy_level'],
                productivity_rating=hist_data['productivity_rating'],
                completed_at=datetime.fromisoformat(hist_data['completed_at']),
                notes=hist_data.get('notes')
            )
            completion_history.append(history)
        
        # Convert energy patterns
        energy_patterns = []
        for pattern_data in data.get('energy_patterns', []):
            pattern = EnergyPattern(
                timestamp=datetime.fromisoformat(pattern_data['timestamp']),
                energy_level=pattern_data['energy_level'],
                activity_type=pattern_data['activity_type'],
                productivity_score=pattern_data['productivity_score'],
                context=pattern_data.get('context', {})
            )
            energy_patterns.append(pattern)
        
        # Convert preferences
        prefs_data = data.get('preferences', {})
        preferences = UserPreferences(
            preferred_work_duration=prefs_data.get('preferred_work_duration', 45),
            max_work_duration=prefs_data.get('max_work_duration', 90),
            break_duration=prefs_data.get('break_duration', 15),
            energy_peak_hours=prefs_data.get('energy_peak_hours', ["09:00-11:00", "14:00-16:00"]),
            avoid_work_hours=prefs_data.get('avoid_work_hours', []),
            timezone=prefs_data.get('timezone', 'UTC'),
            notification_preferences=prefs_data.get('notification_preferences', {})
        )
        
        return cls(
            user_id=data['user_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_updated=datetime.fromisoformat(data['last_updated']),
            tasks=tasks,
            preferences=preferences,
            completion_history=completion_history,
            energy_patterns=energy_patterns,
            current_focus_task=data.get('current_focus_task'),
            session_start_time=datetime.fromisoformat(data['session_start_time']) if data.get('session_start_time') else None,
            total_focus_time=data.get('total_focus_time', 0),
            tasks_completed_today=data.get('tasks_completed_today', 0),
            total_focus_time_today=data.get('total_focus_time_today', 0),
            streak_days=data.get('streak_days', 0)
        )


class SessionManager:
    """Manages user sessions and persistence"""
    
    def __init__(self, storage_dir: str = "storage/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: UserSession) -> bool:
        """Save user session to disk"""
        try:
            file_path = self.storage_dir / f"{session.user_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, user_id: str) -> Optional[UserSession]:
        """Load user session from disk"""
        try:
            file_path = self.storage_dir / f"{user_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return UserSession.from_dict(data)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def create_session(self, user_id: str) -> UserSession:
        """Create a new user session"""
        session = UserSession(user_id=user_id)
        self.save_session(session)
        return session
    
    def get_or_create_session(self, user_id: str) -> UserSession:
        """Get existing session or create new one"""
        session = self.load_session(user_id)
        if session is None:
            session = self.create_session(user_id)
        return session
    
    def delete_session(self, user_id: str) -> bool:
        """Delete user session"""
        try:
            file_path = self.storage_dir / f"{user_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def list_sessions(self) -> List[str]:
        """List all user IDs with sessions"""
        try:
            return [f.stem for f in self.storage_dir.glob("*.json")]
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return [] 