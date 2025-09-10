#!/usr/bin/env python3
"""
Simple configuration test script
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_configuration():
    """Test configuration loading and validation"""
    print("🔧 Testing Configuration...")
    
    try:
        from config import Config
        
        # Load configuration
        config = Config.from_env()
        print("✅ Configuration loaded successfully")
        
        # Validate configuration
        validation = config.validate()
        
        if validation['valid']:
            print("✅ Configuration validation passed!")
            
            # Show configuration summary
            print("\n📋 Configuration Summary:")
            print(f"   📧 Gmail Username: {config.gmail_username}")
            print(f"   📧 Recipient Email: {config.recipient_email}")
            print(f"   🌐 Site URL: {config.site_url}")
            print(f"   ⏱️ Monitoring Interval: {config.monitoring_interval}s")
            print(f"   🛡️ Dry Run Mode: {config.dry_run_mode}")
            print(f"   🎯 Auto Booking: {config.auto_booking_enabled}")
            print(f"   🖥️ Headless Browser: {config.headless_browser}")
            
            # Show warnings
            if validation['warnings']:
                print("\n⚠️ Warnings:")
                for warning in validation['warnings']:
                    print(f"   • {warning}")
            else:
                print("\n✅ No warnings")
                
        else:
            print("❌ Configuration validation failed!")
            if validation['errors']:
                print("\n🚨 Errors:")
                for error in validation['errors']:
                    print(f"   • {error}")
            
        return validation['valid']
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_configuration()
    if success:
        print("\n🎉 Configuration is ready!")
        print("💡 You can now run: python run.py")
    else:
        print("\n💥 Configuration needs fixing")
        print("💡 Check your .env file")
        sys.exit(1)
