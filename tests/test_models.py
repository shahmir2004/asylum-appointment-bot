"""
Unit tests for database models

Tests the core database models for user profiles, Madrid offices,
appointment slots, and booking attempts.
"""

import pytest
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import (
    Base, UserProfile, MadridOffice, AppointmentSlot, BookingAttempt,
    populate_default_offices
)


class TestDatabaseModels:
    """Test database models and relationships"""
    
    @pytest.fixture
    def memory_db(self):
        """Create in-memory SQLite database for testing"""
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def sample_user_profile(self, memory_db):
        """Create sample user profile for testing"""
        user = UserProfile(
            name="Test User",
            email="test@example.com",
            phone="+34612345678",
            nationality="US",
            passport_number="123456789"
        )
        memory_db.add(user)
        memory_db.commit()
        return user
    
    @pytest.fixture
    def sample_office(self, memory_db):
        """Create sample Madrid office for testing"""
        office = MadridOffice(
            office_code="MAD001",
            name="Madrid Centro Test",
            address="Test Address 123",
            is_active=True
        )
        memory_db.add(office)
        memory_db.commit()
        return office
    
    def test_user_profile_creation(self, memory_db):
        """Test UserProfile model creation and validation"""
        user = UserProfile(
            name="John Doe",
            email="john.doe@example.com",
            phone="+34600123456",
            nationality="US",
            passport_number="A12345678"
        )
        
        memory_db.add(user)
        memory_db.commit()
        
        # Test that user was created with auto-generated fields
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.name == "John Doe"
        assert user.email == "john.doe@example.com"
        assert user.phone == "+34600123456"
        assert user.nationality == "US"
        assert user.passport_number == "A12345678"
    
    def test_user_profile_relationships(self, memory_db, sample_user_profile, sample_office):
        """Test UserProfile relationships with booking attempts"""
        # Create booking attempt
        booking = BookingAttempt(
            user_id=sample_user_profile.id,
            office_id=sample_office.id,
            attempted_at=datetime.now(),
            status='success',
            appointment_date='2025-12-01',
            appointment_time='10:00',
            confirmation_code='TEST123',
            dry_run=True,
            attempt_duration_ms=1500
        )
        
        memory_db.add(booking)
        memory_db.commit()
        
        # Test relationship access
        assert len(sample_user_profile.booking_attempts) == 1
        assert sample_user_profile.booking_attempts[0].confirmation_code == 'TEST123'
    
    def test_madrid_office_creation(self, memory_db):
        """Test MadridOffice model creation"""
        office = MadridOffice(
            office_code="MAD002",
            name="Madrid Sur",
            address="Calle Test 456",
            phone="+34915551234",
            email="madrid.sur@test.com",
            is_active=True,
            notes="Test office for unit testing"
        )
        
        memory_db.add(office)
        memory_db.commit()
        
        assert office.id is not None
        assert office.created_at is not None
        assert office.office_code == "MAD002"
        assert office.name == "Madrid Sur"
        assert office.is_active is True
        assert office.notes == "Test office for unit testing"
    
    def test_appointment_slot_creation(self, memory_db, sample_office):
        """Test AppointmentSlot model creation"""
        slot = AppointmentSlot(
            office_id=sample_office.id,
            date='2025-12-15',
            time='14:30',
            detected_at=datetime.now(),
            is_available=True,
            slot_type='standard'
        )
        
        memory_db.add(slot)
        memory_db.commit()
        
        assert slot.id is not None
        assert slot.office_id == sample_office.id
        assert slot.date == '2025-12-15'
        assert slot.time == '14:30'
        assert slot.is_available is True
        assert slot.slot_type == 'standard'
    
    def test_booking_attempt_creation(self, memory_db, sample_user_profile, sample_office):
        """Test BookingAttempt model creation"""
        booking = BookingAttempt(
            user_id=sample_user_profile.id,
            office_id=sample_office.id,
            attempted_at=datetime.now(),
            status='failed',
            appointment_date='2025-12-20',
            appointment_time='09:00',
            error_type='connection_error',
            error_message='Network timeout',
            dry_run=True,
            attempt_duration_ms=3000
        )
        
        memory_db.add(booking)
        memory_db.commit()
        
        assert booking.id is not None
        assert booking.status == 'failed'
        assert booking.error_type == 'connection_error'
        assert booking.error_message == 'Network timeout'
        assert booking.dry_run is True
        assert booking.attempt_duration_ms == 3000
    
    def test_booking_attempt_response_data(self, memory_db, sample_user_profile, sample_office):
        """Test BookingAttempt response data JSON handling"""
        booking = BookingAttempt(
            user_id=sample_user_profile.id,
            office_id=sample_office.id,
            attempted_at=datetime.now(),
            status='success',
            appointment_date='2025-12-25',
            appointment_time='11:30',
            confirmation_code='XMAS2025',
            dry_run=False,
            attempt_duration_ms=2000
        )
        
        # Test setting response data
        response_data = {
            'success': True,
            'confirmation_code': 'XMAS2025',
            'appointment_details': {
                'date': '2025-12-25',
                'time': '11:30',
                'office': 'Madrid Centro'
            },
            'timestamp': '2025-12-09T10:30:00'
        }
        
        booking.set_response_data(response_data)
        memory_db.add(booking)
        memory_db.commit()
        
        # Test getting response data
        retrieved_data = booking.get_response_data()
        assert retrieved_data['success'] is True
        assert retrieved_data['confirmation_code'] == 'XMAS2025'
        assert retrieved_data['appointment_details']['date'] == '2025-12-25'
    
    def test_populate_default_offices(self, memory_db):
        """Test populating default Madrid offices"""
        populate_default_offices(memory_db)
        
        # Check that offices were created
        offices = memory_db.query(MadridOffice).all()
        assert len(offices) > 0
        
        # Check for specific expected offices
        madrid_centro = memory_db.query(MadridOffice).filter_by(office_code="MAD001").first()
        assert madrid_centro is not None
        assert madrid_centro.name == "Madrid Centro"
        assert madrid_centro.is_active is True
    
    def test_model_string_representations(self, memory_db, sample_user_profile, sample_office):
        """Test model __str__ and __repr__ methods"""
        # Test UserProfile string representation
        user_str = str(sample_user_profile)
        assert "Test User" in user_str
        assert "test@example.com" in user_str
        
        # Test MadridOffice string representation
        office_str = str(sample_office)
        assert "MAD001" in office_str
        assert "Madrid Centro Test" in office_str
        
        # Test BookingAttempt string representation
        booking = BookingAttempt(
            user_id=sample_user_profile.id,
            office_id=sample_office.id,
            attempted_at=datetime.now(),
            status='success',
            appointment_date='2025-12-01',
            appointment_time='10:00',
            confirmation_code='STR123',
            dry_run=True
        )
        memory_db.add(booking)
        memory_db.commit()
        
        booking_str = str(booking)
        assert "STR123" in booking_str or "success" in booking_str
    
    def test_model_validations(self, memory_db):
        """Test model field validations and constraints"""
        # Test duplicate office codes are handled
        office1 = MadridOffice(office_code="DUPLICATE", name="Office 1", address="Address 1")
        office2 = MadridOffice(office_code="DUPLICATE", name="Office 2", address="Address 2")
        
        memory_db.add(office1)
        memory_db.commit()
        
        memory_db.add(office2)
        
        # Should raise integrity error for duplicate office_code
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            memory_db.commit()
