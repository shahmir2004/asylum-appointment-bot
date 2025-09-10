"""
Setup verification script for Asylum Appointment Booking Bot MVP

Run this script after completing T001-T004 to verify the basic setup is correct.
"""

import os
import sys
from pathlib import Path

def verify_setup():
    """Verify that all T001-T004 setup tasks are completed correctly"""
    
    print("="*60)
    print("Asylum Appointment Booking Bot MVP - Setup Verification")
    print("="*60)
    
    # Check project structure (T001)
    required_dirs = ['src', 'tests', 'logs']
    print("\n📁 Checking project structure...")
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {dir_name}/ directory exists")
        else:
            print(f"  ❌ {dir_name}/ directory missing")
    
    # Check requirements.txt (T002)
    print("\n📦 Checking requirements.txt...")
    if os.path.exists('requirements.txt'):
        print("  ✅ requirements.txt exists")
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required_packages = ['playwright', 'schedule', 'python-dotenv', 'pytest']
            for package in required_packages:
                if package in content:
                    print(f"    ✅ {package} listed in requirements")
                else:
                    print(f"    ❌ {package} missing from requirements")
    else:
        print("  ❌ requirements.txt missing")
    
    # Check .env file (T003)
    print("\n🔧 Checking .env configuration...")
    if os.path.exists('.env'):
        print("  ✅ .env file exists")
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'RECIPIENT_EMAIL',
            'SMTP_SERVER', 'SMTP_PORT', 'GOVERNMENT_SITE_URL'
        ]
        for var in required_vars:
            if os.getenv(var):
                print(f"    ✅ {var} configured")
            else:
                print(f"    ❌ {var} missing or empty")
    else:
        print("  ❌ .env file missing")
    
    # Check logging configuration (T004)
    print("\n📝 Checking logging configuration...")
    try:
        sys.path.append('src')
        from logging_config import get_logger
        
        print("  ✅ logging_config.py module loads successfully")
        
        # Check if log file was created
        if os.path.exists('logs/asylum_bot.log'):
            print("  ✅ logs/asylum_bot.log file exists")
        else:
            print("  ❌ logs/asylum_bot.log file missing")
            
    except ImportError as e:
        print(f"  ❌ logging_config.py import failed: {e}")
    
    print("\n" + "="*60)
    print("Setup verification complete!")
    print("Next: Run tasks T005-T009 to create failing tests")
    print("="*60)

if __name__ == "__main__":
    verify_setup()
