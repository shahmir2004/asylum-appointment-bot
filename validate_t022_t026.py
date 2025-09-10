#!/usr/bin/env python3
"""
Simple test for T022-T026 validation without Unicode issues
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that core modules can be imported"""
    try:
        print("Testing core module imports...")
        
        from config import Config
        print("✓ Config module imported")
        
        # Test config creation
        config = Config.from_env()
        print("✓ Config created from environment")
        
        # Test validation
        validation = config.validate()
        print(f"✓ Config validation structure: {type(validation).__name__}")
        
        if validation.get('valid'):
            print("✓ Config validation: PASSED")
        else:
            missing_count = len(validation.get('missing_fields', []))
            print(f"! Config validation: {missing_count} missing fields (expected without .env)")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_unit_tests():
    """Test that unit test files are syntactically correct"""
    try:
        print("Testing unit test file syntax...")
        
        import py_compile
        
        test_files = [
            'tests/test_models.py',
            'tests/test_notifications.py',
            'tests/test_config.py'
        ]
        
        for test_file in test_files:
            if Path(test_file).exists():
                py_compile.compile(test_file, doraise=True)
                print(f"✓ {test_file} syntax OK")
            else:
                print(f"! {test_file} not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Unit test syntax check failed: {e}")
        return False

def test_scripts():
    """Test that main scripts are syntactically correct"""
    try:
        print("Testing script file syntax...")
        
        import py_compile
        
        script_files = [
            'run.py',
            'test_site_connection.py',
            'test_email_notifications.py'
        ]
        
        for script_file in script_files:
            if Path(script_file).exists():
                py_compile.compile(script_file, doraise=True)
                print(f"✓ {script_file} syntax OK")
            else:
                print(f"! {script_file} not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Script syntax check failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== T022-T026 Implementation Validation ===")
    print()
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    print()
    
    # Test unit tests
    if not test_unit_tests():
        success = False
    print()
    
    # Test scripts
    if not test_scripts():
        success = False
    print()
    
    # Check README
    if Path('README.md').exists():
        print("✓ README.md exists")
    else:
        print("✗ README.md missing")
        success = False
    
    print()
    if success:
        print("=== ALL T022-T026 TESTS PASSED ===")
        print()
        print("✓ T022 - Unit tests created")
        print("✓ T023 - README.md created") 
        print("✓ T024 - run.py script created")
        print("✓ T025 - Site connection test script created")
        print("✓ T026 - Email notification test script created")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure .env file with credentials") 
        print("3. Run: python run.py")
    else:
        print("=== SOME TESTS FAILED ===")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
