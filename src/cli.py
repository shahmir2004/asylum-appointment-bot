"""
Command-line interface for asylum appointment booking bot.

Provides simple commands for:
- Starting/stopping monitoring
- Checking status
- Viewing logs
- Testing components
- Configuration management
"""

import asyncio
import argparse
import logging
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

# Import bot components
try:
    from main import AsylumBot
except ImportError:
    # Try with src prefix for CLI usage
    from src.main import AsylumBot
from config import Config
from models import DatabaseManager, UserProfile, BookingAttempt
from notifications import NotificationService

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AsylumBotCLI:
    """Command-line interface for asylum bot operations"""
    
    def __init__(self):
        """Initialize CLI"""
        self.config = None
        self.bot = None
        self.logger = logging.getLogger(__name__)
    
    def execute(self, command_args: List[str]) -> Dict[str, Any]:
        """
        Execute CLI command
        
        Args:
            command_args: List of command arguments
            
        Returns:
            Dictionary with execution result
        """
        try:
            # Parse arguments
            parser = self._create_argument_parser()
            args = parser.parse_args(command_args)
            
            # Execute command
            if args.command == 'monitor':
                return asyncio.run(self._cmd_monitor(args))
            elif args.command == 'book':
                return asyncio.run(self._cmd_book(args))
            elif args.command == 'status':
                return asyncio.run(self._cmd_status(args))
            elif args.command == 'config':
                return self._cmd_config(args)
            elif args.command == 'logs':
                return self._cmd_logs(args)
            elif args.command == 'test':
                return asyncio.run(self._cmd_test(args))
            elif args.command == 'health':
                return asyncio.run(self._cmd_health(args))
            else:
                return {
                    'success': False,
                    'output': f'Unknown command: {args.command}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': f'Command execution error: {str(e)}'
            }
    
    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """Create argument parser for CLI commands"""
        parser = argparse.ArgumentParser(
            description='Asylum Appointment Bot CLI',
            prog='asylum-bot'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Monitor command
        monitor_parser = subparsers.add_parser('monitor', help='Start monitoring for appointments')
        monitor_parser.add_argument('--interval', type=int, default=120, 
                                  help='Monitoring interval in seconds (default: 120)')
        monitor_parser.add_argument('--cycles', type=int, default=None,
                                  help='Number of cycles to run (default: infinite)')
        monitor_parser.add_argument('--office-code', type=str, default=None,
                                  help='Specific office code to monitor')
        
        # Book command
        book_parser = subparsers.add_parser('book', help='Attempt to book specific appointment')
        book_parser.add_argument('--appointment-id', type=str, required=True,
                               help='Appointment ID to book')
        book_parser.add_argument('--user-id', type=int, default=None,
                               help='User ID for booking (default: first active user)')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show bot status and statistics')
        status_parser.add_argument('--detailed', action='store_true',
                                 help='Show detailed status information')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_parser.add_argument('--show', action='store_true',
                                  help='Show current configuration')
        config_parser.add_argument('--validate', action='store_true',
                                  help='Validate configuration')
        
        # Logs command
        logs_parser = subparsers.add_parser('logs', help='View log files')
        logs_parser.add_argument('--tail', type=int, default=50,
                               help='Number of lines to show (default: 50)')
        logs_parser.add_argument('--follow', action='store_true',
                               help='Follow log file (like tail -f)')
        logs_parser.add_argument('--level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                               help='Filter by log level')
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Test bot components')
        test_parser.add_argument('--component', type=str, 
                               choices=['all', 'notifications', 'scraping', 'booking', 'database'],
                               default='all', help='Component to test')
        
        # Health command
        health_parser = subparsers.add_parser('health', help='Perform health check')
        health_parser.add_argument('--detailed', action='store_true',
                                 help='Show detailed health information')
        
        return parser
    
    async def _cmd_monitor(self, args) -> Dict[str, Any]:
        """Execute monitor command"""
        try:
            self.logger.info(f"Starting monitoring with interval: {args.interval} seconds")
            
            # Initialize bot
            self.bot = AsylumBot.from_env()
            
            # Override monitoring interval if specified
            if args.interval != 120:
                self.bot.config.monitoring_interval = args.interval
            
            await self.bot.initialize()
            
            if args.cycles:
                # Run specific number of cycles
                results = []
                for cycle in range(args.cycles):
                    self.logger.info(f"Running cycle {cycle + 1}/{args.cycles}")
                    result = await self.bot.run_single_monitoring_cycle()
                    results.append(result)
                
                return {
                    'success': True,
                    'output': f'Completed {args.cycles} monitoring cycles',
                    'results': results
                }
            else:
                # Run continuous monitoring
                await self.bot.run_continuous_monitoring()
                return {
                    'success': True,
                    'output': 'Monitoring stopped'
                }
                
        except Exception as e:
            self.logger.error(f"Error in monitor command: {e}")
            return {
                'success': False,
                'output': f'Monitoring error: {str(e)}'
            }
    
    async def _cmd_book(self, args) -> Dict[str, Any]:
        """Execute book command"""
        try:
            self.logger.info(f"Attempting to book appointment: {args.appointment_id}")
            
            # Initialize bot
            self.bot = AsylumBot.from_env()
            await self.bot.initialize()
            
            # Find appointment by ID
            session = self.bot.db_manager.get_session()
            try:
                # In a real implementation, we'd lookup the appointment
                # For MVP, simulate booking attempt
                mock_appointment = {
                    'date': datetime.now().date() + timedelta(days=30),
                    'time': datetime.now().time().replace(hour=10, minute=0),
                    'office_code': 'MAD001'
                }
                
                # Get user profile
                user_profile = session.query(UserProfile).filter_by(active=True).first()
                if not user_profile:
                    return {
                        'success': False,
                        'output': 'No active user profile found'
                    }
                
                user_credentials = {
                    'name': user_profile.name,
                    'email': user_profile.email,
                    'nationality': user_profile.nationality,
                    'passport_number': user_profile.passport_number
                }
                
                # Attempt booking
                booking_result = await self.bot.booking_service.attempt_booking(
                    mock_appointment, user_credentials
                )
                
                if booking_result['success']:
                    return {
                        'success': True,
                        'output': f"Booking {'simulated' if booking_result['dry_run'] else 'completed'}: {booking_result['confirmation_code']}"
                    }
                else:
                    return {
                        'success': False,
                        'output': f"Booking failed: {booking_result.get('error_message', 'Unknown error')}"
                    }
                    
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Error in book command: {e}")
            return {
                'success': False,
                'output': f'Booking error: {str(e)}'
            }
    
    async def _cmd_status(self, args) -> Dict[str, Any]:
        """Execute status command"""
        try:
            self.logger.info("Retrieving bot status...")
            
            # Initialize bot
            self.bot = AsylumBot.from_env()
            await self.bot.initialize()
            
            # Get basic status
            status_info = {
                'bot_version': '1.0.0-MVP',
                'config': {
                    'dry_run_mode': self.bot.config.dry_run_mode,
                    'monitoring_interval': self.bot.config.monitoring_interval,
                    'auto_booking_enabled': self.bot.config.auto_booking_enabled,
                    'site_url': self.bot.config.site_url
                },
                'database': {
                    'url': self.bot.config.database_url,
                    'status': 'connected'
                }
            }
            
            if args.detailed:
                # Add detailed status information
                session = self.bot.db_manager.get_session()
                try:
                    # Count records
                    user_count = session.query(UserProfile).count()
                    booking_count = session.query(BookingAttempt).count()
                    recent_bookings = session.query(BookingAttempt).filter(
                        BookingAttempt.attempted_at >= datetime.now() - timedelta(days=7)
                    ).count()
                    
                    status_info['statistics'] = {
                        'total_users': user_count,
                        'total_booking_attempts': booking_count,
                        'recent_booking_attempts': recent_bookings
                    }
                    
                    # Performance health check
                    health_result = await self.bot.perform_health_check()
                    status_info['health'] = health_result
                    
                finally:
                    session.close()
            
            return {
                'success': True,
                'output': json.dumps(status_info, indent=2, default=str)
            }
            
        except Exception as e:
            self.logger.error(f"Error in status command: {e}")
            return {
                'success': False,
                'output': f'Status error: {str(e)}'
            }
    
    def _cmd_config(self, args) -> Dict[str, Any]:
        """Execute config command"""
        try:
            config = Config.from_env()
            
            if args.show:
                # Show current configuration (without sensitive data)
                config_info = {
                    'site_url': config.site_url,
                    'monitoring_interval': config.monitoring_interval,
                    'dry_run_mode': config.dry_run_mode,
                    'auto_booking_enabled': config.auto_booking_enabled,
                    'headless_browser': config.headless_browser,
                    'database_url': config.database_url,
                    'gmail_username': config.gmail_username,
                    'gmail_password': '***hidden***' if config.gmail_password else None,
                    'recipient_email': config.recipient_email
                }
                
                return {
                    'success': True,
                    'output': json.dumps(config_info, indent=2)
                }
            
            elif args.validate:
                # Validate configuration
                bot = AsylumBot(config)
                validation = bot.validate_configuration()
                
                return {
                    'success': validation['valid'],
                    'output': json.dumps(validation, indent=2)
                }
            
            else:
                return {
                    'success': False,
                    'output': 'Please specify --show or --validate'
                }
                
        except Exception as e:
            self.logger.error(f"Error in config command: {e}")
            return {
                'success': False,
                'output': f'Config error: {str(e)}'
            }
    
    def _cmd_logs(self, args) -> Dict[str, Any]:
        """Execute logs command"""
        try:
            log_file = 'logs/asylum_bot.log'
            
            if not os.path.exists(log_file):
                return {
                    'success': False,
                    'output': f'Log file not found: {log_file}'
                }
            
            if args.follow:
                return {
                    'success': False,
                    'output': 'Follow mode not implemented in CLI. Use: tail -f logs/asylum_bot.log'
                }
            
            # Read last N lines
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter by log level if specified
            if args.level:
                filtered_lines = [line for line in lines if args.level in line]
                lines = filtered_lines
            
            # Get last N lines
            last_lines = lines[-args.tail:] if len(lines) > args.tail else lines
            
            return {
                'success': True,
                'output': ''.join(last_lines)
            }
            
        except Exception as e:
            self.logger.error(f"Error in logs command: {e}")
            return {
                'success': False,
                'output': f'Logs error: {str(e)}'
            }
    
    async def _cmd_test(self, args) -> Dict[str, Any]:
        """Execute test command"""
        try:
            self.logger.info(f"Testing component: {args.component}")
            
            test_results = {}
            
            if args.component in ['all', 'notifications']:
                # Test notifications
                try:
                    notification_service = NotificationService.from_env()
                    test_result = notification_service.test_notifications()
                    test_results['notifications'] = test_result
                except Exception as e:
                    test_results['notifications'] = {
                        'success': False,
                        'message': str(e)
                    }
            
            if args.component in ['all', 'database']:
                # Test database
                try:
                    db_manager = DatabaseManager()
                    session = db_manager.get_session()
                    session.query(UserProfile).count()
                    session.close()
                    test_results['database'] = {
                        'success': True,
                        'message': 'Database connection successful'
                    }
                except Exception as e:
                    test_results['database'] = {
                        'success': False,
                        'message': str(e)
                    }
            
            if args.component in ['all', 'scraping']:
                # Test scraping
                try:
                    from scraper import ScrapingService
                    scraping_service = ScrapingService()
                    availability = await scraping_service.scraper.check_site_availability()
                    test_results['scraping'] = {
                        'success': availability['available'],
                        'message': availability.get('error_message', 'Site is available'),
                        'response_time_ms': availability.get('response_time_ms')
                    }
                    await scraping_service.cleanup()
                except Exception as e:
                    test_results['scraping'] = {
                        'success': False,
                        'message': str(e)
                    }
            
            if args.component in ['all', 'booking']:
                # Test booking service
                try:
                    from booking import BookingService
                    booking_service = BookingService.from_env()
                    test_appointment = {
                        'date': datetime.now().date() + timedelta(days=30),
                        'time': datetime.now().time(),
                        'office_code': 'MAD001'
                    }
                    is_valid = booking_service.validate_appointment(test_appointment)
                    test_results['booking'] = {
                        'success': is_valid,
                        'message': 'Booking service validation passed' if is_valid else 'Validation failed'
                    }
                except Exception as e:
                    test_results['booking'] = {
                        'success': False,
                        'message': str(e)
                    }
            
            # Summarize results
            all_successful = all(result['success'] for result in test_results.values())
            
            return {
                'success': all_successful,
                'output': json.dumps(test_results, indent=2)
            }
            
        except Exception as e:
            self.logger.error(f"Error in test command: {e}")
            return {
                'success': False,
                'output': f'Test error: {str(e)}'
            }
    
    async def _cmd_health(self, args) -> Dict[str, Any]:
        """Execute health command"""
        try:
            self.logger.info("Performing health check...")
            
            # Initialize bot
            self.bot = AsylumBot.from_env()
            await self.bot.initialize()
            
            # Perform health check
            health_result = await self.bot.perform_health_check()
            
            if args.detailed:
                output = json.dumps(health_result, indent=2, default=str)
            else:
                # Summary output
                status = health_result['overall_status']
                component_count = len(health_result['components'])
                healthy_count = sum(1 for comp in health_result['components'].values() 
                                  if comp['status'] == 'healthy')
                
                output = f"Overall Status: {status.upper()}\n"
                output += f"Components: {healthy_count}/{component_count} healthy\n"
                
                if health_result.get('response_times'):
                    avg_response = sum(health_result['response_times'].values()) / len(health_result['response_times'])
                    output += f"Average Response Time: {avg_response:.1f}ms"
            
            return {
                'success': health_result['overall_status'] != 'unhealthy',
                'output': output
            }
            
        except Exception as e:
            self.logger.error(f"Error in health command: {e}")
            return {
                'success': False,
                'output': f'Health check error: {str(e)}'
            }

def main():
    """Main CLI entry point"""
    cli = AsylumBotCLI()
    
    # Get command line arguments
    import sys
    args = sys.argv[1:]
    
    if not args:
        print("Asylum Appointment Bot CLI")
        print("Usage: python cli.py <command> [options]")
        print("\nCommands:")
        print("  monitor    Start monitoring for appointments")
        print("  book       Attempt to book specific appointment")
        print("  status     Show bot status and statistics")
        print("  config     Configuration management")
        print("  logs       View log files")
        print("  test       Test bot components")
        print("  health     Perform health check")
        print("\nUse 'python cli.py <command> --help' for more information on each command.")
        return
    
    # Execute command
    result = cli.execute(args)
    
    # Print result
    print(result['output'])
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()
