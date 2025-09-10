#!/usr/bin/env python3
"""
Enhanced stealth test for the government website.
Tests the new stealth capabilities against 403 blocking.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def setup_logging():
    """Setup enhanced logging for stealth testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

async def test_stealth_capabilities():
    """Test enhanced stealth capabilities against government site"""
    logger = setup_logging()
    
    print("""
===============================================================================

    🕵️ Enhanced Stealth Test - Asylum Appointment Bot

    Testing advanced stealth capabilities to bypass 403 blocking:
    • Browser fingerprint randomization
    • Human behavior simulation  
    • Advanced request patterns
    • Anti-detection measures

===============================================================================
""")
    
    try:
        logger.info("🚀 Starting enhanced stealth test...")
        
        # Import enhanced scraper
        from scraper import AppointmentScraper
        
        # Create scraper with stealth enabled
        logger.info("🕵️ Initializing scraper with maximum stealth...")
        scraper = AppointmentScraper(enable_stealth=True, headless=True)
        
        # Test 1: Browser startup with stealth
        logger.info("🌐 Testing stealth browser startup...")
        browser_started = await scraper.start_browser()
        if not browser_started:
            logger.error("❌ Failed to start stealth browser")
            return False
        logger.info("✅ Stealth browser started successfully")
        
        # Test 2: Navigation with stealth countermeasures
        logger.info("🔗 Testing stealth navigation to government site...")
        navigation_success = await scraper.navigate_to_site()
        
        if navigation_success:
            logger.info("🎉 SUCCESS! Stealth navigation bypassed blocking!")
            
            # Test 3: Page interaction with human behavior
            logger.info("🤖 Testing human behavior simulation...")
            if scraper.behavior_simulator:
                await scraper.behavior_simulator.simulate_page_reading(scraper.page, 3.0, 6.0)
                await scraper.behavior_simulator.random_page_interaction(scraper.page)
                logger.info("✅ Human behavior simulation completed")
            
            # Test 4: Get page information
            try:
                page_title = await scraper.page.title()
                page_url = scraper.page.url
                logger.info(f"📄 Page Title: {page_title}")
                logger.info(f"🔗 Current URL: {page_url}")
                
                # Check if we can access page content
                content_length = len(await scraper.page.content())
                logger.info(f"📊 Page Content Length: {content_length} characters")
                
                if content_length > 1000:  # Reasonable page content
                    logger.info("✅ Successfully accessed page content")
                else:
                    logger.warning("⚠️ Page content seems limited")
                    
            except Exception as e:
                logger.error(f"❌ Error accessing page content: {e}")
        
        else:
            logger.error("❌ Stealth navigation failed - site is still blocking")
            logger.info("💡 This indicates very strong anti-bot measures")
            logger.info("💡 May need additional stealth techniques:")
            logger.info("   • Residential proxy rotation")
            logger.info("   • CAPTCHA solving integration")
            logger.info("   • More advanced timing patterns")
        
        # Cleanup
        await scraper.stop_browser()
        logger.info("🧹 Browser cleaned up")
        
        return navigation_success
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 Make sure stealth modules are available")
        return False
    
    except Exception as e:
        logger.error(f"❌ Stealth test failed: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_stealth_capabilities()
    
    if success:
        print("\n🎉 STEALTH TEST PASSED!")
        print("✅ Advanced stealth capabilities are working")
        print("💡 The bot can now access the government website")
        print("💡 Ready for appointment monitoring with stealth mode")
    else:
        print("\n⚠️ STEALTH TEST NEEDS IMPROVEMENT")
        print("❌ Still experiencing blocking - need additional measures")
        print("💡 Consider implementing:")
        print("   • Proxy rotation")
        print("   • CAPTCHA solving")
        print("   • More advanced fingerprint randomization")

if __name__ == "__main__":
    asyncio.run(main())
