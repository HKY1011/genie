from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4, UUID
from enum import Enum


class TaskStatus(Enum):
    """Enumeration for task status values"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Data model for representing a task with all required fields"""
    
    heading: str
    details: str
    status: TaskStatus = TaskStatus.PENDING
    deadline: Optional[datetime] = None
    time_estimate: Optional[int] = None  # Duration in minutes
    resource_link: Optional[str] = None
    subtasks: List['Task'] = field(default_factory=list)
    metadata: Optional[dict] = field(default_factory=dict)  # For storing additional data like calendar event IDs
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Ensure updated_at is set when task is created"""
        if self.updated_at == self.created_at:
            self.updated_at = datetime.utcnow()
    
    def update(self, **kwargs):
        """Update task fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def add_subtask(self, subtask: 'Task'):
        """Add a subtask to this task"""
        self.subtasks.append(subtask)
        self.updated_at = datetime.utcnow()
    
    def remove_subtask(self, subtask_id: UUID):
        """Remove a subtask by its ID"""
        self.subtasks = [st for st in self.subtasks if st.id != subtask_id]
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'heading': self.heading,
            'details': self.details,
            'status': self.status.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'time_estimate': self.time_estimate,
            'resource_link': self.resource_link,
            'subtasks': [subtask.to_dict() for subtask in self.subtasks],
            'metadata': self.metadata or {},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary (for JSON deserialization)"""
        # Handle nested subtasks recursively
        subtasks = []
        if 'subtasks' in data and data['subtasks']:
            subtasks = [cls.from_dict(st) for st in data['subtasks']]
        
        return cls(
            id=UUID(data['id']),
            heading=data['heading'],
            details=data['details'],
            status=TaskStatus(data['status']),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            time_estimate=data.get('time_estimate'),
            resource_link=data.get('resource_link'),
            subtasks=subtasks,
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )
    
    def __str__(self) -> str:
        """String representation of the task"""
        return f"Task(id={self.id}, heading='{self.heading}', status={self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the task"""
        return f"Task(id={self.id}, heading='{self.heading}', status={self.status.value}, subtasks={len(self.subtasks)})" 