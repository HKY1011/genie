from flask import Flask, request, jsonify
import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# In-memory storage for Vercel (stateless)
tasks_storage = []

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        return jsonify({
            "tasks": tasks_storage,
            "count": len(tasks_storage),
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        if not data or 'heading' not in data:
            return jsonify({
                "error": "Task heading is required",
                "status": "error"
            }), 400
        
        # Create task object
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
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.get_json()
        
        # Find task
        task = next((t for t in tasks_storage if t['id'] == task_id), None)
        if not task:
            return jsonify({
                "error": "Task not found",
                "status": "error"
            }), 404
        
        # Update task
        for key, value in data.items():
            if key in task:
                task[key] = value
        
        task['updated_at'] = datetime.now().isoformat()
        
        return jsonify({
            "task": task,
            "status": "success",
            "message": "Task updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        global tasks_storage
        tasks_storage = [t for t in tasks_storage if t['id'] != task_id]
        
        return jsonify({
            "status": "success",
            "message": "Task deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)
