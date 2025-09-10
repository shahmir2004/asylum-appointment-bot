#!/usr/bin/env python3
"""
Test runner for the backend contract tests.
This script runs the T004-T007 contract tests and verifies they fail (TDD).
"""
import subprocess
import sys
import os

def run_contract_tests():
    """Run the contract tests for authentication endpoints."""
    print("🧪 Running Contract Tests for Authentication Endpoints (T004-T007)")
    print("=" * 70)
    print("⚠️  These tests MUST FAIL initially as per TDD methodology")
    print("✅ Endpoints are not implemented yet - failures are expected!")
    print()
    
    # Ensure we're in the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Test files to run
    test_files = [
        "tests/contract/test_auth_login.py",
        "tests/contract/test_auth_refresh.py", 
        "tests/contract/test_auth_me.py",
        "tests/contract/test_auth_logout.py"
    ]
    
    # Run each test file
    total_tests = 0
    total_failures = 0
    
    for test_file in test_files:
        print(f"📋 Running {test_file}")
        print("-" * 50)
        
        try:
            # Run pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file,
                "-v",
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Count tests and failures
            lines = result.stdout.split('\n')
            for line in lines:
                if "failed" in line and "passed" in line:
                    # Parse pytest summary line
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed,":
                            total_failures += int(parts[i-1])
                        elif part == "passed":
                            total_tests += int(parts[i-1]) + total_failures
                elif "failed" in line and "error" in line:
                    # Handle error cases
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed":
                            total_failures += int(parts[i-1])
                            total_tests += int(parts[i-1])
            
            print()
            
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            print()
    
    # Summary
    print("=" * 70)
    print("📊 CONTRACT TESTS SUMMARY (T004-T007)")
    print("=" * 70)
    print(f"📝 Total Tests: {total_tests}")
    print(f"❌ Expected Failures: {total_failures}")
    print(f"✅ Expected Passes: {total_tests - total_failures}")
    print()
    
    if total_failures > 0:
        print("🎉 SUCCESS: Contract tests are failing as expected!")
        print("   This confirms TDD approach - tests written before implementation.")
        print("   Next: Implement authentication endpoints to make tests pass.")
    else:
        print("⚠️  WARNING: Some tests passed unexpectedly.")
        print("   This might indicate endpoints already exist or tests need refinement.")
    
    print()
    print("📋 NEXT STEPS:")
    print("1. Implement T008-T011 (Database models)")
    print("2. Implement T012-T019 (Authentication implementation)")  
    print("3. Re-run these tests to verify they pass")
    print("4. Continue with T020-T033 (Bot control API)")


if __name__ == "__main__":
    run_contract_tests()
