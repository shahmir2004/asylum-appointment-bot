"""
Appointment booking logic for asylum appointment booking bot.

Handles the complete booking workflow:
- Appointment validation
- Form filling and submission  
- Confirmation extraction
- Error handling and retries
- Dry run mode for MVP safety
"""

import asyncio
import logging
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Any
import json
import secrets
import string
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BookingConfig:
    """Configuration for booking service"""
    dry_run_mode: bool = True  # MVP safety flag
    max_retries: int = 3
    retry_delay: float = 5.0
    booking_timeout: int = 30
    max_booking_attempts: int = 5
    error_recovery_enabled: bool = True

class BookingError(Exception):
    """Custom exception for booking-related errors"""
    def __init__(self, message: str, error_type: str = "general", retry_recommended: bool = True):
        super().__init__(message)
        self.error_type = error_type
        self.retry_recommended = retry_recommended

class BookingService:
    """Service for handling appointment booking operations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize booking service
        
        Args:
            config: Configuration dictionary
        """
        self.config = BookingConfig()
        if config:
            # Update config from provided dictionary
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        self.logger = logging.getLogger(__name__)
        self.session_data = {}
        self.booking_history = []
        
        # MVP properties
        self.dry_run_mode = self.config.dry_run_mode
        self.max_retries = self.config.max_retries
        self.retry_delay = self.config.retry_delay
        
        self.logger.info(f"BookingService initialized (dry_run_mode: {self.dry_run_mode})")
    
    @classmethod
    def from_env(cls) -> 'BookingService':
        """Create BookingService from environment variables"""
        import os
        
        config = {
            'dry_run_mode': os.getenv('TEST_MODE', 'true').lower() == 'true',
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'retry_delay': float(os.getenv('RETRY_DELAY', '5.0')),
            'booking_timeout': int(os.getenv('BOOKING_TIMEOUT', '30'))
        }
        
        return cls(config)
    
    def validate_appointment(self, appointment_data: Dict[str, Any]) -> bool:
        """
        Validate appointment data before booking attempt
        
        Args:
            appointment_data: Dictionary with appointment details
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            required_fields = ['date', 'time', 'office_code']
            
            # Check required fields
            for field in required_fields:
                if field not in appointment_data:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate date
            appointment_date = appointment_data['date']
            if isinstance(appointment_date, str):
                try:
                    appointment_date = datetime.fromisoformat(appointment_date).date()
                except ValueError:
                    self.logger.error(f"Invalid date format: {appointment_date}")
                    return False
            
            if not isinstance(appointment_date, date):
                self.logger.error(f"Invalid date type: {type(appointment_date)}")
                return False
            
            # Check if date is in the future
            if appointment_date <= date.today():
                self.logger.error(f"Appointment date must be in the future: {appointment_date}")
                return False
            
            # Validate time
            appointment_time = appointment_data['time']
            if isinstance(appointment_time, str):
                try:
                    appointment_time = datetime.fromisoformat(f"2000-01-01T{appointment_time}").time()
                except ValueError:
                    self.logger.error(f"Invalid time format: {appointment_time}")
                    return False
            
            if not isinstance(appointment_time, time):
                self.logger.error(f"Invalid time type: {type(appointment_time)}")
                return False
            
            # Validate office code
            office_code = appointment_data['office_code']
            if not office_code or not isinstance(office_code, str):
                self.logger.error(f"Invalid office code: {office_code}")
                return False
            
            self.logger.info("Appointment data validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating appointment data: {e}")
            return False
    
    async def attempt_booking(self, appointment_data: Dict[str, Any], user_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to book an appointment
        
        Args:
            appointment_data: Dictionary with appointment details
            user_credentials: Dictionary with user information
            
        Returns:
            Dictionary with booking result
        """
        result = {
            'success': False,
            'dry_run': self.dry_run_mode,
            'timestamp': datetime.now().isoformat(),
            'appointment_data': appointment_data,
            'error_type': None,
            'error_message': None
        }
        
        try:
            # Validate appointment data
            if not self.validate_appointment(appointment_data):
                result['error_type'] = 'validation_error'
                result['error_message'] = 'Appointment data validation failed'
                return result
            
            # Create booking session
            session = await self.create_booking_session()
            result['session_id'] = session['session_id']
            
            if self.dry_run_mode:
                # Simulate booking in dry run mode
                booking_result = await self._simulate_booking(appointment_data, user_credentials)
            else:
                # Actual booking (not implemented in MVP for safety)
                booking_result = await self._perform_actual_booking(appointment_data, user_credentials)
            
            result.update(booking_result)
            
            # Save booking attempt to history
            self.booking_history.append(result.copy())
            
            return result
            
        except BookingError as e:
            result['error_type'] = e.error_type
            result['error_message'] = str(e)
            result['retry_recommended'] = e.retry_recommended
            self.logger.error(f"Booking error: {e}")
            return result
            
        except Exception as e:
            result['error_type'] = 'unexpected_error'
            result['error_message'] = str(e)
            self.logger.error(f"Unexpected booking error: {e}")
            return result
        
        finally:
            # Close session if it was created
            if 'session_id' in result:
                await self.close_booking_session(result['session_id'])
    
    async def _simulate_booking(self, appointment_data: Dict[str, Any], user_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate booking process for MVP safety
        
        Args:
            appointment_data: Dictionary with appointment details
            user_credentials: Dictionary with user information
            
        Returns:
            Dictionary with simulation result
        """
        self.logger.info("Starting booking simulation (DRY RUN)")
        
        try:
            # Simulate navigation to booking form
            await asyncio.sleep(1)  # Simulate network delay
            
            # Simulate form validation
            if not await self._validate_booking_form_data(user_credentials):
                raise BookingError("Form validation failed", "form_validation_error")
            
            # Simulate form filling
            await asyncio.sleep(2)  # Simulate form filling time
            
            # Simulate form submission
            await asyncio.sleep(1)  # Simulate submission time
            
            # Generate mock confirmation
            confirmation_code = self.generate_dry_run_confirmation()
            
            result = {
                'success': True,
                'confirmation_code': confirmation_code,
                'appointment_date': appointment_data['date'],
                'appointment_time': appointment_data['time'],
                'office_name': self._get_office_name(appointment_data.get('office_code', 'MAD001')),
                'office_address': self._get_office_address(appointment_data.get('office_code', 'MAD001')),
                'office_phone': self._get_office_phone(appointment_data.get('office_code', 'MAD001')),
                'user_name': user_credentials.get('name', 'Test User'),
                'user_email': user_credentials.get('email', 'test@example.com'),
                'passport_number': user_credentials.get('passport_number', 'A12345678'),
                'booking_timestamp': datetime.now().isoformat(),
                'simulation_duration_ms': 4000,  # Mock duration
                'message': 'Booking simulation completed successfully (no actual booking made)'
            }
            
            self.logger.info(f"Booking simulation completed: {confirmation_code}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in booking simulation: {e}")
            raise BookingError(f"Simulation failed: {str(e)}", "simulation_error")
    
    async def _perform_actual_booking(self, appointment_data: Dict[str, Any], user_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform actual booking (not implemented in MVP for safety)
        
        Args:
            appointment_data: Dictionary with appointment details
            user_credentials: Dictionary with user information
            
        Returns:
            Dictionary with booking result
        """
        self.logger.warning("Actual booking not implemented in MVP for safety")
        
        # For MVP, redirect to simulation
        return await self._simulate_booking(appointment_data, user_credentials)
    
    async def _validate_booking_form_data(self, user_credentials: Dict[str, Any]) -> bool:
        """
        Validate user credentials for booking form
        
        Args:
            user_credentials: Dictionary with user information
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['name', 'email', 'nationality', 'passport_number']
        
        for field in required_fields:
            if field not in user_credentials or not user_credentials[field]:
                self.logger.error(f"Missing required user field: {field}")
                return False
        
        # Validate email format (basic)
        email = user_credentials['email']
        if '@' not in email or '.' not in email:
            self.logger.error(f"Invalid email format: {email}")
            return False
        
        # Validate passport number (basic)
        passport = user_credentials['passport_number']
        if len(passport) < 6:
            self.logger.error(f"Invalid passport number: {passport}")
            return False
        
        return True
    
    def generate_dry_run_confirmation(self) -> str:
        """
        Generate confirmation code for dry run mode
        
        Returns:
            str: Generated confirmation code
        """
        # Generate random confirmation code
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        return f"DRY_RUN_{timestamp}_{random_suffix}"
    
    def _get_office_name(self, office_code: str) -> str:
        """Get office name for given office code"""
        office_names = {
            'MAD001': 'Madrid Centro',
            'MAD002': 'Madrid Norte', 
            'MAD003': 'Madrid Sur'
        }
        return office_names.get(office_code, 'Madrid Office')
    
    def _get_office_address(self, office_code: str) -> str:
        """Get office address for given office code"""
        office_addresses = {
            'MAD001': 'Calle de la Montera, 20, 28013 Madrid',
            'MAD002': 'Calle de Bravo Murillo, 101, 28003 Madrid',
            'MAD003': 'Calle de Embajadores, 155, 28012 Madrid'
        }
        return office_addresses.get(office_code, 'Madrid, Spain')
    
    def _get_office_phone(self, office_code: str) -> str:
        """Get office phone for given office code"""
        office_phones = {
            'MAD001': '+34 915 123 456',
            'MAD002': '+34 915 123 457',
            'MAD003': '+34 915 123 458'
        }
        return office_phones.get(office_code, '+34 915 123 456')
    
    async def navigate_to_booking_form(self, appointment_data: Dict[str, Any]) -> bool:
        """
        Navigate to booking form for the appointment
        
        Args:
            appointment_data: Dictionary with appointment details
            
        Returns:
            bool: True if navigation successful
        """
        try:
            self.logger.info(f"Navigating to booking form for office {appointment_data.get('office_code')}")
            
            # Simulate navigation time
            await asyncio.sleep(2)
            
            # In actual implementation, this would use the scraper
            # For MVP, just simulate success
            return True
            
        except Exception as e:
            self.logger.error(f"Error navigating to booking form: {e}")
            return False
    
    async def fill_booking_form(self, form_data: Dict[str, Any]) -> bool:
        """
        Fill booking form with user data
        
        Args:
            form_data: Dictionary with form field data
            
        Returns:
            bool: True if form filled successfully
        """
        try:
            self.logger.info("Filling booking form with user data")
            
            # Validate form data
            if not await self._validate_booking_form_data(form_data):
                return False
            
            # Simulate form filling time
            await asyncio.sleep(3)
            
            # In actual implementation, this would interact with web form
            # For MVP, just simulate success
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling booking form: {e}")
            return False
    
    async def submit_booking_form(self) -> Dict[str, Any]:
        """
        Submit booking form
        
        Returns:
            Dictionary with submission result
        """
        try:
            self.logger.info("Submitting booking form")
            
            # Simulate form submission time
            await asyncio.sleep(2)
            
            if self.dry_run_mode:
                # Simulate successful submission
                return {
                    'success': True,
                    'confirmation_code': self.generate_dry_run_confirmation(),
                    'message': 'Form submission simulated successfully'
                }
            else:
                # Actual submission (not implemented in MVP)
                return {
                    'success': False,
                    'error_message': 'Actual form submission not implemented in MVP'
                }
                
        except Exception as e:
            self.logger.error(f"Error submitting booking form: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    async def extract_confirmation_details(self, confirmation_html: str) -> Dict[str, Any]:
        """
        Extract booking confirmation details from HTML
        
        Args:
            confirmation_html: HTML content of confirmation page
            
        Returns:
            Dictionary with confirmation details
        """
        try:
            import re
            
            details = {}
            
            # Extract confirmation code
            conf_match = re.search(r'Código de confirmación:\s*<strong>([^<]+)</strong>', confirmation_html)
            if conf_match:
                details['confirmation_code'] = conf_match.group(1).strip()
            
            # Extract date
            date_match = re.search(r'Fecha:\s*<span>([^<]+)</span>', confirmation_html)
            if date_match:
                date_str = date_match.group(1).strip()
                try:
                    # Parse Spanish date format (DD/MM/YYYY)
                    day, month, year = map(int, date_str.split('/'))
                    details['date'] = date(year, month, day)
                except ValueError:
                    self.logger.warning(f"Could not parse date: {date_str}")
            
            # Extract time
            time_match = re.search(r'Hora:\s*<span>([^<]+)</span>', confirmation_html)
            if time_match:
                time_str = time_match.group(1).strip()
                try:
                    # Parse time format (HH:MM)
                    hour, minute = map(int, time_str.split(':'))
                    details['time'] = time(hour, minute)
                except ValueError:
                    self.logger.warning(f"Could not parse time: {time_str}")
            
            # Extract office name
            office_match = re.search(r'Oficina:\s*<span>([^<]+)</span>', confirmation_html)
            if office_match:
                details['office_name'] = office_match.group(1).strip()
            
            # Extract office address
            address_match = re.search(r'Dirección:\s*<span>([^<]+)</span>', confirmation_html)
            if address_match:
                details['office_address'] = address_match.group(1).strip()
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error extracting confirmation details: {e}")
            return {}
    
    async def handle_booking_error(self, error_type: str) -> Dict[str, Any]:
        """
        Handle various booking error scenarios
        
        Args:
            error_type: Type of error encountered
            
        Returns:
            Dictionary with error handling result
        """
        error_handlers = {
            'slot_no_longer_available': {
                'retry_recommended': False,
                'message': 'The appointment slot is no longer available. Please try booking a different slot.'
            },
            'invalid_credentials': {
                'retry_recommended': False,
                'message': 'Invalid user credentials. Please check your personal information.'
            },
            'network_timeout': {
                'retry_recommended': True,
                'message': 'Network timeout occurred. Retrying may resolve the issue.'
            },
            'captcha_required': {
                'retry_recommended': False,
                'message': 'CAPTCHA verification required. Manual intervention needed.'
            },
            'form_validation_error': {
                'retry_recommended': False,
                'message': 'Form validation failed. Please check your information.'
            }
        }
        
        handler = error_handlers.get(error_type, {
            'retry_recommended': True,
            'message': 'Unknown error occurred. Retrying may help.'
        })
        
        result = {
            'success': False,
            'error_type': error_type,
            'error_message': handler['message'],
            'retry_recommended': handler['retry_recommended'],
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.error(f"Handling booking error: {error_type} - {handler['message']}")
        return result
    
    async def attempt_booking_with_retry(self, appointment_data: Dict[str, Any], user_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt booking with retry logic
        
        Args:
            appointment_data: Dictionary with appointment details
            user_credentials: Dictionary with user information
            
        Returns:
            Dictionary with final booking result
        """
        attempts = 0
        last_result = None
        
        while attempts < self.max_retries:
            attempts += 1
            self.logger.info(f"Booking attempt {attempts}/{self.max_retries}")
            
            try:
                result = await self._perform_booking(appointment_data, user_credentials)
                
                if result['success']:
                    result['attempts'] = attempts
                    return result
                
                last_result = result
                
                # Check if retry is recommended
                if not result.get('retry_recommended', True):
                    self.logger.info("Retry not recommended, stopping attempts")
                    break
                
                # Wait before retry
                if attempts < self.max_retries:
                    self.logger.info(f"Waiting {self.retry_delay} seconds before retry")
                    await asyncio.sleep(self.retry_delay)
                
            except Exception as e:
                self.logger.error(f"Attempt {attempts} failed with exception: {e}")
                last_result = {
                    'success': False,
                    'error_type': 'exception',
                    'error_message': str(e),
                    'attempts': attempts
                }
        
        # All attempts failed
        if last_result:
            last_result['attempts'] = attempts
            last_result['all_attempts_failed'] = True
        
        return last_result or {
            'success': False,
            'error_type': 'retry_exhausted',
            'error_message': f'All {attempts} booking attempts failed',
            'attempts': attempts
        }
    
    async def _perform_booking(self, appointment_data: Dict[str, Any], user_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform single booking attempt
        
        Args:
            appointment_data: Dictionary with appointment details
            user_credentials: Dictionary with user information
            
        Returns:
            Dictionary with booking result
        """
        # This is a wrapper around the main booking logic
        return await self.attempt_booking(appointment_data, user_credentials)
    
    async def check_appointment_conflict(self, appointment_data: Dict[str, Any]) -> bool:
        """
        Check for appointment conflicts
        
        Args:
            appointment_data: Dictionary with appointment details
            
        Returns:
            bool: True if conflict exists, False otherwise
        """
        try:
            # For MVP, simulate conflict check
            await asyncio.sleep(0.5)
            
            # In actual implementation, this would check against existing bookings
            # For now, randomly return False (no conflicts for testing)
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking appointment conflicts: {e}")
            return False
    
    async def get_conflict_details(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get details about appointment conflicts
        
        Args:
            appointment_data: Dictionary with appointment details
            
        Returns:
            Dictionary with conflict details
        """
        # For MVP, return empty conflict details
        return {
            'existing_appointment': None,
            'conflict_type': None,
            'resolution_suggestions': []
        }
    
    async def create_booking_session(self) -> Dict[str, Any]:
        """
        Create new booking session
        
        Returns:
            Dictionary with session information
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
        
        session = {
            'session_id': session_id,
            'created_at': datetime.now(),
            'status': 'active'
        }
        
        self.session_data[session_id] = session
        self.logger.info(f"Created booking session: {session_id}")
        
        return session
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get status of booking session
        
        Args:
            session_id: ID of the session
            
        Returns:
            Dictionary with session status
        """
        session = self.session_data.get(session_id)
        
        if session:
            return {
                'session_id': session_id,
                'status': session['status'],
                'created_at': session['created_at'].isoformat()
            }
        else:
            return {
                'session_id': session_id,
                'status': 'not_found',
                'created_at': None
            }
    
    async def close_booking_session(self, session_id: str):
        """
        Close booking session
        
        Args:
            session_id: ID of the session to close
        """
        if session_id in self.session_data:
            self.session_data[session_id]['status'] = 'closed'
            self.logger.info(f"Closed booking session: {session_id}")
        else:
            self.logger.warning(f"Session not found for closing: {session_id}")
