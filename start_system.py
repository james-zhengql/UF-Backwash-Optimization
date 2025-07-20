#!/usr/bin/env python3
"""
System startup script for Intelligent UF Backwash
This script sets up and starts both frontend and backend components
"""

import os
import sys
import subprocess
import time
import webbrowser
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def create_virtual_environment():
    """Create Python virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created successfully!")
    else:
        print("Virtual environment already exists")
    
    return venv_path

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    # Determine the pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def check_node_dependencies():
    """Check if Node.js dependencies are installed"""
    if Path("node_modules").exists():
        print("Node.js dependencies already installed")
        return True
    else:
        print("Node.js dependencies not found")
        print("Please run: npm install")
        return False

def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    
    # Determine the python command based on OS
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen(
            [python_cmd, "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                print("Backend server started successfully!")
                return backend_process
            else:
                print("Backend server started but health check failed")
                return backend_process
        except requests.exceptions.RequestException:
            print("Backend server started but health check failed")
            return backend_process
            
    except Exception as e:
        print(f"Error starting backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("Starting frontend server...")
    
    try:
        # Use Python's built-in HTTP server for frontend
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8080"],
            cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(2)
        
        print("Frontend server started successfully!")
        return frontend_process
        
    except Exception as e:
        print(f"Error starting frontend: {e}")
        return None

def open_browser():
    """Open browser to the application"""
    print("Opening application in browser...")
    webbrowser.open("http://localhost:8080")

def wait_for_user_input():
    """Wait for user to stop the system"""
    print("\n" + "="*50)
    print("System is running!")
    print("Frontend: http://localhost:8080")
    print("Backend API: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the system")
    print("="*50)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")

def cleanup(backend_process, frontend_process):
    """Clean up processes"""
    if backend_process:
        print("Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()
    
    if frontend_process:
        print("Stopping frontend server...")
        frontend_process.terminate()
        frontend_process.wait()
    
    print("System stopped successfully!")

def main():
    """Main startup function"""
    print("Intelligent UF Backwash System Startup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Exiting.")
        return
    
    # Check Node.js dependencies
    if not check_node_dependencies():
        print("Please install Node.js dependencies first:")
        print("npm install")
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("Failed to start backend. Exiting.")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("Failed to start frontend. Stopping backend...")
        backend_process.terminate()
        return
    
    # Open browser
    open_browser()
    
    # Wait for user input
    try:
        wait_for_user_input()
    finally:
        cleanup(backend_process, frontend_process)

if __name__ == "__main__":
    main() 