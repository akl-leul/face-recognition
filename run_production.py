#!/usr/bin/env python3
"""
Production runner for face recognition app
"""
import os
import sys
from web_app import app

if __name__ == '__main__':
    # Get local IP for network access
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    
    print(f"🌐 Starting production server...")
    print(f"📍 Local access: http://localhost:5000")
    print(f"🌍 Network access: http://{local_ip}:5000")
    print(f"💡 Camera and recognition will initialize on demand")
    
    # Production settings
    app.run(
        host='0.0.0.0',  # Allow network access
        port=5000,
        debug=False,     # Production mode
        threaded=True    # Handle multiple requests
    )
