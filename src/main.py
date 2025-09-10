"""
Main monitoring script for asylum appointment booking bot.

This is the central orchestrator that ties together all components:
- Site monitoring with Playwright scraping
- Appointment detection and parsing
- Booking attempts (simulated for MVP)
- Email notifications
- Database persistence
- Scheduled execution

MVP Features:
- Monitor single Madrid office every 2 minutes
- Send email alerts for available appointments
- Simulate booking attempts for safety
- Log all activities for debugging
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import os
from dataclasses import dataclass, asdict

# Import bot components
from models import DatabaseManager, UserProfile, MadridOffice, AppointmentSlot, BookingAttempt, populate_default_offices
from notifications import NotificationService
from scraper import ScrapingService
from booking import BookingService
from config import Config

# Configure logging
from logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

@dataclass
class MonitoringStats:
    """Statistics for monitoring session"""
    start_time: datetime
    checks_performed: int = 0
    appointments_found: int = 0
    booking_attempts: int = 0
    successful_bookings: int = 0
    errors_encountered: int = 0
    last_check_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'start_time': self.start_time.isoformat(),
            'checks_performed': self.checks_performed,
            'appointments_found': self.appointments_found,
            'booking_attempts': self.booking_attempts,
            'successful_bookings': self.successful_bookings,
            'errors_encountered': self.errors_encountered,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds()
        }

class AsylumBot:
    """
    Main asylum appointment booking bot with graceful shutdown support
    
    Features:
    - Continuous monitoring with configurable intervals
    - Health checks for all components
    - Progressive retry logic with network error handling
    - Comprehensive logging with emojis and structured messages
    - Graceful shutdown with proper resource cleanup
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the asylum bot
        
        Args:
            config: Configuration object (defaults to Config.from_env())
        """
        self.config = config or Config.from_env()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db_manager = DatabaseManager(self.config.database_url)
        self.notification_service = None
        self.scraping_service = None
        self.booking_service = None
        
        # Runtime state
        self.is_running = False
        self.shutdown_requested = False
        self.stats = MonitoringStats(start_time=datetime.now())
        self.current_user_profile = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        try:
            # Handle Ctrl+C (SIGINT) and termination (SIGTERM) signals
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self.logger.debug("🔧 Signal handlers configured for graceful shutdown")
        except ValueError as e:
            # Signal handling may not work in some environments (like Jupyter)
            self.logger.debug(f"⚠️ Could not setup signal handlers: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"🛑 Received {signal_name} signal, initiating graceful shutdown...")
        self.shutdown_requested = True
        
        if self.is_running:
            self.logger.info("📢 Stopping monitoring loop...")
        else:
            self.logger.info("🚪 Bot not running, exiting...")
            sys.exit(0)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"AsylumBot initialized with config: dry_run={self.config.dry_run_mode}")
    
    @classmethod
    def from_env(cls) -> 'AsylumBot':
        """Create AsylumBot from environment variables"""
        config = Config.from_env()
        return cls(config)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.is_running = False
    
    async def initialize(self):
        """Initialize all bot components"""
        try:
            self.logger.info("Initializing asylum bot components...")
            
            # Initialize database
            await self.initialize_database()
            
            # Initialize services
            self.notification_service = NotificationService.from_env()
            self.scraping_service = ScrapingService(
                base_url=self.config.site_url,
                headless=self.config.headless_browser
            )
            self.booking_service = BookingService.from_env()
            
            # Test services
            await self._test_services()
            
            # Load or create default user profile
            await self._load_user_profile()
            
            self.logger.info("Bot initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def initialize_database(self):
        """Initialize database and populate with default data"""
        try:
            self.logger.info("Initializing database...")
            
            # Create tables
            self.db_manager.create_tables()
            
            # Populate default Madrid offices
            session = self.db_manager.get_session()
            try:
                populate_default_offices(session)
                self.logger.info("Database initialized with default Madrid offices")
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _test_services(self):
        """Test all services to ensure they're working"""
        self.logger.info("Testing bot services...")
        
        # Test notification service
        if self.notification_service:
            test_result = self.notification_service.test_notifications()
            if test_result['success']:
                self.logger.info("✅ Notification service test passed")
            else:
                self.logger.warning(f"⚠️ Notification service test failed: {test_result['message']}")
        
        # Test scraping service
        if self.scraping_service:
            try:
                availability = await self.scraping_service.scraper.check_site_availability()
                if availability['available']:
                    self.logger.info("✅ Site scraping service test passed")
                else:
                    self.logger.warning(f"⚠️ Site not available: {availability['error_message']}")
            except Exception as e:
                self.logger.warning(f"⚠️ Scraping service test failed: {e}")
        
        # Test booking service (basic validation)
        if self.booking_service:
            test_appointment = {
                'date': datetime.now().date() + timedelta(days=30),
                'time': datetime.now().time(),
                'office_code': 'MAD001'
            }
            if self.booking_service.validate_appointment(test_appointment):
                self.logger.info("✅ Booking service test passed")
            else:
                self.logger.warning("⚠️ Booking service test failed")
    
    async def _load_user_profile(self):
        """Load or create default user profile"""
        session = self.db_manager.get_session()
        try:
            # Try to find existing user profile
            user_profile = session.query(UserProfile).filter_by(active=True).first()
            
            if not user_profile:
                # Create default test user profile for MVP
                user_profile = UserProfile(
                    name=self.config.default_user_name,
                    email=self.config.recipient_email,
                    nationality="Nigerian",
                    passport_number="A12345678",
                    phone="+34123456789"
                )
                user_profile.set_preferred_office_codes(['MAD001'])  # Start with one office for MVP
                
                session.add(user_profile)
                session.commit()
                
                self.logger.info(f"Created default user profile: {user_profile.name}")
            
            self.current_user_profile = user_profile
            self.logger.info(f"Loaded user profile: {user_profile.name} ({user_profile.email})")
            
        except Exception as e:
            self.logger.error(f"Error loading user profile: {e}")
            raise
        finally:
            session.close()
    
    async def run_single_monitoring_cycle(self) -> Dict[str, Any]:
        """
        Run a single monitoring cycle - integrates all components
        
        Returns:
            Dictionary with cycle results
        """
        cycle_start_time = datetime.now()
        cycle_result = {
            'timestamp': cycle_start_time.isoformat(),
            'success': False,
            'appointments_found': 0,
            'booking_attempts': 0,
            'notifications_sent': 0,
            'errors': [],
            'component_results': {}
        }
        
        try:
            self.logger.info("🔄 Starting monitoring cycle...")
            self.stats.checks_performed += 1
            self.stats.last_check_time = cycle_start_time
            
            # Phase 1: Site Connection Test
            self.logger.info("📡 Testing site connectivity...")
            site_check = await self.scraping_service.scraper.check_site_availability()
            cycle_result['component_results']['site_check'] = site_check
            
            if not site_check['available']:
                error_msg = f"Government site unavailable: {site_check.get('error_message', 'Unknown error')}"
                self.logger.error(f"❌ {error_msg}")
                cycle_result['errors'].append(error_msg)
                self.stats.errors_encountered += 1
                return cycle_result
            
            self.logger.info(f"✅ Site available (response time: {site_check.get('response_time_ms', 'N/A')}ms)")
            
            # Phase 2: Monitor Madrid offices for appointments
            self.logger.info("🏢 Monitoring Madrid offices for appointments...")
            monitoring_result = await self.scraping_service.monitor_madrid_offices()
            cycle_result['component_results']['monitoring'] = monitoring_result
            
            if monitoring_result['success']:
                appointments = monitoring_result['appointments']
                cycle_result['appointments_found'] = len(appointments)
                self.stats.appointments_found += len(appointments)
                
                if appointments:
                    self.logger.info(f"🎯 Found {len(appointments)} available appointments!")
                    
                    # Phase 3: Process each found appointment
                    for i, appointment in enumerate(appointments, 1):
                        try:
                            self.logger.info(f"📋 Processing appointment {i}/{len(appointments)}")
                            await self._process_found_appointment(appointment)
                            cycle_result['booking_attempts'] += 1
                            cycle_result['notifications_sent'] += 1
                            
                        except Exception as e:
                            self.logger.error(f"❌ Error processing appointment {i}: {e}")
                            cycle_result['errors'].append(f"Appointment {i} error: {str(e)}")
                            self.stats.errors_encountered += 1
                else:
                    self.logger.info("📭 No appointments found this cycle")
                
                cycle_result['success'] = True
                
            else:
                error_msg = f"Monitoring failed: {', '.join(monitoring_result['errors'])}"
                self.logger.error(f"❌ {error_msg}")
                cycle_result['errors'].append(error_msg)
                self.stats.errors_encountered += 1
            
            # Phase 4: Update component health status
            cycle_result['component_results']['database_health'] = await self._check_database_health()
            cycle_result['component_results']['notification_health'] = await self._check_notification_health()
            
        except Exception as e:
            error_msg = f"Monitoring cycle error: {str(e)}"
            self.logger.error(f"💥 {error_msg}")
            cycle_result['errors'].append(error_msg)
            self.stats.errors_encountered += 1
        
        # Calculate cycle duration
        cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
        cycle_result['cycle_duration_seconds'] = cycle_duration
        
        # Log cycle summary
        status_emoji = "✅" if cycle_result['success'] else "❌"
        self.logger.info(
            f"{status_emoji} Cycle completed in {cycle_duration:.1f}s: "
            f"{cycle_result['appointments_found']} appointments, "
            f"{cycle_result['booking_attempts']} booking attempts, "
            f"{len(cycle_result['errors'])} errors"
        )
        
        return cycle_result
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database component health"""
        try:
            session = self.db_manager.get_session()
            start_time = datetime.now()
            
            # Simple health check query
            user_count = session.query(UserProfile).count()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            session.close()
            
            return {
                'status': 'healthy',
                'response_time_ms': int(response_time),
                'user_count': user_count,
                'message': 'Database responding normally'
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Database connection failed'
            }
    
    async def _check_notification_health(self) -> Dict[str, Any]:
        """Check notification component health"""
        try:
            if not self.notification_service:
                return {
                    'status': 'unhealthy',
                    'message': 'Notification service not initialized'
                }
            
            # Test SMTP connection
            test_result = self.notification_service.test_notifications()
            
            return {
                'status': 'healthy' if test_result['success'] else 'warning',
                'smtp_test': test_result,
                'message': test_result.get('message', 'Unknown status')
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Notification service check failed'
            }

    async def _process_found_appointment(self, appointment: Dict[str, Any]):
        """
        Process a found appointment (notification + booking attempt) with detailed logging
        
        Args:
            appointment: Dictionary with appointment details
        """
        appointment_id = f"{appointment.get('date', 'unknown')}_{appointment.get('time', 'unknown')}"
        
        try:
            self.logger.info(f"📋 Processing appointment {appointment_id}")
            self.logger.debug(f"Appointment details: {json.dumps(appointment, default=str, indent=2)}")
            
            # Save appointment to database
            self.logger.info(f"💾 Saving appointment {appointment_id} to database...")
            await self._save_appointment_to_db(appointment)
            self.logger.info(f"✅ Appointment {appointment_id} saved to database")
            
            # Send notification about found appointment
            self.logger.info(f"📧 Sending appointment alert for {appointment_id}...")
            notification_start = datetime.now()
            
            notification_success = self.notification_service.notify_appointment_found(
                appointment_data=appointment,
                recipient=self.current_user_profile.email
            )
            
            notification_duration = (datetime.now() - notification_start).total_seconds()
            
            if notification_success:
                self.logger.info(f"✅ Appointment alert sent for {appointment_id} (took {notification_duration:.1f}s)")
            else:
                self.logger.warning(f"⚠️ Failed to send appointment notification for {appointment_id}")
            
            # Attempt booking if configured
            if self.config.auto_booking_enabled:
                self.logger.info(f"🎯 Auto-booking enabled, attempting to book {appointment_id}...")
                await self._attempt_appointment_booking(appointment)
            else:
                self.logger.info(f"⏸️ Auto-booking disabled for {appointment_id}, skipping booking attempt")
            
            self.logger.info(f"✅ Completed processing appointment {appointment_id}")
            
        except Exception as e:
            self.logger.error(f"💥 Error processing appointment {appointment_id}: {e}")
            self.logger.error(f"Appointment data: {json.dumps(appointment, default=str)}")
            raise
    
    async def _save_appointment_to_db(self, appointment: Dict[str, Any]):
        """Save found appointment to database"""
        session = self.db_manager.get_session()
        try:
            # Get office info
            office_info = appointment.get('office_info', {})
            office_code = office_info.get('office_code', 'MAD001')
            
            # Find or create office
            office = session.query(MadridOffice).filter_by(office_code=office_code).first()
            if not office:
                office = session.query(MadridOffice).first()  # Fallback to first office
            
            # Create appointment slot record
            appointment_slot = AppointmentSlot(
                office_id=office.id,
                appointment_date=appointment['date'],
                appointment_time=appointment['time'],
                available=appointment.get('available', True),
                site_slot_id=appointment.get('site_slot_id'),
                first_detected=datetime.now(),
                last_seen=datetime.now()
            )
            
            session.add(appointment_slot)
            session.commit()
            
            self.logger.info(f"Saved appointment to database: {appointment['date']} {appointment['time']}")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving appointment to database: {e}")
            raise
        finally:
            session.close()
    
    async def _attempt_appointment_booking(self, appointment: Dict[str, Any]):
        """
        Attempt to book the found appointment with comprehensive logging
        
        Args:
            appointment: Dictionary with appointment details
        """
        appointment_id = f"{appointment.get('date', 'unknown')}_{appointment.get('time', 'unknown')}"
        booking_start_time = datetime.now()
        
        try:
            self.logger.info(f"🎯 Starting booking attempt for appointment {appointment_id}")
            self.stats.booking_attempts += 1
            
            # Prepare user credentials
            user_credentials = {
                'name': self.current_user_profile.name,
                'email': self.current_user_profile.email,
                'phone': self.current_user_profile.phone,
                'nationality': self.current_user_profile.nationality,
                'passport_number': self.current_user_profile.passport_number
            }
            
            self.logger.info(f"👤 Using credentials for: {user_credentials['name']} ({user_credentials['email']})")
            self.logger.debug(f"Full credentials: {json.dumps({k: v for k, v in user_credentials.items() if k != 'passport_number'})}")
            
            # Attempt booking
            self.logger.info(f"🚀 Initiating booking process for {appointment_id}...")
            booking_result = await self.booking_service.attempt_booking(appointment, user_credentials)
            
            booking_duration = (datetime.now() - booking_start_time).total_seconds()
            self.logger.info(f"⏱️ Booking attempt completed in {booking_duration:.1f}s")
            
            # Save booking attempt to database
            self.logger.info(f"💾 Saving booking attempt for {appointment_id} to database...")
            await self._save_booking_attempt_to_db(booking_result, appointment)
            
            if booking_result['success']:
                self.stats.successful_bookings += 1
                booking_type = "simulated" if booking_result.get('dry_run', True) else "completed"
                confirmation_code = booking_result.get('confirmation_code', 'N/A')
                
                self.logger.info(f"🎉 Booking {booking_type} successfully for {appointment_id}")
                self.logger.info(f"📋 Confirmation code: {confirmation_code}")
                
                # Send booking confirmation notification
                self.logger.info(f"📧 Sending booking confirmation for {appointment_id}...")
                notification_sent = self.notification_service.notify_booking_confirmed(
                    booking_data=booking_result,
                    recipient=self.current_user_profile.email
                )
                
                if notification_sent:
                    self.logger.info(f"✅ Booking confirmation sent for {appointment_id}")
                else:
                    self.logger.warning(f"⚠️ Failed to send booking confirmation for {appointment_id}")
                
            else:
                error_type = booking_result.get('error_type', 'unknown')
                error_message = booking_result.get('error_message', 'Unknown error')
                
                self.logger.warning(f"❌ Booking attempt failed for {appointment_id}")
                self.logger.warning(f"Error type: {error_type}")
                self.logger.warning(f"Error message: {error_message}")
                
                # Send error notification
                self.logger.info(f"📧 Sending booking error notification for {appointment_id}...")
                self.notification_service.notify_error(
                    error_data={
                        'error_type': error_type,
                        'error_message': error_message,
                        'timestamp': booking_result.get('timestamp'),
                        'operation': 'appointment_booking',
                        'context': {
                            'appointment_id': appointment_id,
                            'appointment_data': appointment,
                            'booking_duration_seconds': booking_duration
                        }
                    },
                    recipient=self.current_user_profile.email
                )
            
        except Exception as e:
            booking_duration = (datetime.now() - booking_start_time).total_seconds()
            self.logger.error(f"💥 Exception in booking attempt for {appointment_id} after {booking_duration:.1f}s: {e}")
            self.logger.error(f"Appointment data: {json.dumps(appointment, default=str)}")
            self.stats.errors_encountered += 1
            raise
    
    async def _save_booking_attempt_to_db(self, booking_result: Dict[str, Any], appointment: Dict[str, Any]):
        """
        Save booking attempt to database with comprehensive logging
        
        Args:
            booking_result: Result from booking attempt
            appointment: Original appointment data
        """
        appointment_id = f"{appointment.get('date', 'unknown')}_{appointment.get('time', 'unknown')}"
        save_start_time = datetime.now()
        session = self.db_manager.get_session()
        
        try:
            self.logger.info(f"💾 Saving booking attempt for {appointment_id} to database...")
            
            # Get office info
            office_info = appointment.get('office_info', {})
            office_code = office_info.get('office_code', 'MAD001')
            office = session.query(MadridOffice).filter_by(office_code=office_code).first()
            
            if not office:
                office = session.query(MadridOffice).first()  # Fallback
                self.logger.warning(f"⚠️ Office {office_code} not found, using fallback office {office.office_code}")
            else:
                self.logger.debug(f"Using office: {office.office_code} ({office.name})")
            
            # Create booking attempt record
            booking_attempt = BookingAttempt(
                user_id=self.current_user_profile.id,
                office_id=office.id,
                attempted_at=datetime.now(),
                status='success' if booking_result['success'] else 'failed',
                appointment_date=appointment.get('date'),
                appointment_time=appointment.get('time'),
                confirmation_code=booking_result.get('confirmation_code'),
                error_type=booking_result.get('error_type'),
                error_message=booking_result.get('error_message'),
                dry_run=booking_result.get('dry_run', True),
                attempt_duration_ms=booking_result.get('simulation_duration_ms', 0)
            )
            
            booking_attempt.set_response_data(booking_result)
            
            session.add(booking_attempt)
            session.commit()
            
            booking_attempt_id = booking_attempt.id
            save_duration = (datetime.now() - save_start_time).total_seconds()
            
            booking_status = "success" if booking_result['success'] else "failed"
            dry_run_status = "dry run" if booking_result.get('dry_run', True) else "live booking"
            
            self.logger.info(f"✅ Booking attempt saved to database with ID {booking_attempt_id} in {save_duration:.2f}s")
            self.logger.info(f"📊 Status: {booking_status} ({dry_run_status})")
            
        except Exception as e:
            session.rollback()
            save_duration = (datetime.now() - save_start_time).total_seconds()
            self.logger.error(f"💥 Error saving booking attempt to database after {save_duration:.2f}s: {e}")
            self.logger.error(f"Booking result data: {json.dumps(booking_result, default=str)}")
            self.logger.error(f"Appointment data: {json.dumps(appointment, default=str)}")
            raise
        finally:
            session.close()
    
    async def run_continuous_monitoring(self):
        """
        Run continuous monitoring with graceful shutdown support
        
        Features:
        - Configured intervals with health checks
        - Progressive retry logic with network error handling  
        - Graceful shutdown on signal interruption
        - Comprehensive error recovery
        """
        try:
            self.is_running = True
            self.logger.info(f"🚀 Starting continuous monitoring (interval: {self.config.monitoring_interval}s)")
            self.logger.info(f"💡 Press Ctrl+C for graceful shutdown")
            
            # Send startup notification
            self.notification_service.notify_status(
                status_data={
                    'status': 'started',
                    'timestamp': datetime.now().isoformat(),
                    'monitoring_interval': self.config.monitoring_interval,
                    'dry_run_mode': self.config.dry_run_mode,
                    'auto_booking': self.config.auto_booking_enabled
                },
                recipient=self.current_user_profile.email
            )
            
            consecutive_errors = 0
            max_consecutive_errors = 5
            base_retry_delay = 30  # Base retry delay in seconds
            
            while self.is_running and not self.shutdown_requested:
                try:
                    # Check for shutdown before starting cycle
                    if self.shutdown_requested:
                        self.logger.info("🛑 Shutdown requested, breaking monitoring loop")
                        break
                    
                    # Run monitoring cycle with retry logic
                    cycle_result = await self._run_cycle_with_retry()
                    
                    # Reset error counter on successful cycle
                    if cycle_result['success']:
                        if consecutive_errors > 0:
                            self.logger.info(f"✅ Recovered after {consecutive_errors} consecutive errors")
                            consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                        self.logger.warning(f"⚠️ Cycle failed ({consecutive_errors}/{max_consecutive_errors} consecutive errors)")
                    
                    # Log cycle summary with emojis
                    status_emoji = "✅" if cycle_result['success'] else "❌"
                    self.logger.info(
                        f"{status_emoji} Cycle summary: {cycle_result['appointments_found']} appointments found, "
                        f"{cycle_result['booking_attempts']} booking attempts, "
                        f"{len(cycle_result['errors'])} errors"
                    )
                    
                    # Check for too many consecutive errors
                    if consecutive_errors >= max_consecutive_errors:
                        error_msg = f"Too many consecutive errors ({consecutive_errors}), implementing progressive backoff"
                        self.logger.error(f"🚨 {error_msg}")
                        
                        # Send error notification
                        self.notification_service.notify_error(
                            error_data={
                                'error_type': 'consecutive_failures',
                                'error_message': error_msg,
                                'timestamp': datetime.now().isoformat(),
                                'operation': 'continuous_monitoring',
                                'consecutive_errors': consecutive_errors,
                                'context': cycle_result
                            },
                            recipient=self.current_user_profile.email
                        )
                        
                        # Progressive backoff: wait longer after multiple failures
                        backoff_delay = min(base_retry_delay * (2 ** (consecutive_errors - max_consecutive_errors)), 300)  # Max 5 minutes
                        self.logger.info(f"⏳ Implementing {backoff_delay}s backoff delay...")
                        await self._interruptible_sleep(backoff_delay)
                    
                    # Normal wait for next cycle (with shutdown check)
                    if self.is_running and not self.shutdown_requested:
                        self.logger.info(f"⏳ Waiting {self.config.monitoring_interval}s until next check...")
                        await self._interruptible_sleep(self.config.monitoring_interval)
                    
                except asyncio.CancelledError:
                    self.logger.info("🛑 Monitoring cancelled")
                    break
                except Exception as e:
                    consecutive_errors += 1
                    self.logger.error(f"💥 Fatal error in monitoring cycle ({consecutive_errors}): {e}")
                    self.stats.errors_encountered += 1
                    
                    # Send error notification for critical failures
                    try:
                        self.notification_service.notify_error(
                            error_data={
                                'error_type': 'fatal_monitoring_error',
                                'error_message': str(e),
                                'timestamp': datetime.now().isoformat(),
                                'operation': 'continuous_monitoring',
                                'consecutive_errors': consecutive_errors
                            },
                            recipient=self.current_user_profile.email
                        )
                    except Exception as notification_error:
                        self.logger.error(f"Failed to send error notification: {notification_error}")
                    
                    # Wait before retrying after critical error
                    if self.is_running and consecutive_errors < max_consecutive_errors and not self.shutdown_requested:
                        retry_delay = min(base_retry_delay * consecutive_errors, 120)  # Max 2 minutes
                        self.logger.info(f"⏳ Retrying in {retry_delay}s...")
                        await self._interruptible_sleep(retry_delay)
                    elif consecutive_errors >= max_consecutive_errors:
                        self.logger.error(f"🚨 Maximum consecutive errors reached ({consecutive_errors}), stopping monitoring")
                        break
            
        except Exception as e:
            self.logger.error(f"💥 Fatal error in continuous monitoring: {e}")
            raise
        finally:
            self.logger.info("🏁 Monitoring loop finished, starting cleanup...")
            await self.cleanup()
    
    async def _run_cycle_with_retry(self, max_retries: int = 3) -> Dict[str, Any]:
        """
        Run monitoring cycle with retry logic for network failures
        
        Args:
            max_retries: Maximum number of retries for network failures
            
        Returns:
            Dictionary with cycle results
        """
        last_result = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    retry_delay = 5 * attempt  # Progressive delay: 5s, 10s, 15s
                    self.logger.info(f"🔄 Retry attempt {attempt}/{max_retries} (waiting {retry_delay}s)...")
                    await asyncio.sleep(retry_delay)
                
                result = await self.run_single_monitoring_cycle()
                
                # Check if this was a network-related failure that should be retried
                if not result['success'] and self._should_retry_cycle(result):
                    last_result = result
                    if attempt < max_retries:
                        self.logger.warning(f"⚠️ Network error detected, will retry (attempt {attempt + 1}/{max_retries + 1})")
                        continue
                    else:
                        self.logger.error(f"❌ All retry attempts failed, returning last result")
                        return result
                
                # Success or non-retryable failure
                if attempt > 0:
                    self.logger.info(f"✅ Succeeded on retry attempt {attempt}")
                
                return result
                
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ Timeout on attempt {attempt + 1}")
                last_result = {
                    'success': False,
                    'timestamp': datetime.now().isoformat(),
                    'appointments_found': 0,
                    'booking_attempts': 0,
                    'notifications_sent': 0,
                    'errors': ['Network timeout'],
                    'cycle_duration_seconds': 0
                }
                if attempt < max_retries:
                    continue
            except Exception as e:
                self.logger.error(f"💥 Error on attempt {attempt + 1}: {e}")
                last_result = {
                    'success': False,
                    'timestamp': datetime.now().isoformat(),
                    'appointments_found': 0,
                    'booking_attempts': 0,
                    'notifications_sent': 0,
                    'errors': [str(e)],
                    'cycle_duration_seconds': 0
                }
                
                # Don't retry non-network errors
                if not self._is_network_error(e):
                    break
                
                if attempt < max_retries:
                    continue
        
        return last_result or {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'appointments_found': 0,
            'booking_attempts': 0,
            'notifications_sent': 0,
            'errors': ['All retry attempts failed'],
            'cycle_duration_seconds': 0
        }
    
    def _should_retry_cycle(self, result: Dict[str, Any]) -> bool:
        """
        Determine if a failed cycle should be retried based on error types
        
        Args:
            result: Cycle result dictionary
            
        Returns:
            bool: True if cycle should be retried
        """
        # Check for network-related errors in the error messages
        network_error_keywords = [
            'timeout', 'connection', 'network', 'unavailable', 
            'unreachable', 'dns', 'socket', 'ssl', 'tls'
        ]
        
        for error in result.get('errors', []):
            error_lower = str(error).lower()
            if any(keyword in error_lower for keyword in network_error_keywords):
                return True
        
        # Check component results for network issues
        component_results = result.get('component_results', {})
        site_check = component_results.get('site_check', {})
        
        if not site_check.get('available', True):
            return True
        
        return False
    
    def _is_network_error(self, exception: Exception) -> bool:
        """
        Check if an exception is network-related and should be retried
        
        Args:
            exception: Exception to check
            
        Returns:
            bool: True if this is a network error
        """
        network_exception_types = [
            'ConnectionError', 'TimeoutError', 'NetworkError', 
            'DNSError', 'SSLError', 'HTTPError'
        ]
        
        exception_name = type(exception).__name__
        return any(net_type in exception_name for net_type in network_exception_types)

    async def run_continuous_monitoring_original(self):
        """Run continuous monitoring with configured intervals"""
        try:
            self.is_running = True
            self.logger.info(f"Starting continuous monitoring (interval: {self.config.monitoring_interval} seconds)")
            
            # Send startup notification
            self.notification_service.notify_status(
                status_data={
                    'status': 'started',
                    'timestamp': datetime.now().isoformat(),
                    'monitoring_interval': self.config.monitoring_interval,
                    'dry_run_mode': self.config.dry_run_mode,
                    'auto_booking': self.config.auto_booking_enabled
                },
                recipient=self.current_user_profile.email
            )
            
            while self.is_running:
                try:
                    # Run monitoring cycle
                    cycle_result = await self.run_single_monitoring_cycle()
                    
                    # Log cycle summary
                    self.logger.info(
                        f"Cycle completed: {cycle_result['appointments_found']} appointments found, "
                        f"{cycle_result['booking_attempts']} booking attempts, "
                        f"{len(cycle_result['errors'])} errors"
                    )
                    
                    # Wait for next cycle
                    if self.is_running:
                        self.logger.info(f"Waiting {self.config.monitoring_interval} seconds until next check...")
                        await asyncio.sleep(self.config.monitoring_interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in monitoring cycle: {e}")
                    self.stats.errors_encountered += 1
                    
                    # Send error notification
                    self.notification_service.notify_error(
                        error_data={
                            'error_type': 'monitoring_cycle_error',
                            'error_message': str(e),
                            'timestamp': datetime.now().isoformat(),
                            'operation': 'continuous_monitoring'
                        },
                        recipient=self.current_user_profile.email
                    )
                    
                    # Wait before retrying
                    if self.is_running:
                        await asyncio.sleep(self.config.monitoring_interval)
            
        except Exception as e:
            self.logger.error(f"Fatal error in continuous monitoring: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def run_complete_workflow(self) -> Dict[str, Any]:
        """
        Run complete workflow once (for testing/integration)
        
        Returns:
            Dictionary with workflow results
        """
        workflow_result = {
            'workflow_completed': False,
            'monitoring_results': {},
            'booking_attempts': 0,
            'notifications_sent': 0,
            'errors': []
        }
        
        try:
            self.logger.info("Running complete workflow...")
            
            # Initialize if not already done
            if not self.notification_service:
                await self.initialize()
            
            # Run single monitoring cycle
            monitoring_result = await self.run_single_monitoring_cycle()
            workflow_result['monitoring_results'] = monitoring_result
            workflow_result['booking_attempts'] = monitoring_result['booking_attempts']
            workflow_result['notifications_sent'] = monitoring_result['notifications_sent']
            workflow_result['errors'] = monitoring_result['errors']
            
            workflow_result['workflow_completed'] = monitoring_result['success']
            
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Error in complete workflow: {e}")
            workflow_result['errors'].append(str(e))
            return workflow_result
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate bot configuration
        
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'valid': True,
            'required_fields_present': True,
            'missing_fields': [],
            'warnings': []
        }
        
        # Check required configuration fields
        required_fields = [
            ('site_url', self.config.site_url),
            ('gmail_username', self.config.gmail_username),
            ('gmail_password', self.config.gmail_password),
            ('recipient_email', self.config.recipient_email)
        ]
        
        for field_name, field_value in required_fields:
            if not field_value:
                validation_result['missing_fields'].append(field_name)
                validation_result['required_fields_present'] = False
        
        if validation_result['missing_fields']:
            validation_result['valid'] = False
        
        # Add warnings for optional fields
        if self.config.dry_run_mode:
            validation_result['warnings'].append('Running in DRY RUN mode - no actual bookings will be made')
        
        if not self.config.auto_booking_enabled:
            validation_result['warnings'].append('Auto-booking is disabled - only notifications will be sent')
        
        return validation_result
    
    async def cleanup(self):
        """Cleanup bot resources"""
        try:
            self.logger.info("Cleaning up bot resources...")
            
            cleanup_result = {
                'database_closed': False,
                'browser_closed': False,
                'scheduler_stopped': False,
                'temp_files_cleaned': False
            }
            
            # Cleanup scraping service
            if self.scraping_service:
                await self.scraping_service.cleanup()
                cleanup_result['browser_closed'] = True
            
            # Database is closed automatically with session management
            cleanup_result['database_closed'] = True
            cleanup_result['scheduler_stopped'] = True  # No scheduler in MVP
            cleanup_result['temp_files_cleaned'] = True  # No temp files in MVP
            
            # Send shutdown notification
            if self.notification_service and self.current_user_profile:
                final_stats = self.stats.to_dict()
                self.notification_service.notify_status(
                    status_data={
                        'status': 'stopped',
                        'timestamp': datetime.now().isoformat(),
                        'final_stats': final_stats
                    },
                    recipient=self.current_user_profile.email
                )
            
            self.logger.info("Bot cleanup completed")
            return cleanup_result
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            Dictionary with health check results
        """
        health_result = {
            'overall_status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'database': {'status': 'unknown'},
                'browser': {'status': 'unknown'}, 
                'notifications': {'status': 'unknown'},
                'scheduler': {'status': 'healthy'}  # No scheduler in MVP
            },
            'response_times': {},
            'memory_usage': 'N/A',  # Not implemented in MVP
            'disk_usage': 'N/A'     # Not implemented in MVP
        }
        
        try:
            # Check database
            start_time = datetime.now()
            session = self.db_manager.get_session()
            session.query(UserProfile).count()  # Simple query
            session.close()
            database_time = (datetime.now() - start_time).total_seconds() * 1000
            
            health_result['components']['database']['status'] = 'healthy'
            health_result['response_times']['database_ms'] = int(database_time)
            
            # Check browser/scraping
            start_time = datetime.now()
            if self.scraping_service:
                availability = await self.scraping_service.scraper.check_site_availability()
                browser_time = (datetime.now() - start_time).total_seconds() * 1000
                
                health_result['components']['browser']['status'] = 'healthy' if availability['available'] else 'warning'
                health_result['response_times']['browser_ms'] = int(browser_time)
            
            # Check notifications
            start_time = datetime.now()
            if self.notification_service:
                test_result = self.notification_service.test_notifications()
                notification_time = (datetime.now() - start_time).total_seconds() * 1000
                
                health_result['components']['notifications']['status'] = 'healthy' if test_result['success'] else 'warning'
                health_result['response_times']['notifications_ms'] = int(notification_time)
            
            # Determine overall status
            component_statuses = [comp['status'] for comp in health_result['components'].values()]
            if 'unhealthy' in component_statuses:
                health_result['overall_status'] = 'unhealthy'
            elif 'warning' in component_statuses:
                health_result['overall_status'] = 'warning'
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            health_result['overall_status'] = 'unhealthy'
            health_result['error'] = str(e)
        
        return health_result

