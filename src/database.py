"""
Database initialization and management for asylum appointment booking bot.

Handles:
- SQLite database setup and migrations
- Database connection management
- Data access layer operations
- Backup and maintenance utilities
"""

import sqlite3
import logging
from datetime import datetime, date, time
from typing import Dict, List, Optional, Any, Tuple
import json
import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Import models
from models import Base, DatabaseManager, UserProfile, MadridOffice, AppointmentSlot, BookingAttempt, DEFAULT_MADRID_OFFICES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Enhanced database management class for asylum bot"""
    
    def __init__(self, database_url: str = "sqlite:///asylum_bot.db"):
        """
        Initialize database manager
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.db_manager = DatabaseManager(database_url)
        self.logger = logging.getLogger(__name__)
        
        # Extract database file path for SQLite
        if database_url.startswith('sqlite:///'):
            self.db_file_path = database_url.replace('sqlite:///', '')
        else:
            self.db_file_path = None
        
        self.logger.info(f"Database initialized: {database_url}")
    
    def initialize_database(self, reset_if_exists: bool = False) -> bool:
        """
        Initialize database with tables and default data
        
        Args:
            reset_if_exists: Whether to reset database if it already exists
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing asylum bot database...")
            
            # Check if database exists
            if self.db_file_path and os.path.exists(self.db_file_path):
                if reset_if_exists:
                    self.logger.warning("Resetting existing database...")
                    os.remove(self.db_file_path)
                else:
                    self.logger.info("Database already exists, checking tables...")
            
            # Create logs directory if needed
            if self.db_file_path:
                db_dir = os.path.dirname(self.db_file_path)
                if db_dir:
                    os.makedirs(db_dir, exist_ok=True)
            
            # Create all tables
            self.db_manager.create_tables()
            self.logger.info("Database tables created successfully")
            
            # Populate with default data
            self._populate_default_data()
            
            # Verify database structure
            if self._verify_database_structure():
                self.logger.info("✅ Database initialization completed successfully")
                return True
            else:
                self.logger.error("❌ Database structure verification failed")
                return False
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def _populate_default_data(self):
        """Populate database with default data"""
        session = self.db_manager.get_session()
        try:
            self.logger.info("Populating database with default data...")
            
            # Add default Madrid offices
            self._add_default_offices(session)
            
            # Add default user profile if none exists
            self._add_default_user_profile(session)
            
            session.commit()
            self.logger.info("Default data populated successfully")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error populating default data: {e}")
            raise
        finally:
            session.close()
    
    def _add_default_offices(self, session: Session):
        """Add default Madrid offices"""
        for office_data in DEFAULT_MADRID_OFFICES:
            existing = session.query(MadridOffice).filter_by(office_code=office_data['office_code']).first()
            if not existing:
                office = MadridOffice(**office_data)
                session.add(office)
                self.logger.info(f"Added office: {office_data['office_name']}")
    
    def _add_default_user_profile(self, session: Session):
        """Add default user profile if none exists"""
        existing_user = session.query(UserProfile).filter_by(active=True).first()
        if not existing_user:
            from config import Config
            config = Config.from_env()
            
            default_user = UserProfile(
                name=config.default_user_name,
                email=config.default_user_email or config.recipient_email,
                nationality="Nigerian",
                passport_number="A12345678",
                phone="+34123456789"
            )
            default_user.set_preferred_office_codes(['MAD001'])
            
            session.add(default_user)
            self.logger.info(f"Added default user profile: {default_user.name}")
    
    def _verify_database_structure(self) -> bool:
        """Verify that all required tables exist with correct structure"""
        try:
            inspector = inspect(self.db_manager.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = ['user_profiles', 'madrid_offices', 'appointment_slots', 'booking_attempts']
            
            for table in required_tables:
                if table not in existing_tables:
                    self.logger.error(f"Missing required table: {table}")
                    return False
                
                # Verify table has columns
                columns = inspector.get_columns(table)
                if not columns:
                    self.logger.error(f"Table {table} has no columns")
                    return False
            
            self.logger.info(f"Database structure verified: {len(required_tables)} tables found")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying database structure: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        session = self.db_manager.get_session()
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'tables': {},
                'database_size_bytes': None,
                'last_modified': None
            }
            
            # Count records in each table
            stats['tables']['user_profiles'] = session.query(UserProfile).count()
            stats['tables']['madrid_offices'] = session.query(MadridOffice).count()
            stats['tables']['appointment_slots'] = session.query(AppointmentSlot).count()
            stats['tables']['booking_attempts'] = session.query(BookingAttempt).count()
            
            # Get database file info for SQLite
            if self.db_file_path and os.path.exists(self.db_file_path):
                file_stat = os.stat(self.db_file_path)
                stats['database_size_bytes'] = file_stat.st_size
                stats['last_modified'] = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {'error': str(e)}
        finally:
            session.close()
    
    def backup_database(self, backup_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create database backup
        
        Args:
            backup_path: Path for backup file (auto-generated if None)
            
        Returns:
            Dictionary with backup result
        """
        if not self.db_file_path:
            return {
                'success': False,
                'message': 'Database backup only supported for SQLite databases'
            }
        
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"asylum_bot_backup_{timestamp}.db"
            
            # Ensure backup directory exists
            backup_dir = os.path.dirname(backup_path)
            if backup_dir:
                os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup
            import shutil
            shutil.copy2(self.db_file_path, backup_path)
            
            # Verify backup
            backup_size = os.path.getsize(backup_path)
            original_size = os.path.getsize(self.db_file_path)
            
            result = {
                'success': True,
                'backup_path': backup_path,
                'backup_size_bytes': backup_size,
                'original_size_bytes': original_size,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Database backup created: {backup_path} ({backup_size} bytes)")
            return result
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def restore_database(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Dictionary with restore result
        """
        if not self.db_file_path:
            return {
                'success': False,
                'message': 'Database restore only supported for SQLite databases'
            }
        
        try:
            if not os.path.exists(backup_path):
                return {
                    'success': False,
                    'message': f'Backup file not found: {backup_path}'
                }
            
            # Create backup of current database before restore
            current_backup_result = self.backup_database(f"{self.db_file_path}.pre_restore_backup")
            
            # Restore from backup
            import shutil
            shutil.copy2(backup_path, self.db_file_path)
            
            # Verify restore
            if self._verify_database_structure():
                result = {
                    'success': True,
                    'restored_from': backup_path,
                    'pre_restore_backup': current_backup_result.get('backup_path'),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.logger.info(f"Database restored from: {backup_path}")
                return result
            else:
                return {
                    'success': False,
                    'message': 'Restored database failed structure verification'
                }
                
        except Exception as e:
            self.logger.error(f"Database restore failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Clean up old data from database
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Dictionary with cleanup result
        """
        session = self.db_manager.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            cleanup_result = {
                'success': True,
                'cutoff_date': cutoff_date.isoformat(),
                'deleted_records': {}
            }
            
            # Clean up old appointment slots
            old_slots = session.query(AppointmentSlot).filter(
                AppointmentSlot.appointment_date < cutoff_date.date()
            )
            slots_count = old_slots.count()
            old_slots.delete()
            cleanup_result['deleted_records']['appointment_slots'] = slots_count
            
            # Clean up old booking attempts (keep longer history)
            old_booking_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
            old_attempts = session.query(BookingAttempt).filter(
                BookingAttempt.attempted_at < old_booking_cutoff
            )
            attempts_count = old_attempts.count()
            old_attempts.delete()
            cleanup_result['deleted_records']['booking_attempts'] = attempts_count
            
            session.commit()
            
            total_deleted = sum(cleanup_result['deleted_records'].values())
            self.logger.info(f"Database cleanup completed: {total_deleted} records deleted")
            
            return cleanup_result
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database cleanup failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            session.close()
    
    def vacuum_database(self) -> Dict[str, Any]:
        """
        Vacuum SQLite database to reclaim space
        
        Returns:
            Dictionary with vacuum result
        """
        if not self.db_file_path:
            return {
                'success': False,
                'message': 'Database vacuum only supported for SQLite databases'
            }
        
        try:
            # Get size before vacuum
            size_before = os.path.getsize(self.db_file_path)
            
            # Perform vacuum
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("VACUUM"))
            
            # Get size after vacuum
            size_after = os.path.getsize(self.db_file_path)
            space_saved = size_before - size_after
            
            result = {
                'success': True,
                'size_before_bytes': size_before,
                'size_after_bytes': size_after,
                'space_saved_bytes': space_saved,
                'space_saved_percent': (space_saved / size_before * 100) if size_before > 0 else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Database vacuum completed: {space_saved} bytes saved ({result['space_saved_percent']:.1f}%)")
            return result
            
        except Exception as e:
            self.logger.error(f"Database vacuum failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def export_data(self, export_path: str, format: str = 'json') -> Dict[str, Any]:
        """
        Export database data to file
        
        Args:
            export_path: Path for export file
            format: Export format ('json' or 'csv')
            
        Returns:
            Dictionary with export result
        """
        session = self.db_manager.get_session()
        try:
            # Ensure export directory exists
            export_dir = os.path.dirname(export_path)
            if export_dir:
                os.makedirs(export_dir, exist_ok=True)
            
            if format.lower() == 'json':
                return self._export_to_json(session, export_path)
            elif format.lower() == 'csv':
                return self._export_to_csv(session, export_path)
            else:
                return {
                    'success': False,
                    'message': f'Unsupported export format: {format}'
                }
                
        except Exception as e:
            self.logger.error(f"Data export failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            session.close()
    
    def _export_to_json(self, session: Session, export_path: str) -> Dict[str, Any]:
        """Export data to JSON format"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'user_profiles': [user.to_dict() for user in session.query(UserProfile).all()],
            'madrid_offices': [office.to_dict() for office in session.query(MadridOffice).all()],
            'appointment_slots': [slot.to_dict() for slot in session.query(AppointmentSlot).all()],
            'booking_attempts': [attempt.to_dict() for attempt in session.query(BookingAttempt).all()]
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        file_size = os.path.getsize(export_path)
        total_records = sum(len(records) for records in export_data.values() if isinstance(records, list))
        
        self.logger.info(f"Data exported to JSON: {export_path} ({total_records} records, {file_size} bytes)")
        
        return {
            'success': True,
            'export_path': export_path,
            'format': 'json',
            'total_records': total_records,
            'file_size_bytes': file_size,
            'timestamp': datetime.now().isoformat()
        }
    
    def _export_to_csv(self, session: Session, export_path: str) -> Dict[str, Any]:
        """Export data to CSV format"""
        import csv
        
        # For CSV, we'll create separate files for each table
        base_path = export_path.rsplit('.', 1)[0]
        
        tables = {
            'user_profiles': session.query(UserProfile).all(),
            'madrid_offices': session.query(MadridOffice).all(),
            'appointment_slots': session.query(AppointmentSlot).all(),
            'booking_attempts': session.query(BookingAttempt).all()
        }
        
        exported_files = []
        total_records = 0
        
        for table_name, records in tables.items():
            if not records:
                continue
                
            csv_path = f"{base_path}_{table_name}.csv"
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                if records:
                    # Get field names from first record
                    record_dict = records[0].to_dict()
                    fieldnames = record_dict.keys()
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for record in records:
                        writer.writerow(record.to_dict())
                    
                    exported_files.append(csv_path)
                    total_records += len(records)
        
        self.logger.info(f"Data exported to CSV: {len(exported_files)} files, {total_records} records")
        
        return {
            'success': True,
            'export_files': exported_files,
            'format': 'csv',
            'total_records': total_records,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_maintenance(self) -> Dict[str, Any]:
        """
        Run complete database maintenance
        
        Returns:
            Dictionary with maintenance results
        """
        maintenance_result = {
            'success': True,
            'maintenance_timestamp': datetime.now().isoformat(),
            'operations': {}
        }
        
        try:
            # Backup database
            backup_result = self.backup_database()
            maintenance_result['operations']['backup'] = backup_result
            
            # Clean up old data
            cleanup_result = self.cleanup_old_data()
            maintenance_result['operations']['cleanup'] = cleanup_result
            
            # Vacuum database
            vacuum_result = self.vacuum_database()
            maintenance_result['operations']['vacuum'] = vacuum_result
            
            # Verify database structure
            structure_ok = self._verify_database_structure()
            maintenance_result['operations']['structure_verification'] = {
                'success': structure_ok,
                'message': 'Database structure verified' if structure_ok else 'Structure verification failed'
            }
            
            # Get final stats
            stats = self.get_database_stats()
            maintenance_result['final_stats'] = stats
            
            # Check if any operation failed
            if not all(op.get('success', True) for op in maintenance_result['operations'].values()):
                maintenance_result['success'] = False
            
            self.logger.info("Database maintenance completed")
            return maintenance_result
            
        except Exception as e:
            self.logger.error(f"Database maintenance failed: {e}")
            maintenance_result['success'] = False
            maintenance_result['error'] = str(e)
            return maintenance_result

# Convenience functions for database operations
def initialize_asylum_database(database_url: str = "sqlite:///asylum_bot.db", reset: bool = False) -> bool:
    """
    Initialize asylum bot database
    
    Args:
        database_url: Database URL
        reset: Whether to reset existing database
        
    Returns:
        bool: True if successful, False otherwise
    """
    db = Database(database_url)
    return db.initialize_database(reset_if_exists=reset)

def get_database_connection(database_url: str = "sqlite:///asylum_bot.db") -> Database:
    """
    Get database connection
    
    Args:
        database_url: Database URL
        
    Returns:
        Database instance
    """
    return Database(database_url)

def run_database_maintenance(database_url: str = "sqlite:///asylum_bot.db") -> Dict[str, Any]:
    """
    Run database maintenance
    
    Args:
        database_url: Database URL
        
    Returns:
        Dictionary with maintenance results
    """
    db = Database(database_url)
    return db.run_maintenance()
