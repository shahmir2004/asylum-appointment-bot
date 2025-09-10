"""
Database models for asylum appointment booking bot.

This module defines SQLAlchemy models for:
- UserProfile: User information and credentials
- MadridOffice: Available government offices in Madrid
- AppointmentSlot: Available appointment time slots
- BookingAttempt: Record of booking attempts and results
"""

from datetime import datetime, date, time
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Time, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

Base = declarative_base()

class UserProfile(Base):
    """User profile with personal information and credentials"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    nationality = Column(String(50), nullable=False)
    passport_number = Column(String(20), nullable=False)
    
    # Government site credentials
    username = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)
    
    # Preferences
    preferred_office_codes = Column(Text, nullable=True)  # JSON array of office codes
    earliest_acceptable_date = Column(Date, nullable=True)
    latest_acceptable_date = Column(Date, nullable=True)
    preferred_times = Column(Text, nullable=True)  # JSON array of time preferences
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    booking_attempts = relationship("BookingAttempt", back_populates="user")
    
    def set_preferred_office_codes(self, codes):
        """Set preferred office codes as JSON"""
        self.preferred_office_codes = json.dumps(codes) if codes else None
    
    def get_preferred_office_codes(self):
        """Get preferred office codes from JSON"""
        return json.loads(self.preferred_office_codes) if self.preferred_office_codes else []
    
    def set_preferred_times(self, times):
        """Set preferred times as JSON (list of HH:MM strings)"""
        self.preferred_times = json.dumps(times) if times else None
    
    def get_preferred_times(self):
        """Get preferred times from JSON"""
        return json.loads(self.preferred_times) if self.preferred_times else []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'nationality': self.nationality,
            'passport_number': self.passport_number,
            'preferred_office_codes': self.get_preferred_office_codes(),
            'earliest_acceptable_date': self.earliest_acceptable_date.isoformat() if self.earliest_acceptable_date else None,
            'latest_acceptable_date': self.latest_acceptable_date.isoformat() if self.latest_acceptable_date else None,
            'preferred_times': self.get_preferred_times(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'active': self.active
        }

class MadridOffice(Base):
    """Madrid government offices where appointments can be booked"""
    __tablename__ = 'madrid_offices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    office_code = Column(String(20), nullable=False, unique=True)
    office_name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    district = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Site-specific identifiers
    site_office_id = Column(String(50), nullable=True)  # ID used on government site
    booking_url = Column(Text, nullable=True)  # Direct URL for booking
    
    # Operational info
    operating_hours = Column(Text, nullable=True)  # JSON with schedule
    available_services = Column(Text, nullable=True)  # JSON array of services
    
    # Metadata
    active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointment_slots = relationship("AppointmentSlot", back_populates="office")
    booking_attempts = relationship("BookingAttempt", back_populates="office")
    
    def set_operating_hours(self, hours):
        """Set operating hours as JSON"""
        self.operating_hours = json.dumps(hours) if hours else None
    
    def get_operating_hours(self):
        """Get operating hours from JSON"""
        return json.loads(self.operating_hours) if self.operating_hours else {}
    
    def set_available_services(self, services):
        """Set available services as JSON"""
        self.available_services = json.dumps(services) if services else None
    
    def get_available_services(self):
        """Get available services from JSON"""
        return json.loads(self.available_services) if self.available_services else []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'office_code': self.office_code,
            'office_name': self.office_name,
            'address': self.address,
            'district': self.district,
            'phone': self.phone,
            'site_office_id': self.site_office_id,
            'operating_hours': self.get_operating_hours(),
            'available_services': self.get_available_services(),
            'active': self.active,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AppointmentSlot(Base):
    """Available appointment time slots at Madrid offices"""
    __tablename__ = 'appointment_slots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    office_id = Column(Integer, ForeignKey('madrid_offices.id'), nullable=False)
    
    # Appointment timing
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=30)
    
    # Availability
    available = Column(Boolean, default=True)
    max_capacity = Column(Integer, default=1)
    current_bookings = Column(Integer, default=0)
    
    # Site-specific data
    site_slot_id = Column(String(100), nullable=True)  # ID used on government site
    booking_link = Column(Text, nullable=True)  # Direct booking link
    
    # Metadata
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    times_detected = Column(Integer, default=1)
    
    # Relationships
    office = relationship("MadridOffice", back_populates="appointment_slots")
    booking_attempts = relationship("BookingAttempt", back_populates="appointment_slot")
    
    @property
    def is_available(self):
        """Check if slot is still available"""
        return self.available and self.current_bookings < self.max_capacity
    
    @property
    def appointment_datetime(self):
        """Get combined datetime from date and time"""
        return datetime.combine(self.appointment_date, self.appointment_time)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'office_id': self.office_id,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_time': self.appointment_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'available': self.available,
            'max_capacity': self.max_capacity,
            'current_bookings': self.current_bookings,
            'site_slot_id': self.site_slot_id,
            'first_detected': self.first_detected.isoformat() if self.first_detected else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'times_detected': self.times_detected
        }

class BookingAttempt(Base):
    """Record of booking attempts and their results"""
    __tablename__ = 'booking_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    office_id = Column(Integer, ForeignKey('madrid_offices.id'), nullable=False)
    appointment_slot_id = Column(Integer, ForeignKey('appointment_slots.id'), nullable=True)
    
    # Attempt details
    attempted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False)  # 'success', 'failed', 'dry_run', 'pending'
    
    # Booking details
    appointment_date = Column(Date, nullable=True)
    appointment_time = Column(Time, nullable=True)
    confirmation_code = Column(String(100), nullable=True)
    
    # Result details
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    response_data = Column(Text, nullable=True)  # JSON response from site
    
    # Metadata
    dry_run = Column(Boolean, default=True)  # MVP safety flag
    attempt_duration_ms = Column(Integer, nullable=True)  # Time taken for attempt
    retry_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("UserProfile", back_populates="booking_attempts")
    office = relationship("MadridOffice", back_populates="booking_attempts")
    appointment_slot = relationship("AppointmentSlot", back_populates="booking_attempts")
    
    @property
    def was_successful(self):
        """Check if booking attempt was successful"""
        return self.status == 'success'
    
    @property
    def appointment_datetime(self):
        """Get combined datetime from date and time"""
        if self.appointment_date and self.appointment_time:
            return datetime.combine(self.appointment_date, self.appointment_time)
        return None
    
    def set_response_data(self, data):
        """Set response data as JSON"""
        self.response_data = json.dumps(data) if data else None
    
    def get_response_data(self):
        """Get response data from JSON"""
        return json.loads(self.response_data) if self.response_data else {}
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'office_id': self.office_id,
            'appointment_slot_id': self.appointment_slot_id,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None,
            'status': self.status,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.isoformat() if self.appointment_time else None,
            'confirmation_code': self.confirmation_code,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'response_data': self.get_response_data(),
            'dry_run': self.dry_run,
            'attempt_duration_ms': self.attempt_duration_ms,
            'retry_count': self.retry_count
        }

# Database connection and session management
class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url="sqlite:///asylum_bot.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all tables (for testing)"""
        Base.metadata.drop_all(bind=self.engine)

# Default Madrid offices for MVP
DEFAULT_MADRID_OFFICES = [
    {
        'office_code': 'MAD001',
        'office_name': 'Madrid Centro',
        'address': 'Calle de la Montera, 20, 28013 Madrid',
        'district': 'Centro',
        'phone': '+34 915 123 456',
        'site_office_id': 'madrid_centro_001'
    },
    {
        'office_code': 'MAD002', 
        'office_name': 'Madrid Norte',
        'address': 'Calle de Bravo Murillo, 101, 28003 Madrid',
        'district': 'Tetuán',
        'phone': '+34 915 123 457',
        'site_office_id': 'madrid_norte_002'
    },
    {
        'office_code': 'MAD003',
        'office_name': 'Madrid Sur',
        'address': 'Calle de Embajadores, 155, 28012 Madrid', 
        'district': 'Centro',
        'phone': '+34 915 123 458',
        'site_office_id': 'madrid_sur_003'
    }
]

def populate_default_offices(session):
    """Populate database with default Madrid offices"""
    for office_data in DEFAULT_MADRID_OFFICES:
        existing = session.query(MadridOffice).filter_by(office_code=office_data['office_code']).first()
        if not existing:
            office = MadridOffice(**office_data)
            session.add(office)
    session.commit()
