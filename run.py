#!/usr/bin/env python3
"""
Startup script for the Intelligent UF Backwash API
"""

import uvicorn
import os
from backend.models.database import init_db

def main():
    """Main startup function"""
    # Initialize database
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting server on {host}:{port}")
    print(f"Reload mode: {reload}")
    
    # Start server
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 