async def main():
    """Main entry point for the asylum bot"""
    try:
        # Create and initialize bot
        bot = AsylumBot.from_env()
        await bot.initialize()
        
        # Validate configuration
        validation = bot.validate_configuration()
        if not validation['valid']:
            logger.error(f"Configuration validation failed: {validation['missing_fields']}")
            sys.exit(1)
        
        # Log warnings
        for warning in validation['warnings']:
            logger.warning(warning)
        
        # Run continuous monitoring
        logger.info("Starting asylum appointment bot...")
        await bot.run_continuous_monitoring()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)


class AsylumBotHelpers:
    """Helper methods for AsylumBot (moved to avoid nesting issues)"""
    
    @staticmethod
    async def _interruptible_sleep(shutdown_flag, duration: float):
        """
        Sleep that can be interrupted by shutdown signal
        
        Args:
            shutdown_flag: Boolean flag indicating shutdown request
            duration: Sleep duration in seconds
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if shutdown_flag:
                elapsed = asyncio.get_event_loop().time() - start_time
                break
                
            # Sleep in small chunks to check for shutdown
            chunk_duration = min(1.0, duration)
            await asyncio.sleep(chunk_duration)
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= duration:
                break
                
            duration -= chunk_duration


# Add helper methods to AsylumBot class
async def _interruptible_sleep(self, duration: float):
    """
    Sleep that can be interrupted by shutdown signal
    
    Args:
        duration: Sleep duration in seconds
    """
    start_time = asyncio.get_event_loop().time()
    
    while True:
        if self.shutdown_requested:
            elapsed = asyncio.get_event_loop().time() - start_time
            self.logger.debug(f"⏸️ Sleep interrupted after {elapsed:.1f}s (requested {duration}s)")
            break
            
        # Sleep in small chunks to check for shutdown
        chunk_duration = min(1.0, duration)
        await asyncio.sleep(chunk_duration)
        
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= duration:
            break
            
        duration -= chunk_duration

async def cleanup(self):
    """
    Perform graceful cleanup of all resources
    """
    cleanup_start_time = datetime.now()
    self.logger.info("🧹 Starting cleanup process...")
    
    try:
        # Mark as no longer running
        self.is_running = False
        
        # Close scraping service
        if self.scraping_service:
            try:
                self.logger.info("🔧 Closing scraping service...")
                await self.scraping_service.close()
                self.logger.info("✅ Scraping service closed")
            except Exception as e:
                self.logger.error(f"❌ Error closing scraping service: {e}")
        
        # Close booking service
        if self.booking_service:
            try:
                self.logger.info("🔧 Closing booking service...")
                await self.booking_service.close()
                self.logger.info("✅ Booking service closed")
            except Exception as e:
                self.logger.error(f"❌ Error closing booking service: {e}")
        
        # Send shutdown notification
        if self.notification_service and self.current_user_profile:
            try:
                self.logger.info("📧 Sending shutdown notification...")
                runtime_duration = (datetime.now() - self.stats.start_time).total_seconds()
                
                self.notification_service.notify_status(
                    status_data={
                        'status': 'stopped',
                        'timestamp': datetime.now().isoformat(),
                        'runtime_duration_seconds': runtime_duration,
                        'total_cycles': self.stats.cycles_completed,
                        'total_appointments_found': self.stats.appointments_found,
                        'total_booking_attempts': self.stats.booking_attempts,
                        'successful_bookings': self.stats.successful_bookings,
                        'errors_encountered': self.stats.errors_encountered
                    },
                    recipient=self.current_user_profile.email
                )
                self.logger.info("✅ Shutdown notification sent")
            except Exception as e:
                self.logger.error(f"❌ Error sending shutdown notification: {e}")
        
        # Close database connections
        if self.db_manager:
            try:
                self.logger.info("🔧 Closing database connections...")
                # Database connections are typically closed automatically
                self.logger.info("✅ Database connections closed")
            except Exception as e:
                self.logger.error(f"❌ Error closing database: {e}")
        
        cleanup_duration = (datetime.now() - cleanup_start_time).total_seconds()
        self.logger.info(f"🧹 Cleanup completed in {cleanup_duration:.2f}s")
        
        # Final statistics summary
        runtime_duration = (datetime.now() - self.stats.start_time).total_seconds()
        self.logger.info("📊 Final Statistics:")
        self.logger.info(f"   ⏱️ Total runtime: {runtime_duration:.1f}s")
        self.logger.info(f"   🔄 Monitoring cycles: {self.stats.cycles_completed}")
        self.logger.info(f"   📅 Appointments found: {self.stats.appointments_found}")
        self.logger.info(f"   🎯 Booking attempts: {self.stats.booking_attempts}")
        self.logger.info(f"   ✅ Successful bookings: {self.stats.successful_bookings}")
        self.logger.info(f"   ❌ Errors encountered: {self.stats.errors_encountered}")
        self.logger.info("🏁 Bot shutdown complete")
        
    except Exception as e:
        self.logger.error(f"💥 Error during cleanup: {e}")
        raise

# Bind methods to AsylumBot class
AsylumBot._interruptible_sleep = _interruptible_sleep
AsylumBot.cleanup = cleanup

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
