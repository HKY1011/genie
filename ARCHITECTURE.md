# Genie Backend - Architecture Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)

---

## 🎯 Overview

Genie Backend is an AI-powered task management system that uses multiple intelligent agents to:
- Extract and structure tasks from natural language
- Break down complex tasks into manageable subtasks
- Intelligently prioritize work using brain-aware algorithms
- Schedule tasks to Google Calendar
- Provide real-time task recommendations

### Tech Stack
- **Backend Framework**: Flask (Python 3.9+)
- **AI/LLM**: Google Gemini API
- **Research**: Perplexity API
- **Calendar**: Google Calendar API
- **Storage**: JSON-based persistent storage
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS

---

## 📁 Project Structure

```
genie_backend/
├── 📱 Core Application
│   ├── main.py                 # Main system orchestrator
│   ├── web_server.py           # Flask web server & API
│   └── health_check.py         # System health monitoring
│
├── 🤖 Agents (AI Components)
│   ├── task_extraction_agent.py      # Extracts tasks from user input
│   ├── planning_agent.py             # Breaks tasks into subtasks
│   ├── genieorchestrator_agent.py    # Prioritizes & recommends tasks
│   ├── supervisor_agent.py           # Oversees agent coordination
│   ├── scheduler_agent.py            # Manages task scheduling
│   ├── feedback_agent.py             # Learns from user feedback
│   └── resource_agent.py             # Finds research resources
│
├── 🔌 Integrations
│   ├── gemini_api.py           # Google Gemini LLM integration
│   ├── google_calendar_api.py  # Calendar integration
│   └── perplexity_api.py       # Research/search integration
│
├── 📊 Models
│   ├── task_model.py           # Task data structures
│   └── user_session.py         # User session management
│
├── 💾 Storage
│   ├── json_store.py           # Persistent JSON storage
│   ├── user_tasks.json         # Production task data
│   ├── progress.json           # User progress data
│   └── sessions/               # User session files
│
├── 🎨 Frontend
│   └── templates/
│       └── index.html          # Web UI (single-page app)
│
├── 📝 Prompts
│   ├── extract_task.prompt           # Task extraction prompt
│   ├── breakdown_chunk.prompt        # Task breakdown prompt
│   ├── genieorchestrator.prompt      # Original orchestrator prompt
│   └── genieorchestrator_ai.prompt   # AI-driven prioritization prompt
│
├── 🚀 Deployment
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Docker container config
│   ├── docker-compose.yml      # Multi-container orchestration
│   ├── nginx.conf              # Nginx reverse proxy config
│   ├── Procfile                # Heroku deployment config
│   └── env.example             # Environment variables template
│
└── 📚 Documentation
    ├── README.md               # Project overview
    ├── ARCHITECTURE.md         # This file
    ├── DEPLOYMENT_GUIDE.md     # Deployment instructions
    ├── USAGE_GUIDE.md          # User guide
    └── GOOGLE_CALENDAR_SETUP.md # Calendar setup guide
```

---

## 🔧 Core Components

### 1. **Main System (`main.py`)**
The central orchestrator that coordinates all components:
- Initializes all agents and integrations
- Manages the task processing pipeline
- Handles user input and system state
- Coordinates between agents for optimal task management

**Key Classes:**
- `GenieInteractiveSystem`: Main system controller

### 2. **Web Server (`web_server.py`)**
Flask-based REST API and web interface:
- Serves the frontend UI
- Provides REST API endpoints
- Handles CORS for cross-origin requests
- Manages real-time task updates

**Key Endpoints:**
- `GET /` - Web UI
- `GET /health` - System health check
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `DELETE /api/tasks/<id>` - Delete task
- `GET /api/current-subtask` - Get next recommended subtask

### 3. **Agents System**

#### **Task Extraction Agent** (`task_extraction_agent.py`)
- Parses natural language input
- Extracts task title, description, and deadline
- Identifies urgency and priority signals

#### **Planning Agent** (`planning_agent.py`)
- Breaks complex tasks into actionable subtasks
- Estimates time requirements
- Finds relevant research resources
- Creates structured task plans

#### **Orchestrator Agent** (`genieorchestrator_agent.py`)
- Uses AI to prioritize tasks intelligently
- Considers psychological factors (energy, motivation, flow)
- Adapts to user patterns and context
- Recommends the best next action

#### **Supervisor Agent** (`supervisor_agent.py`)
- Monitors agent performance
- Ensures coordination between agents
- Handles error recovery

#### **Scheduler Agent** (`scheduler_agent.py`)
- Manages task scheduling
- Coordinates with Google Calendar
- Handles time-based triggers

#### **Feedback Agent** (`feedback_agent.py`)
- Learns from user actions
- Adapts recommendations
- Improves over time

#### **Resource Agent** (`resource_agent.py`)
- Finds relevant articles, videos, tutorials
- Categorizes learning resources
- Prioritizes quality content

### 4. **Integrations**

#### **Gemini API** (`gemini_api.py`)
- Primary LLM for task processing
- Powers all AI agents
- Handles natural language understanding

