# 🎯 Genie Interactive Demo - Usage Guide

## 🚀 Quick Start

### Option 1: Quick Test (No Input Required)
```bash
python3 quick_test.py
```
- **Predefined tasks**: Python learning, React app, Job interview prep
- **Predefined schedule**: 3 time blocks with energy levels
- **Instant results**: See orchestration in action immediately

### Option 2: Interactive Demo (Full Experience)
```bash
python3 interactive_demo.py
```
- **Custom tasks**: Enter your own tasks in natural language
- **Custom schedule**: Set your own availability and energy levels
- **Real-time interaction**: Natural language commands

## 🎯 How to Use the Interactive Demo

### 1. Setup Phase
- **Work hours**: Enter your typical start and end times
- **Energy levels**: Choose when you have the most energy (Morning/Afternoon/Evening)
- **Session preferences**: Set preferred and maximum work session lengths

### 2. Task Entry
Enter your tasks in natural language:
```
Task 1: I need to learn Python programming by next Friday
Task 2: Build a React todo app with authentication
Task 3: Write a research paper on machine learning
```

### 3. Interactive Commands
Once the system is running, you can use natural language:

#### ✅ Mark Tasks as Complete
```
"I finished the Python task"
"Mark the React app as done"
"I completed the research paper"
```

#### ➕ Add New Tasks
```
"Add a new task: learn machine learning by next Friday"
"I need to prepare for job interview next week"
```

#### 📊 Check Progress
```
"Show me my progress"
"What's my status?"
```

#### 🎯 Get Next Recommendation
```
"What should I do next?"
"Give me the next task"
```

#### 🔄 Edit Tasks
```
"Change the Python deadline to next Monday"
"Update the React app details to include authentication"
```

## 🎉 Key Improvements

### ✅ Natural Language Processing
- No more rigid commands like `done task_1`
- Just tell the system what you want in plain English
- The AI understands context and intent

### ✅ Automatic Status Updates
- When you mark a task as done, all subtasks are automatically completed
- The system remembers your progress across sessions
- No more repeating the same task

### ✅ Smart Recommendations
- After completing a task, the system automatically suggests the next best action
- Recommendations consider deadlines, energy levels, and task dependencies
- No priority numbers cluttering the interface

### ✅ Better Error Handling
- Handles non-numeric inputs gracefully
- Provides clear feedback for all actions
- Continues working even if some operations fail

## 🔧 Technical Features

### 📅 Availability Management
- **Current**: Dummy data setup with interactive prompts
- **Future**: Google Calendar integration for real-time availability

### 🧠 AI-Powered Task Management
- **TaskExtractionAgent**: Converts natural language to structured actions
- **PlanningAgent**: Breaks down complex tasks into manageable chunks
- **GenieOrchestrator**: Prioritizes and schedules tasks intelligently

### 📊 Real-Time Context
- **Task priorities** based on deadlines and importance
- **Energy level matching** - harder tasks during peak energy
- **Progress tracking** across all tasks
- **Resource recommendations** with specific focus areas

## 🎯 Example Session

```bash
$ python3 interactive_demo.py

📅 Setting Up Your Availability
🕐 Start time: 09:00
🕐 End time: 17:00
⚡ Energy level: Morning (high energy)

📝 Adding Tasks
Task 1: I need to learn Python programming by next Friday
Task 2: Build a React todo app with authentication
Task 3: Write a research paper on machine learning

🎯 RECOMMENDED NEXT ACTION:
📋 Task: task_1
🎯 Chunk: Set up Python development environment
⏱️  Time: 30 minutes
📅 Scheduled: 2024-08-22T09:00:00Z to 2024-08-22T09:30:00Z

🔄 Interactive Task Management
What would you like to do? I finished the Python task
✅ Marked 'Learn Python Programming' as completed

🎯 Getting next recommendation...
🎯 RECOMMENDED NEXT ACTION:
📋 Task: task_2
🎯 Chunk: Set up React development environment
⏱️  Time: 25 minutes
📅 Scheduled: 2024-08-22T09:30:00Z to 2024-08-22T09:55:00Z

What would you like to do? Add a new task: learn machine learning by next Friday
✅ Added new task: 'Learn Machine Learning'

What would you like to do? Show me my progress
📊 Current Status:
✅ Learn Python Programming: 2/2 completed
⏳ Build React Todo App: 0/1 completed
⏳ Learn Machine Learning: 0/0 completed
```

## 🚀 Ready to Test!

The system is now ready for you to test with natural language interaction. Just run:

```bash
python3 interactive_demo.py
```

And start telling Genie what you want to do! 🎯 