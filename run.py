#!/usr/bin/env python3
"""
Railway startup script for Genie Backend
Handles dynamic port assignment properly
"""

import os
import sys
import subprocess

def main():
    # Get port from environment variable, default to 5000
    port = os.environ.get('PORT', '5000')
    
    print(f"Starting Genie Backend on port {port}")
    
    # Start gunicorn with the port
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '4',
        '--timeout', '120',
        'web_server:app'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Execute the command
    sys.exit(subprocess.call(cmd))

if __name__ == '__main__':
    main()
