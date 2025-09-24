# Genie Backend

A Python-based task management system with intelligent agent architecture for automated task processing and resource management.

## Project Structure

```
genie_backend/
├── __init__.py
├── README.md
├── agents/                    # Agent implementations
│   ├── __init__.py
│   ├── supervisor_agent.py
│   ├── task_extraction_agent.py
│   ├── planning_agent.py
│   ├── resource_agent.py
│   └── scheduler_agent.py
├── config/                    # Configuration files
├── integrations/              # External service integrations
│   └── __init__.py
├── models/                    # Data models
│   ├── __init__.py
│   └── task_model.py         # Task data model
├── prompts/                   # LLM prompts and templates
│   └── __init__.py
├── storage/                   # Data persistence layer
│   ├── __init__.py
│   └── json_store.py         # JSON-based task storage
├── utils/                     # Utility functions
│   └── __init__.py
├── test_storage.py           # Comprehensive test suite
└── demo_usage.py             # Usage demonstration
```

## Features

### Task Data Model

The `Task` class provides a comprehensive data model for representing tasks with the following features:

- **Unique Identification**: Each task has a UUID for unique identification
- **Rich Metadata**: Heading, details, status, deadlines, and time estimates
- **Resource Links**: URLs pointing to relevant resources
- **Hierarchical Structure**: Support for nested subtasks
- **Timestamps**: Automatic creation and update timestamps
- **Status Management**: Enum-based status tracking (pending, in_progress, done, cancelled)

### JSON Storage Layer

The `JsonStore` class provides persistent storage with the following capabilities:

- **CRUD Operations**: Create, read, update, and delete tasks
- **Querying**: Filter tasks by status, deadline, time estimate, and content
- **Search**: Full-text search across task headings and details
- **Persistence**: Automatic JSON file storage with error handling
- **Data Integrity**: Proper serialization/deserialization with validation

## Quick Start

### Installation

1. Clone the repository
2. Navigate to the project directory
3. Run the test suite to verify everything works:

```bash
python3 test_storage.py
```

### Basic Usage

```python
from models.task_model import Task, TaskStatus
from storage.json_store import JsonStore
from datetime import datetime, timedelta

# Initialize storage
store = JsonStore(storage_dir="data")

# Create a task
task = Task(
    heading="Complete project documentation",
    details="Write comprehensive documentation for the genie_backend project",
    time_estimate=120,  # 2 hours
    deadline=datetime.utcnow() + timedelta(days=7),
    resource_link="https://docs.python.org/3/"
)

# Save task to storage
task_id = store.add_task(task)

# Retrieve task
retrieved_task = store.get_task(task_id)

# Update task
store.update_task(task_id, status=TaskStatus.IN_PROGRESS)

# Query tasks
pending_tasks = store.list_tasks_by_status(TaskStatus.PENDING)
api_tasks = store.search_tasks("API")
short_tasks = store.get_tasks_by_time_estimate(max_minutes=60)
```

### Working with Subtasks

```python
# Create main task
main_task = Task(
    heading="Build web application",
    details="Create a full-stack web application",
    time_estimate=480
)

# Create and add subtasks
subtask1 = Task(
    heading="Set up project structure",
    details="Create directories and initialize git repository",
    time_estimate=30
)

subtask2 = Task(
    heading="Implement backend API",
    details="Create RESTful API endpoints",
    time_estimate=240
)

main_task.add_subtask(subtask1)
main_task.add_subtask(subtask2)

# Save to storage
store.add_task(main_task)
```

## API Reference

### Task Model

#### Task Class

```python
class Task:
    def __init__(self, heading: str, details: str, status: TaskStatus = TaskStatus.PENDING,
                 deadline: Optional[datetime] = None, time_estimate: Optional[int] = None,
                 resource_link: Optional[str] = None, subtasks: List['Task'] = None,
                 id: UUID = None, created_at: datetime = None, updated_at: datetime = None)
```

**Methods:**
- `update(**kwargs)`: Update task fields and set updated_at timestamp
- `add_subtask(subtask: Task)`: Add a subtask to this task
- `remove_subtask(subtask_id: UUID)`: Remove a subtask by its ID
- `to_dict() -> dict`: Convert task to dictionary for JSON serialization
- `from_dict(data: dict) -> Task`: Create task from dictionary (class method)

#### TaskStatus Enum

```python
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
```

### JsonStore Class

```python
class JsonStore:
    def __init__(self, storage_dir: str = "data")
```

**Methods:**
- `add_task(task: Task) -> str`: Add a new task and return its ID
- `get_task(task_id: str) -> Optional[Task]`: Retrieve a task by ID
- `update_task(task_id: str, **kwargs) -> bool`: Update a task by ID
- `delete_task(task_id: str) -> bool`: Delete a task by ID
- `list_tasks() -> List[Task]`: Get all tasks
- `list_tasks_by_status(status: TaskStatus) -> List[Task]`: Filter tasks by status
- `list_tasks_by_deadline(before_date: datetime = None, after_date: datetime = None) -> List[Task]`: Filter by deadline
- `search_tasks(query: str) -> List[Task]`: Search tasks by content
- `get_tasks_by_time_estimate(min_minutes: int = None, max_minutes: int = None) -> List[Task]`: Filter by time estimate
- `get_task_count() -> int`: Get total number of tasks
- `clear_all_tasks()`: Remove all tasks from storage
- `get_storage_info() -> dict`: Get storage information and statistics

## Testing

Run the comprehensive test suite:

```bash
python3 test_storage.py
```

The test suite covers:
- Task creation and properties
- Task serialization/deserialization
- Subtask management
- JsonStore CRUD operations
- Querying and filtering
- Data persistence
- Error handling

## Demo

Run the usage demonstration:

```bash
python3 demo_usage.py
```

The demo showcases:
- Basic task management operations
- Task updates and modifications
- Working with subtasks
- Storage information and statistics
- Various querying methods

## Data Storage

Tasks are stored in JSON format in the specified storage directory. The default structure is:

```
data/
└── tasks.json
```

The JSON file contains a dictionary where keys are task IDs and values are task data in dictionary format.

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass before submitting changes

## License

This project is part of the Genie Backend system for intelligent task management.
