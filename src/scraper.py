"""
Web scraping service for asylum appointment booking bot.

Uses Playwright with advanced stealth capabilities to interact with the Spanish government website:
https://icp.administracionelectronica.gob.es

Features:
- Advanced browser stealth and fingerprint randomization
- Human behavior simulation
- Automated browser management
- Madrid office detection
- Appointment slot parsing
- Form interaction simulation
- Error handling and recovery
"""

import asyncio
import logging
import random
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re
from urllib.parse import urljoin, urlparse
import json

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

# Import stealth modules
try:
    from .stealth.browser_stealth import BrowserStealth
    from .stealth.behavior_simulator import BehaviorSimulator
    STEALTH_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import path
        import sys
        import os
        stealth_path = os.path.join(os.path.dirname(__file__), 'stealth')
        if stealth_path not in sys.path:
            sys.path.insert(0, stealth_path)
        from browser_stealth import BrowserStealth
        from behavior_simulator import BehaviorSimulator
        STEALTH_AVAILABLE = True
    except ImportError:
        STEALTH_AVAILABLE = False
        logging.warning("Stealth modules not available - using basic stealth only")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SiteScrapingError(Exception):
    """Custom exception for site scraping errors"""
    pass

class AppointmentScraper:
    """Playwright-based scraper with advanced stealth capabilities for Spanish government appointment site"""
    
    def __init__(self, base_url: str = "https://icp.administracionelectronica.gob.es", 
                 headless: bool = True, enable_stealth: bool = True):
        """
        Initialize the scraper with stealth capabilities
        
        Args:
            base_url: Base URL of the government site
            headless: Whether to run browser in headless mode
            enable_stealth: Whether to enable advanced stealth features
        """
        self.base_url = base_url
        self.headless = headless
        self.enable_stealth = enable_stealth
        self.browser = None
        self.context = None
        self.page = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize stealth modules
        if STEALTH_AVAILABLE and enable_stealth:
            self.browser_stealth = BrowserStealth()
            self.behavior_simulator = BehaviorSimulator()
            self.logger.info("Advanced stealth capabilities enabled")
        else:
            self.browser_stealth = None
            self.behavior_simulator = None
            self.logger.info("Using basic stealth capabilities only")
        
        # Enhanced browser configuration for maximum stealth
        self.browser_launch_config = {
            'headless': headless,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Faster loading
                '--disable-javascript-harmony-shipping',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--disable-translate',
                '--hide-scrollbars',
                '--mute-audio',
                '--no-default-browser-check',
                '--no-pings',
                '--disable-default-apps',
                '--disable-background-networking',
                '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                '--disable-ipc-flooding-protection',
                '--disable-breakpad',
                '--disable-component-extensions-with-background-pages',
                '--disable-extensions-http-throttling',
                '--disable-field-trial-config'
            ]
        }
        
        # Dynamic browser context configuration (will be randomized)
        self.browser_context_config = None  # Will be set by stealth module
        
        # Timeouts and delays
        self.page_timeout = 45000  # Increased for stealth delays
        self.element_timeout = 15000  # Increased timeout
        self.navigation_delay = 2000  # Base navigation delay
        
        self.logger.info(f"AppointmentScraper initialized for {base_url} (stealth: {enable_stealth})")
    
    async def start_browser(self) -> bool:
        """
        Start Playwright browser with advanced stealth capabilities
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("Starting Playwright with stealth capabilities...")
            playwright = await async_playwright().start()
            
            # Launch browser with enhanced stealth configuration
            self.logger.info("Launching browser with stealth arguments...")
            self.browser = await playwright.chromium.launch(**self.browser_launch_config)
            
            # Generate stealth profile if available
            if self.browser_stealth:
                self.logger.info("Generating randomized stealth profile...")
                stealth_profile = self.browser_stealth.generate_stealth_profile()
                
                # Create context with stealth profile
                self.browser_context_config = {
                    'viewport': stealth_profile.viewport,
                    'user_agent': stealth_profile.user_agent,
                    'locale': stealth_profile.locale,
                    'timezone_id': stealth_profile.timezone,
                    'extra_http_headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': stealth_profile.locale,
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Cache-Control': 'no-cache',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': f'"{stealth_profile.platform}"'
                    },
                    'ignore_https_errors': True,
                    'java_script_enabled': True
                }
            else:
                # Fallback configuration
                self.browser_context_config = {
                    'viewport': {'width': 1366, 'height': 768},
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'extra_http_headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                }
            
            # Create browser context
            self.logger.info("Creating browser context with stealth configuration...")
            self.context = await self.browser.new_context(**self.browser_context_config)
            
            # Apply stealth measures to context
            if self.browser_stealth:
                await self.browser_stealth.apply_stealth_to_context(self.context)
            
            # Create new page
            self.logger.info("Creating new page...")
            self.page = await self.context.new_page()
            
            # Apply page-level stealth measures
            if self.browser_stealth:
                await self.browser_stealth.apply_stealth_to_page(self.page)
            
            # Set timeouts
            self.page.set_default_timeout(self.page_timeout)
            self.page.set_default_navigation_timeout(self.page_timeout)
            
            # Add request interceptor for additional stealth
            await self._setup_request_interceptor()
            
            self.logger.info("Browser started successfully with stealth capabilities")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            return False
    
    async def stop_browser(self):
        """Stop browser and cleanup resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
                
            self.page = None
            self.context = None
            self.browser = None
            
            self.logger.info("Browser stopped successfully")
            
        except Exception as e:
            self.logger.warning(f"Error stopping browser: {e}")
    
    async def _setup_request_interceptor(self) -> None:
        """Setup request interceptor for additional stealth measures"""
        try:
            async def handle_request(request):
                # Block unnecessary requests to improve stealth and speed
                resource_type = request.resource_type
                if resource_type in ['image', 'media', 'font', 'stylesheet']:
                    await request.abort()
                else:
                    # Add random delays to requests
                    if random.random() < 0.3:  # 30% of requests
                        await asyncio.sleep(random.uniform(0.1, 0.5))
                    await request.continue_()
            
            await self.page.route('**/*', handle_request)
            self.logger.debug("Request interceptor configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup request interceptor: {e}")

    async def navigate_to_site(self) -> bool:
        """
        Navigate to the main government site with enhanced stealth
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            if not self.page:
                if not await self.start_browser():
                    return False
            
            self.logger.info(f"Navigating to {self.base_url} with stealth...")
            
            # Pre-navigation behavior simulation
            if self.behavior_simulator:
                await asyncio.sleep(random.uniform(1.0, 3.0))  # Initial delay
            
            # Navigate to main page with enhanced error handling
            response = await self.page.goto(
                self.base_url, 
                wait_until='domcontentloaded',
                timeout=self.page_timeout
            )
            
            # Check response status
            if response:
                status = response.status
                self.logger.info(f"Navigation response status: {status}")
                
                if status == 200:
                    self.logger.info("✅ Successfully navigated to government site")
                    
                    # Simulate human behavior after navigation
                    if self.behavior_simulator:
                        await self.behavior_simulator.simulate_navigation_delay(self.page)
                        await self.behavior_simulator.simulate_page_reading(self.page, 2.0, 5.0)
                    else:
                        # Basic delay fallback
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                    
                    return True
                    
                elif status == 403:
                    self.logger.error("🚫 403 Forbidden - Site is blocking requests")
                    self.logger.info("� Attempting stealth countermeasures...")
                    
                    # Try stealth countermeasures
                    return await self._handle_403_error()
                    
                elif status == 503:
                    self.logger.error("⏸️ 503 Service Unavailable - Site under maintenance")
                    return False
                    
                elif status in [429, 509]:
                    self.logger.error(f"⏱️ {status} Rate Limited - Too many requests")
                    self.logger.info("⏳ Implementing backoff strategy...")
                    await asyncio.sleep(random.uniform(30, 60))
                    return False
                    
                else:
                    self.logger.error(f"❌ Navigation failed with status: {status}")
                    return False
                    
            else:
                self.logger.error("❌ Navigation failed - no response received")
                return False
                
        except PlaywrightTimeoutError:
            self.logger.error("⏱️ Navigation timeout - site may be slow or blocking")
            return await self._handle_timeout_error()
            
        except Exception as e:
            self.logger.error(f"❌ Navigation error: {e}")
            return False

    async def _handle_403_error(self) -> bool:
        """Handle 403 forbidden error with stealth countermeasures"""
        try:
            self.logger.info("🕵️ Deploying advanced stealth countermeasures...")
            
            # Wait before retry
            await asyncio.sleep(random.uniform(10, 20))
            
            if self.browser_stealth:
                # Generate new stealth profile
                new_profile = await self.browser_stealth.rotate_profile(self.context)
                self.logger.info(f"🔄 Rotated to new stealth profile")
                
                # Apply new stealth measures to current page
                await self.browser_stealth.apply_stealth_to_page(self.page, new_profile)
            
            # Add additional random delay
            await asyncio.sleep(random.uniform(5, 15))
            
            # Retry navigation with new profile
            self.logger.info("🔄 Retrying navigation with enhanced stealth...")
            response = await self.page.goto(
                self.base_url,
                wait_until='domcontentloaded', 
                timeout=self.page_timeout
            )
            
            if response and response.status == 200:
                self.logger.info("✅ Stealth countermeasures successful!")
                if self.behavior_simulator:
                    await self.behavior_simulator.simulate_navigation_delay(self.page)
                return True
            else:
                self.logger.error("❌ Stealth countermeasures failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in stealth countermeasures: {e}")
            return False

    async def _handle_timeout_error(self) -> bool:
        """Handle timeout errors with retry logic"""
        try:
            self.logger.info("⏳ Implementing timeout recovery strategy...")
            
            # Longer wait for slow connections
            await asyncio.sleep(random.uniform(15, 30))
            
            # Try with longer timeout
            self.logger.info("🔄 Retrying with extended timeout...")
            response = await self.page.goto(
                self.base_url,
                wait_until='load',  # Wait for full load instead of just DOM
                timeout=60000  # 60 second timeout
            )
            
            if response and response.status == 200:
                self.logger.info("✅ Timeout recovery successful!")
                return True
            else:
                self.logger.error("❌ Timeout recovery failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in timeout recovery: {e}")
            return False
                
        except PlaywrightTimeoutError:
            self.logger.error("Timeout while navigating to site")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to site: {e}")
            return False
    
    async def find_madrid_office_links(self) -> List[Dict[str, Any]]:
        """
        Find links and information for Madrid offices
        
        Returns:
            List of dictionaries with office information
        """
        offices = []
        
        try:
            # Common Spanish patterns for Madrid office links
            madrid_patterns = [
                r'madrid',
                r'cita.*madrid', 
                r'oficina.*madrid',
                r'extranjería.*madrid',
                r'asilo.*madrid'
            ]
            
            # Look for links containing Madrid-related terms
            for pattern in madrid_patterns:
                links = await self.page.locator(f'a:has-text("{pattern}")').all()
                
                for link in links:
                    try:
                        text = await link.text_content()
                        href = await link.get_attribute('href')
                        
                        if text and href:
                            office_info = {
                                'text': text.strip(),
                                'url': urljoin(self.base_url, href),
                                'type': 'madrid_office'
                            }
                            
                            # Try to extract office details from link text
                            office_info.update(self._parse_office_info_from_text(text))
                            offices.append(office_info)
                            
                    except Exception as e:
                        self.logger.warning(f"Error processing office link: {e}")
                        continue
            
            # Remove duplicates based on URL
            unique_offices = {office['url']: office for office in offices}.values()
            offices = list(unique_offices)
            
            self.logger.info(f"Found {len(offices)} Madrid office links")
            return offices
            
        except Exception as e:
            self.logger.error(f"Error finding Madrid office links: {e}")
            return []
    
    def _parse_office_info_from_text(self, text: str) -> Dict[str, Any]:
        """
        Parse office information from link text
        
        Args:
            text: Link text content
            
        Returns:
            Dictionary with parsed office information
        """
        info = {}
        
        # Extract office name patterns
        office_patterns = [
            r'oficina\s+(.+?)(?:\s|$)',
            r'madrid\s+(.+?)(?:\s|$)',
            r'centro\s+(.+?)(?:\s|$)'
        ]
        
        for pattern in office_patterns:
            match = re.search(pattern, text.lower())
            if match:
                info['office_name'] = match.group(1).title()
                break
        
        # Extract district information
        district_patterns = [
            r'(centro|norte|sur|este|oeste)',
            r'distrito\s+(.+?)(?:\s|$)'
        ]
        
        for pattern in district_patterns:
            match = re.search(pattern, text.lower())
            if match:
                info['district'] = match.group(1).title()
                break
        
        return info
    
    async def navigate_to_appointment_page(self, office_url: str) -> bool:
        """
        Navigate to appointment booking page for specific office
        
        Args:
            office_url: URL of the office appointment page
            
        Returns:
            bool: True if navigation successful
        """
        try:
            self.logger.info(f"Navigating to office appointment page: {office_url}")
            
            response = await self.page.goto(office_url, wait_until='networkidle')
            
            if response and response.status == 200:
                await self.page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(1)
                
                self.logger.info("Successfully navigated to appointment page")
                return True
            else:
                self.logger.error(f"Failed to navigate to appointment page: {response.status if response else 'No response'}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error navigating to appointment page: {e}")
            return False
    
    async def parse_appointment_slots(self) -> List[Dict[str, Any]]:
        """
        Parse available appointment slots from the current page
        
        Returns:
            List of appointment slot dictionaries
        """
        appointments = []
        
        try:
            # Common Spanish selectors for appointment slots
            appointment_selectors = [
                '.appointment-slot',
                '.cita-disponible',
                '.fecha-disponible',
                '.horario-disponible',
                'tr:has-text("disponible")',
                'div:has-text("cita")',
                '.calendar-day:has(.available)',
                '.time-slot.available'
            ]
            
            # Try each selector to find appointment elements
            appointment_elements = []
            for selector in appointment_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    appointment_elements.extend(elements)
                except:
                    continue
            
            # If no specific appointment elements found, look for date/time patterns
            if not appointment_elements:
                appointment_elements = await self._find_appointment_patterns()
            
            # Parse each appointment element
            for element in appointment_elements[:20]:  # Limit to first 20 to avoid overwhelming
                try:
                    appointment_data = await self._parse_appointment_element(element)
                    if appointment_data:
                        appointments.append(appointment_data)
                        
                except Exception as e:
                    self.logger.warning(f"Error parsing appointment element: {e}")
                    continue
            
            # Remove duplicates and sort by date/time
            appointments = self._deduplicate_and_sort_appointments(appointments)
            
            self.logger.info(f"Found {len(appointments)} appointment slots")
            return appointments
            
        except Exception as e:
            self.logger.error(f"Error parsing appointment slots: {e}")
            return []
    
    async def _find_appointment_patterns(self) -> List:
        """Find appointment slots using date/time patterns"""
        elements = []
        
        try:
            # Look for Spanish date patterns
            date_patterns = [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # DD/MM/YYYY or DD-MM-YYYY
                r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',  # DD de MONTH de YYYY
                r'(lunes|martes|miércoles|jueves|viernes|sábado|domingo)',  # Weekdays
            ]
            
            # Look for time patterns
            time_patterns = [
                r'\d{1,2}:\d{2}',  # HH:MM
                r'\d{1,2}h\d{2}',  # HHhMM
            ]
            
            # Combine patterns to find elements with both date and time
            combined_pattern = f"({'|'.join(date_patterns)}).*({'|'.join(time_patterns)})"
            
            text_elements = await self.page.locator(f'text=/{combined_pattern}/').all()
            elements.extend(text_elements)
            
        except Exception as e:
            self.logger.warning(f"Error finding appointment patterns: {e}")
        
        return elements
    
    async def _parse_appointment_element(self, element) -> Optional[Dict[str, Any]]:
        """
        Parse individual appointment element
        
        Args:
            element: Playwright element containing appointment info
            
        Returns:
            Dictionary with appointment data or None
        """
        try:
            text_content = await element.text_content()
            if not text_content:
                return None
            
            # Extract date
            appointment_date = self._extract_date_from_text(text_content)
            
            # Extract time
            appointment_time = self._extract_time_from_text(text_content)
            
            # Only return if we found both date and time
            if appointment_date and appointment_time:
                return {
                    'date': appointment_date,
                    'time': appointment_time,
                    'available': True,
                    'raw_text': text_content.strip(),
                    'source_element': 'parsed'
                }
            
        except Exception as e:
            self.logger.warning(f"Error parsing appointment element: {e}")
        
        return None
    
    def _extract_date_from_text(self, text: str) -> Optional[date]:
        """Extract date from text using Spanish patterns"""
        try:
            # Pattern 1: DD/MM/YYYY or DD-MM-YYYY
            date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', text)
            if date_match:
                day, month, year = map(int, date_match.groups())
                return date(year, month, day)
            
            # Pattern 2: DD de MONTH de YYYY
            spanish_months = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            
            month_pattern = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
            month_match = re.search(month_pattern, text.lower())
            if month_match:
                day = int(month_match.group(1))
                month_name = month_match.group(2)
                year = int(month_match.group(3))
                
                if month_name in spanish_months:
                    month = spanish_months[month_name]
                    return date(year, month, day)
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Error parsing date from text '{text}': {e}")
        
        return None
    
    def _extract_time_from_text(self, text: str) -> Optional[time]:
        """Extract time from text using various patterns"""
        try:
            # Pattern 1: HH:MM
            time_match = re.search(r'(\d{1,2}):(\d{2})', text)
            if time_match:
                hour, minute = map(int, time_match.groups())
                return time(hour, minute)
            
            # Pattern 2: HHhMM
            time_match = re.search(r'(\d{1,2})h(\d{2})', text)
            if time_match:
                hour, minute = map(int, time_match.groups())
                return time(hour, minute)
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Error parsing time from text '{text}': {e}")
        
        return None
    
    def _deduplicate_and_sort_appointments(self, appointments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and sort appointments by datetime"""
        try:
            # Remove duplicates based on date and time
            unique_appointments = {}
            for apt in appointments:
                key = (apt['date'], apt['time'])
                if key not in unique_appointments:
                    unique_appointments[key] = apt
            
            # Sort by date and time
            sorted_appointments = sorted(
                unique_appointments.values(),
                key=lambda x: datetime.combine(x['date'], x['time'])
            )
            
            return sorted_appointments
            
        except Exception as e:
            self.logger.warning(f"Error sorting appointments: {e}")
            return appointments
    
    async def simulate_booking_attempt(self, appointment_data: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate booking attempt (MVP safety feature)
        
        Args:
            appointment_data: Dictionary with appointment details
            user_data: Dictionary with user information
            
        Returns:
            Dictionary with booking result
        """
        try:
            self.logger.info("Simulating booking attempt (DRY RUN MODE)")
            
            # Simulate form interaction
            await asyncio.sleep(2)  # Simulate processing time
            
            # Generate mock confirmation code
            confirmation_code = f"DRY_RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            result = {
                'success': True,
                'dry_run': True,
                'confirmation_code': confirmation_code,
                'appointment_date': appointment_data.get('date'),
                'appointment_time': appointment_data.get('time'),
                'office_name': 'Madrid Centro',  # Mock office name
                'office_address': 'Calle de la Montera, 20, 28013 Madrid',
                'user_name': user_data.get('name', 'Test User'),
                'user_email': user_data.get('email', 'test@example.com'),
                'passport_number': user_data.get('passport_number', 'A12345678'),
                'booking_timestamp': datetime.now().isoformat(),
                'message': 'Booking simulation completed successfully (no actual booking made)'
            }
            
            self.logger.info(f"Booking simulation completed: {confirmation_code}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in booking simulation: {e}")
            return {
                'success': False,
                'dry_run': True,
                'error_type': 'simulation_error',
                'error_message': str(e),
                'booking_timestamp': datetime.now().isoformat()
            }
    
    async def check_site_availability(self) -> Dict[str, Any]:
        """
        Check if the government site is available and accessible
        
        Returns:
            Dictionary with availability status
        """
        result = {
            'available': False,
            'status_code': None,
            'response_time_ms': None,
            'error_message': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            start_time = datetime.now()
            
            # Try to navigate to the site
            success = await self.navigate_to_site()
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            if success:
                result['available'] = True
                result['status_code'] = 200
                result['response_time_ms'] = int(response_time)
                self.logger.info(f"Site is available (response time: {response_time:.0f}ms)")
            else:
                result['error_message'] = 'Failed to navigate to site'
                self.logger.warning("Site is not available")
                
        except Exception as e:
            result['error_message'] = str(e)
            self.logger.error(f"Error checking site availability: {e}")
        
        return result
    
    async def get_page_content(self) -> str:
        """Get current page content for debugging"""
        try:
            if self.page:
                return await self.page.content()
        except Exception as e:
            self.logger.error(f"Error getting page content: {e}")
        
        return ""

class ScrapingService:
    """High-level scraping service for asylum appointment monitoring"""
    
    def __init__(self, base_url: str = "https://icp.administracionelectronica.gob.es", headless: bool = True):
        """
        Initialize scraping service
        
        Args:
            base_url: Base URL of the government site
            headless: Whether to run browser in headless mode
        """
        self.scraper = AppointmentScraper(base_url, headless)
        self.logger = logging.getLogger(__name__)
    
    async def monitor_madrid_offices(self) -> Dict[str, Any]:
        """
        Monitor all Madrid offices for available appointments
        
        Returns:
            Dictionary with monitoring results
        """
        result = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'offices_checked': 0,
            'appointments_found': 0,
            'appointments': [],
            'errors': []
        }
        
        try:
            # Check site availability first
            availability = await self.scraper.check_site_availability()
            if not availability['available']:
                result['errors'].append('Government site is not available')
                return result
            
            # Find Madrid office links
            offices = await self.scraper.find_madrid_office_links()
            result['offices_checked'] = len(offices)
            
            if not offices:
                result['errors'].append('No Madrid office links found')
                return result
            
            # Check each office for appointments
            for office in offices[:3]:  # Limit to first 3 offices for MVP
                try:
                    # Navigate to office appointment page
                    if await self.scraper.navigate_to_appointment_page(office['url']):
                        # Parse appointment slots
                        appointments = await self.scraper.parse_appointment_slots()
                        
                        # Add office info to each appointment
                        for appointment in appointments:
                            appointment['office_info'] = office
                            result['appointments'].append(appointment)
                        
                        result['appointments_found'] += len(appointments)
                        
                except Exception as e:
                    self.logger.warning(f"Error checking office {office.get('text', 'Unknown')}: {e}")
                    result['errors'].append(f"Office check error: {str(e)}")
                    continue
            
            result['success'] = True
            self.logger.info(f"Monitoring completed: {result['appointments_found']} appointments found across {result['offices_checked']} offices")
            
        except Exception as e:
            self.logger.error(f"Error in monitoring: {e}")
            result['errors'].append(f"Monitoring error: {str(e)}")
        
        finally:
            # Always cleanup browser resources
            await self.scraper.stop_browser()
        
        return result
    
    async def attempt_booking(self, appointment_data: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to book an appointment (simulation for MVP)
        
        Args:
            appointment_data: Dictionary with appointment details
            user_data: Dictionary with user information
            
        Returns:
            Dictionary with booking result
        """
        try:
            # Ensure browser is running
            if not self.scraper.page:
                await self.scraper.start_browser()
            
            # Simulate booking attempt
            result = await self.scraper.simulate_booking_attempt(appointment_data, user_data)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in booking attempt: {e}")
            return {
                'success': False,
                'dry_run': True,
                'error_type': 'booking_error',
                'error_message': str(e),
                'booking_timestamp': datetime.now().isoformat()
            }
        
        finally:
            await self.scraper.stop_browser()
    
    async def cleanup(self):
        """Cleanup scraping resources"""
        await self.scraper.stop_browser()
