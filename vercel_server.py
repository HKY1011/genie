#!/usr/bin/env python3
"""
Vercel-compatible Flask server for Genie Backend
Simplified version for serverless deployment
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# In-memory storage for Vercel (stateless)
tasks_storage = []
sessions_storage = {}

@app.route('/')
def index():
    """Serve the main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Genie Backend",
        "version": "1.0.0",
        "environment": "vercel",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def api_health():
    """API health check"""
    return jsonify({
        "status": "healthy",
        "api": "Genie Backend API",
        "version": "1.0.0"
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        return jsonify({
            "tasks": tasks_storage,
            "count": len(tasks_storage),
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        if not data or 'heading' not in data:
            return jsonify({
                "error": "Task heading is required"
            }), 400
        
        task = {
            "id": len(tasks_storage) + 1,
            "heading": data['heading'],
            "details": data.get('details', ''),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "deadline": data.get('deadline'),
            "priority": data.get('priority', 'medium')
        }
        
        tasks_storage.append(task)
        
        return jsonify({
            "task": task,
            "status": "success",
            "message": "Task created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.get_json()
        
        task = next((t for t in tasks_storage if t['id'] == task_id), None)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        for key, value in data.items():
            if key in task:
                task[key] = value
        
        task['updated_at'] = datetime.now().isoformat()
        
        return jsonify({
            "task": task,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        global tasks_storage
        tasks_storage = [t for t in tasks_storage if t['id'] != task_id]
        
        return jsonify({
            "status": "success",
            "message": "Task deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/current-subtask', methods=['GET'])
def get_current_subtask():
    """Get current subtask (simplified for Vercel)"""
    try:
        # Return a mock subtask for demo
        return jsonify({
            "subtask": {
                "id": 1,
                "heading": "Welcome to Genie Backend",
                "details": "This is a simplified version for Vercel deployment",
                "estimated_time": 5,
                "status": "pending"
            },
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback (simplified for Vercel)"""
    try:
        data = request.get_json()
        
        feedback = {
            "id": len(sessions_storage) + 1,
            "feedback": data.get('feedback', ''),
            "rating": data.get('rating', 5),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "feedback": feedback,
            "status": "success",
            "message": "Feedback submitted successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel serverless function handler
def handler(request):
    """Vercel serverless function entry point"""
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
