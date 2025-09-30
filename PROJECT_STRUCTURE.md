# Genie Backend - Project Structure

## 🗂️ Clean Architecture Overview

```
genie_backend/
│
├── 📱 CORE APPLICATION (3 files)
│   ├── main.py                          # Main system orchestrator & task pipeline
│   ├── web_server.py                    # Flask REST API & web UI server
│   └── health_check.py                  # System health monitoring
│
├── 🤖 AGENTS (7 files)
│   ├── __init__.py
│   ├── task_extraction_agent.py         # Parses user input → structured tasks
│   ├── planning_agent.py                # Breaks tasks → actionable subtasks  
│   ├── genieorchestrator_agent.py       # AI prioritization & recommendations
│   ├── supervisor_agent.py              # Coordinates agents & error handling
│   ├── scheduler_agent.py               # Time management & scheduling
│   ├── feedback_agent.py                # Learning & adaptation
│   └── resource_agent.py                # Research & learning resources
│
├── 🔌 INTEGRATIONS (3 files)
│   ├── __init__.py
│   ├── gemini_api.py                    # Google Gemini LLM (primary AI)
│   ├── google_calendar_api.py           # Calendar management (OAuth2)
│   └── perplexity_api.py                # Research & information gathering
│
├── 📊 MODELS (2 files)
│   ├── __init__.py
│   ├── task_model.py                    # Task & subtask data structures
│   └── user_session.py                  # User session management
│
├── 💾 STORAGE
│   ├── __init__.py
│   ├── json_store.py                    # Persistent storage with auto-backup
│   ├── user_tasks.json                  # Production task database
│   ├── progress.json                    # User progress tracking
│   └── sessions/                        # User session files
│       └── *.json
│
├── 🎨 FRONTEND
│   └── templates/
│       └── index.html                   # Modern web UI (Tailwind CSS)
│
├── 📝 PROMPTS (4 files)
│   ├── __init__.py
│   ├── extract_task.prompt              # Task extraction AI prompt
│   ├── breakdown_chunk.prompt           # Task breakdown AI prompt
│   ├── genieorchestrator.prompt         # Original prioritization prompt
│   └── genieorchestrator_ai.prompt      # Brain-aware prioritization prompt
│
├── 🔧 UTILITIES
│   └── __init__.py                      # Utility functions
│
├── 🚀 DEPLOYMENT (7 files)
│   ├── requirements.txt                 # Python dependencies
│   ├── Dockerfile                       # Docker container configuration
│   ├── docker-compose.yml               # Multi-container orchestration
│   ├── nginx.conf                       # Nginx reverse proxy config
│   ├── Procfile                         # Heroku deployment
│   ├── env.example                      # Environment variables template
│   └── .gitignore                       # Git ignore rules
│
├── 🔐 CREDENTIALS (2 files)
│   ├── credentials.json                 # Google OAuth2 credentials
│   └── token.json                       # Google OAuth2 token
│
└── 📚 DOCUMENTATION (5 files)
    ├── README.md                        # Project overview & quick start
    ├── ARCHITECTURE.md                  # System architecture & design
    ├── PROJECT_STRUCTURE.md             # This file
    ├── DEPLOYMENT_GUIDE.md              # Deployment instructions
    ├── USAGE_GUIDE.md                   # User guide & examples
    └── GOOGLE_CALENDAR_SETUP.md         # Calendar integration setup
```

---

## 📋 File Count Summary

| Category | Files | Purpose |
|----------|-------|---------|
| **Core Application** | 3 | Main system logic |
| **Agents** | 7 | AI task management |
| **Integrations** | 3 | External APIs |
| **Models** | 2 | Data structures |
| **Storage** | 1 + data | Persistence layer |
| **Frontend** | 1 | Web interface |
| **Prompts** | 4 | AI instructions |
| **Deployment** | 7 | Production configs |
| **Documentation** | 5 | Guides & docs |
| **Total** | **~35 files** | Clean & organized |

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                       USER INPUT                         │
│                    (Web UI / API)                        │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│               TASK EXTRACTION AGENT                      │
│   • Parses natural language                             │
│   • Extracts: heading, details, deadline                │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  PLANNING AGENT                          │
│   • Breaks into subtasks                                │
│   • Estimates time (max 30 min each)                    │
│   • Finds research resources                            │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  STORAGE SYSTEM                          │
│   • Saves task + subtasks                               │
│   • Creates auto-backup                                 │
│   • Updates session state                               │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT (AI)                     │
│   • Analyzes ALL tasks (up to 5 subtasks each)          │
│   • Brain-aware prioritization                          │
│   • Considers: energy, time, psychology                 │
│   • Returns: best next subtask + reasoning              │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              SCHEDULER AGENT                             │
│   • Checks if subtask ≤ 30 minutes                      │
│   • Verifies calendar availability                       │
│   • Schedules to Google Calendar (if conditions met)    │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  WEB UI UPDATE                           │
│   • Displays current subtask                            │
│   • Shows AI reasoning                                  │
│   • Lists all tasks                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Component Responsibilities

