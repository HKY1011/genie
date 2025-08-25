# 🧞‍♂️ Genie - AI-Powered Task Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/yourusername/genie)
[![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Perplexity-orange.svg)](https://ai.google.dev)

> **Your intelligent AI assistant for task planning, scheduling, and productivity management**

Genie is an advanced AI-powered task management system that combines natural language processing, intelligent planning, and calendar integration to help you organize and execute your tasks efficiently. Think of it as having a personal AI assistant that understands your goals and helps you achieve them.

## ✨ Key Features

### 🤖 **Multi-Agent AI Architecture**
- **Task Extraction Agent**: Converts natural language into structured tasks
- **Planning Agent**: Breaks down complex projects into manageable subtasks
- **Orchestrator Agent**: Coordinates all agents and manages workflow
- **Supervisor Agent**: Monitors system health and performance
- **Feedback Agent**: Learns from your interactions and improves recommendations

### 🗣️ **Natural Language Interface**
```bash
# Instead of rigid commands, just tell Genie what you want:
"I need to learn Python programming by next Friday"
"Build a React todo app with authentication"
"Prepare for my job interview next week"
```

### 📅 **Smart Calendar Integration**
- **Google Calendar API**: Real-time availability detection
- **Energy-based Scheduling**: Matches tasks to your peak energy times
- **Deadline Management**: Automatic priority based on due dates
- **Conflict Resolution**: Intelligent scheduling to avoid overlaps

### 🧠 **Intelligent Task Management**
- **Automatic Subtask Generation**: Complex tasks broken into actionable steps
- **Progress Tracking**: Real-time status updates and completion tracking
- **Resource Linking**: Automatic attachment of relevant resources
- **Persistent Storage**: Your tasks and progress saved across sessions

### 🔄 **Interactive Feedback Loop**
- **Natural Language Updates**: "I finished the Python task" automatically updates status
- **Smart Recommendations**: AI suggests next best actions based on context
- **Learning System**: Improves recommendations based on your patterns

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Calendar API credentials (optional, for calendar integration)
- Gemini API key (for AI processing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/genie.git
cd genie
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the interactive demo**
```bash
cd genie_backend
python3 interactive_demo.py
```

## 🎯 Usage Examples

### Basic Task Management
```python
from genie_backend.main import GenieInteractiveSystem

# Initialize the system
genie = GenieInteractiveSystem()

# Add tasks using natural language
genie.add_task("Learn Python programming by next Friday")
genie.add_task("Build a React todo app with authentication")
genie.add_task("Prepare for job interview next week")

# Get AI-powered recommendations
recommendations = genie.get_recommendations()
```

### Interactive Commands
```bash
# Mark tasks as complete
"I finished the Python task"
"Mark the React app as done"

# Add new tasks
"Add a new task: learn machine learning by next Friday"
"I need to prepare for job interview next week"

# Check progress
"Show me my progress"
"What's my status?"

# Get next recommendation
"What should I do next?"
"Give me the next task"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Genie Interactive System                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   User      │  │   Natural   │  │   Task      │        │
│  │   Input     │→ │   Language  │→ │ Extraction  │        │
│  │             │  │   Processing│  │   Agent     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                              ↓                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Planning  │  │Orchestrator │  │  Supervisor │        │
│  │   Agent     │← │   Agent     │→ │   Agent     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                              ↓                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Google    │  │   Feedback  │  │   JSON      │        │
│  │  Calendar   │  │   Agent     │  │  Storage    │        │
│  │    API      │  └─────────────┘  └─────────────┘        │
│  └─────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### Agents
- **`TaskExtractionAgent`**: Converts natural language to structured tasks
- **`PlanningAgent`**: Creates detailed task breakdowns and timelines
- **`GenieOrchestrator`**: Coordinates all agents and manages workflow
- **`SupervisorAgent`**: Monitors system health and performance
- **`FeedbackAgent`**: Processes user feedback and improves recommendations

### Integrations
- **`GoogleCalendarAPI`**: Real-time calendar integration
- **`GeminiAPIClient`**: AI processing and natural language understanding
- **`PerplexityAPIClient`**: Enhanced research and information gathering

### Storage
- **`JsonStore`**: Persistent task storage with advanced querying
- **`UserSession`**: Session management and user state persistence
- **`SessionManager`**: Multi-user session handling

## 📊 Data Models

### Task Structure
```python
class Task:
    id: UUID                    # Unique identifier
    heading: str               # Task title
    details: str               # Detailed description
    status: TaskStatus         # PENDING, IN_PROGRESS, DONE, CANCELLED
    deadline: datetime         # Due date and time
    time_estimate: int         # Estimated minutes
    resource_link: str         # Relevant URLs or resources
    subtasks: List[Task]       # Nested subtasks
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last update timestamp
```

## 🧪 Testing

### Run Test Suite
```bash
# Comprehensive system tests
python3 comprehensive_test_suite.py

# Storage tests
python3 test_storage.py

# Interactive demo tests
python3 interactive_test.py
```

### Quick Test (No Setup Required)
```bash
python3 quick_test.py
```

## 📚 Documentation

- **[Usage Guide](genie_backend/USAGE_GUIDE.md)**: Detailed usage instructions
- **[System Analysis](genie_backend/SYSTEM_ANALYSIS.md)**: Technical architecture
- **[Google Calendar Setup](genie_backend/GOOGLE_CALENDAR_SETUP.md)**: Calendar integration guide
- **[API Reference](genie_backend/README.md)**: Backend API documentation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `python3 comprehensive_test_suite.py`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini API** for AI processing capabilities
- **Google Calendar API** for scheduling integration
- **Perplexity API** for enhanced research capabilities
- **Python Community** for excellent libraries and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/genie/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/genie/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/genie/wiki)

---

<div align="center">

**Made with ❤️ by the Genie Team**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/genie?style=social)](https://github.com/yourusername/genie)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/genie?style=social)](https://github.com/yourusername/genie)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/genie)](https://github.com/yourusername/genie/issues)

</div>