#### **Google Calendar API** (`google_calendar_api.py`)
- OAuth2 authentication
- Event creation and management
- Free/busy time checking
- Only schedules tasks ≤30 minutes

#### **Perplexity API** (`perplexity_api.py`)
- Research and information gathering
- Finds high-quality resources
- Provides context for tasks

### 5. **Storage System** (`storage/json_store.py`)
- Persistent JSON-based storage
- Auto-backup functionality
- Transaction-safe updates
- Session management

---

## 🔄 Data Flow

### Task Creation Flow

```
1. User Input (Web UI)
   ↓
2. Task Extraction Agent
   - Parses natural language
   - Extracts structured data
   ↓
3. Planning Agent
   - Breaks into subtasks
   - Estimates time
   - Finds resources
   ↓
4. Storage System
   - Saves task & subtasks
   - Creates backup
   ↓
5. Orchestrator Agent
   - Analyzes all tasks
   - Recommends next action
   - Considers psychology
   ↓
6. Scheduler Agent
   - Schedules to calendar (if ≤30 min)
   - Sets time blocks
   ↓
7. Web UI Update
   - Shows current subtask
   - Displays recommendations
```

### AI Prioritization Flow

```
1. Orchestrator receives:
   - All tasks with subtasks (max 5 per task)
   - User schedule & context
   - Psychological state
   ↓
2. AI Analysis considers:
   - Current energy level
   - Time of day (peak hours)
   - Cognitive preferences
   - Deadlines & urgency
   - Task complexity
   - Flow potential
   ↓
3. Returns recommendation with:
   - Next best subtask
   - Reasoning
   - Psychological fit
   - Expected outcomes
```

---

## 🌐 API Endpoints

### Health & Status
- `GET /health` - System health check
- `GET /api/api_health_check` - API health check

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
  ```json
  {
    "task_description": "Learn Python and build a web app",
    "user_id": "default_user"
  }
  ```
- `DELETE /api/tasks/<task_id>` - Delete task
- `PATCH /api/tasks/<task_id>/status` - Update task status

### Subtasks
- `GET /api/current-subtask` - Get recommended next subtask
- `POST /api/subtasks/<subtask_id>/complete` - Mark subtask complete
- `POST /api/subtasks/<subtask_id>/feedback` - Provide feedback

### System
- `GET /api/user/<user_id>/stats` - Get user statistics
- `GET /api/calendar/events` - Get calendar events

---

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your API keys

# Run the server
python web_server.py
```

### Docker
```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8080
```

### Heroku
```bash
# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key

# Deploy
git push heroku main
```

### VPS (Ubuntu/Debian)
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip nginx

# Setup application
pip3 install -r requirements.txt

# Configure Nginx (use nginx.conf)
sudo cp nginx.conf /etc/nginx/sites-available/genie
sudo ln -s /etc/nginx/sites-available/genie /etc/nginx/sites-enabled/

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 web_server:app
```

---

## 🔐 Environment Variables

Required variables (add to `.env`):
```bash
# AI APIs
GEMINI_API_KEY=your_gemini_api_key
PERPLEXITY_API_KEY=your_perplexity_key

# Google Calendar (OAuth2)
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=token.json

# Application
FLASK_ENV=production
FLASK_DEBUG=False
PORT=8080

# Optional
LOG_LEVEL=INFO
BACKUP_ENABLED=True
```

---

## 📊 Key Features

### 1. **Brain-Aware Prioritization**
Uses psychological principles to recommend tasks based on:
- Current energy levels
- Time of day (circadian rhythms)
- Cognitive load
- Flow state potential
- Motivation factors

### 2. **Smart Calendar Integration**
- Only schedules short tasks (≤30 minutes)
- Checks calendar availability
- Schedules within next 2 hours
- Avoids over-scheduling

### 3. **Adaptive Learning**
- Learns from user feedback
- Adjusts recommendations
- Improves over time
- Personalizes experience

### 4. **Research Integration**
- Finds relevant learning resources
- Categorizes by type (article, video, tutorial)
- Provides focused sections
- Saves research time

---

## 🛠️ Development Guidelines

### Adding New Agents
1. Create agent file in `agents/`
2. Inherit from base agent class
3. Implement required methods
4. Register in `main.py`

### Adding New Endpoints
1. Add route in `web_server.py`
2. Implement handler function
3. Add error handling
4. Update API documentation

### Modifying Prompts
1. Edit prompt files in `prompts/`
2. Test with sample data
3. Validate AI responses
4. Update documentation

---

## 📝 Notes

### Storage
- Uses JSON for simplicity and transparency
- Auto-backup before each write
- Easy to inspect and debug
- Can migrate to database later

### Scalability
- Single-user focus (MVP)
- Extensible to multi-user
- Can add Redis for caching
- Can add PostgreSQL for scale

### Security
- API keys in environment variables
- OAuth2 for Google Calendar
- CORS enabled for web access
- No sensitive data in code

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📞 Support

For issues or questions:
- Check the documentation
- Review error logs
- Open GitHub issue

---

**Built with ❤️ for better productivity and brain-aware task management**
