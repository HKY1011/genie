#!/usr/bin/env python3
"""
Railway startup script for Genie Backend
Simple Python deployment without Docker
"""

import os
import sys
import subprocess

def main():
    # Get port from Railway environment
    port = os.environ.get('PORT', '5000')
    
    print(f"🚀 Starting Genie Backend on Railway")
    print(f"📍 Port: {port}")
    print(f"🌐 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    
    # Start gunicorn
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '4',
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'web_server:app'
    ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    
    try:
        # Execute the command
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main()