### Core Application
- **main.py**: Orchestrates entire system, manages agent lifecycle
- **web_server.py**: HTTP server, REST API, serves frontend
- **health_check.py**: Monitors system health, reports status

### Agents (AI Brain)
- **Task Extraction**: NL → Structured data
- **Planning**: Task → Subtasks + Resources
- **Orchestrator**: AI-driven prioritization
- **Supervisor**: Agent coordination
- **Scheduler**: Time management
- **Feedback**: Learning & adaptation
- **Resource**: Research gathering

### Integrations (External Services)
- **Gemini API**: Primary LLM for all AI agents
- **Google Calendar**: Event scheduling & management
- **Perplexity API**: Research & information retrieval

### Models (Data Layer)
- **task_model.py**: Task, Subtask, TaskStatus classes
- **user_session.py**: Session state management

### Storage (Persistence)
- **json_store.py**: Transaction-safe JSON storage
- Auto-backup on every write
- Session management

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your API keys
```

### 3. Run the Server
```bash
python web_server.py
# Access at http://localhost:8080
```

---

## 🔧 Configuration Files

### requirements.txt
- Flask, Flask-CORS (web server)
- google-api-python-client (calendar)
- google-generativeai (Gemini)
- python-dotenv (env management)
- All dependencies with versions

### Dockerfile
- Python 3.9 base image
- Multi-stage build
- Production-optimized

### docker-compose.yml
- Backend service
- Nginx reverse proxy
- Volume mounts
- Environment variables

### nginx.conf
- Reverse proxy setup
- Static file serving
- SSL/TLS configuration
- Load balancing ready

---

## 📊 System Architecture Layers

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER              │
│  • Web UI (HTML/CSS/JS)                │
│  • REST API (Flask)                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         APPLICATION LAYER               │
│  • Main Orchestrator                    │
│  • Agent Coordination                   │
│  • Business Logic                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         AGENT LAYER (AI)                │
│  • Task Processing Agents               │
│  • AI Decision Making                   │
│  • Learning & Adaptation                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         INTEGRATION LAYER               │
│  • Gemini API (LLM)                    │
│  • Google Calendar API                  │
│  • Perplexity API (Research)           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         DATA LAYER                      │
│  • JSON Storage                         │
│  • Session Management                   │
│  • Auto Backup System                   │
└─────────────────────────────────────────┘
```

---

## 🎨 Design Principles

1. **Modularity**: Each agent is independent and replaceable
2. **Single Responsibility**: Each file has one clear purpose
3. **Clean Interfaces**: Well-defined APIs between components
4. **Fail-Safe**: Error handling and auto-recovery
5. **Observable**: Logging and health monitoring
6. **Scalable**: Easy to extend and scale

---

## 📝 Development Workflow

### Adding a New Feature
1. Identify which layer it belongs to
2. Create/modify relevant files
3. Update prompts if AI-related
4. Add API endpoints if needed
5. Update documentation
6. Test thoroughly

### Modifying AI Behavior
1. Edit prompt files in `prompts/`
2. Test with various inputs
3. Validate responses
4. Monitor in production

### Deploying Changes
1. Test locally
2. Update version
3. Build Docker image
4. Deploy to production
5. Monitor logs

---

## 🔍 File Descriptions

### Core Files

**main.py** (804 lines)
- `GenieInteractiveSystem` class
- Agent initialization
- Task processing pipeline
- AI orchestration logic

**web_server.py** (835 lines)
- Flask application setup
- REST API endpoints
- CORS configuration
- Error handling

**health_check.py** (50 lines)
- System health checks
- Component status monitoring
- API availability testing

### Agent Files

Each agent file follows this structure:
- Class definition
- Initialization with API clients
- Core processing method
- Error handling
- Logging

### Integration Files

Standard pattern:
- API client initialization
- Authentication handling
- Request/response methods
- Error handling & retries

---

## 🛡️ Security Considerations

1. **API Keys**: Stored in `.env`, never in code
2. **OAuth2**: Secure Google Calendar authentication
3. **CORS**: Configured for specific origins
4. **Input Validation**: All user inputs validated
5. **Error Messages**: No sensitive data in errors

---

## 📊 Monitoring & Logging

- **Health Endpoint**: `/health` for system status
- **Logging**: INFO level for production
- **Backup System**: Auto-backup before writes
- **Error Tracking**: Comprehensive error logs

---

**Clean, organized, and production-ready! 🚀**
