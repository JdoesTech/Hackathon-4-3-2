#!/usr/bin/env python3
"""
Scholarship Matchmaker - Flask Application Runner
"""

import os
import sys
from app import app, init_database

def main():
    """Main application entry point"""
    print(" Starting Scholarship Matchmaker...")
    print("=" * 50)
    
    # Check if database initialization is successful
    print(" Initializing database...")
    if init_database():
        print(" Database initialized successfully!")
    else:
        print(" Database initialization failed!")
        print("Please check your MySQL connection and try again.")
        sys.exit(1)
    
    # Get configuration from environment or use defaults
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f" Starting server on http://{host}:{port}")
    print(f" Debug mode: {'ON' if debug else 'OFF'}")
    print("=" * 50)
    print(" Ready for scholarship matching!")
    
    # Start the Flask application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()