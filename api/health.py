from flask import Flask, jsonify
import os
import sys

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Vercel deployment"""
    try:
        # Basic health check
        return jsonify({
            "status": "healthy",
            "service": "Genie Backend API",
            "version": "1.0.0",
            "environment": "vercel",
            "timestamp": "2024-01-01T00:00:00Z"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "service": "Genie Backend API"
        }), 500

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)
