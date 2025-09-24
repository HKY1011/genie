#!/bin/bash

# Railway startup script for Genie Backend
# Handles dynamic port assignment

# Set default port if PORT is not set
export PORT=${PORT:-5000}

echo "Starting Genie Backend on port $PORT"

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 web_server:app
