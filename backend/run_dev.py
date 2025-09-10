#!/usr/bin/env python3
"""
Development server runner for the Asylum Appointment Bot API.
Run this script to start the development server with auto-reload.
"""
import sys
import os

# Add the backend src directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, "src")
sys.path.insert(0, src_dir)

if __name__ == "__main__":
    from src.main import run_dev_server
    run_dev_server()
