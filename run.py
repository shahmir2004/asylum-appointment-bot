#!/usr/bin/env python3
"""
Simple startup script for Asylum Appointment Booking Bot

This script provides an easy way to start the bot with python run.py
Handles initialization, validation, and graceful startup.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def setup_logging():
    """Setup basic logging for startup script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def print_banner():
    """Print bot startup banner"""
    banner = """
===============================================================================
                                                                
    🤖 Asylum Appointment Booking Bot (MVP)                    
                                                                
    Automated monitoring for asylum appointments in Madrid     
    Built with Python + Playwright + Safety First Design      
                                                                
===============================================================================
"""
    print(banner)

def check_requirements():
    """Check that basic requirements are met"""
    logger = logging.getLogger(__name__)
    
    # Check Python version
    if sys.version_info < (3, 11):
        logger.error("❌ Python 3.11+ required. Current version: %s", sys.version)
        return False
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("⚠️ No .env file found. Using environment variables or defaults.")
        logger.info("💡 Create a .env file with your configuration for best results.")
    
    # Check if src directory exists
    src_dir = Path('src')
    if not src_dir.exists():
        logger.error("❌ src/ directory not found. Run from project root directory.")
        return False
    
    # Check essential modules can be imported
    try:
        from config import Config
        from main import AsylumBot
        logger.info("✅ Core modules imported successfully")
    except ImportError as e:
        logger.error("❌ Failed to import core modules: %s", e)
        logger.error("💡 Install dependencies with: pip install -r requirements.txt")
        return False
    
    return True

def validate_configuration():
    """Validate bot configuration"""
    logger = logging.getLogger(__name__)
    
    try:
        from config import Config
        config = Config.from_env()
        validation = config.validate()
        
        if validation['valid']:
            logger.info("✅ Configuration validation passed")
            
            # Show warnings if any
            for warning in validation['warnings']:
                logger.warning("⚠️ %s", warning)
            
            return True
        else:
            logger.error("❌ Configuration validation failed")
            if 'errors' in validation and validation['errors']:
                logger.error("Validation errors:")
                for error in validation['errors']:
                    logger.error("  • %s", error)
            logger.error("💡 Check your .env file or environment variables")
            return False
            
    except Exception as e:
        logger.error("❌ Configuration validation error: %s", e)
        return False

def show_startup_info():
    """Show important startup information"""
    logger = logging.getLogger(__name__)
    
    try:
        from config import Config
        config = Config.from_env()
        
        logger.info("🔧 Configuration Summary:")
        logger.info("   📧 Email: %s", config.gmail_username)
        logger.info("   👤 User: %s", config.default_user_name)
        logger.info("   ⏱️ Monitoring Interval: %ds", config.monitoring_interval)
        logger.info("   🛡️ Dry Run Mode: %s", "ENABLED" if config.dry_run_mode else "DISABLED")
        logger.info("   🎯 Auto Booking: %s", "ENABLED" if config.auto_booking_enabled else "DISABLED")
        logger.info("")
        
        if config.dry_run_mode:
            logger.info("🛡️ SAFETY MODE: Booking attempts will be simulated only")
        else:
            logger.warning("⚠️ LIVE MODE: Real booking attempts will be made!")
        
        logger.info("")
        logger.info("💡 Press Ctrl+C to stop the bot gracefully")
        logger.info("📁 Logs will be saved to: %s", config.log_file)
        logger.info("")
        
    except Exception as e:
        logger.error("❌ Error displaying startup info: %s", e)

async def main():
    """Main startup function"""
    logger = setup_logging()
    
    try:
        # Show banner
        print_banner()
        
        # Check requirements
        logger.info("🔍 Checking requirements...")
        if not check_requirements():
            logger.error("❌ Requirements check failed. Exiting.")
            sys.exit(1)
        
        # Validate configuration
        logger.info("🔧 Validating configuration...")
        if not validate_configuration():
            logger.error("❌ Configuration validation failed. Exiting.")
            logger.error("💡 Run 'python -m src.cli config --validate' for detailed information")
            sys.exit(1)
        
        # Show startup information
        show_startup_info()
        
        # Initialize and start bot
        logger.info("🚀 Initializing bot...")
        from main import AsylumBot
        
        bot = AsylumBot.from_env()
        await bot.initialize()
        
        logger.info("🎯 Starting monitoring...")
        await bot.run_continuous_monitoring()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
        logger.info("👋 Goodbye!")
        
    except Exception as e:
        logger.error("💥 Fatal error: %s", e)
        logger.error("💡 Check logs for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure we're running from the correct directory
    script_dir = Path(__file__).parent
    if Path.cwd() != script_dir:
        print(f"🔄 Changing to script directory: {script_dir}")
        os.chdir(script_dir)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted during startup")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Startup error: {e}")
        sys.exit(1)
