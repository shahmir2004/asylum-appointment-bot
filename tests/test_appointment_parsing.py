"""
Test appointment slot parsing functionality - MUST FAIL INITIALLY (TDD)

These tests are written BEFORE implementation to ensure proper TDD compliance.
All tests should fail when first run, then pass after implementation.
"""

import pytest
import os
import sys
from datetime import datetime, date, time
from unittest.mock import Mock

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestAppointmentParsing:
    """Test appointment slot parsing and data extraction functionality"""
    
    def test_appointment_parser_initialization(self):
        """Test that appointment parser can be initialized"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        assert parser is not None
    
    def test_parse_date_formats(self):
        """Test parsing various date formats from government site"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        # Test Spanish date formats
        test_dates = [
            ('15/09/2025', date(2025, 9, 15)),
            ('01/12/2025', date(2025, 12, 1)),
            ('31/12/2025', date(2025, 12, 31)),
            ('15 de septiembre de 2025', date(2025, 9, 15)),
            ('1 de diciembre de 2025', date(2025, 12, 1))
        ]
        
        for date_str, expected_date in test_dates:
            parsed_date = parser.parse_date(date_str)
            assert parsed_date == expected_date
    
    def test_parse_time_formats(self):
        """Test parsing various time formats from government site"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        # Test Spanish time formats
        test_times = [
            ('09:30', time(9, 30)),
            ('14:15', time(14, 15)),
            ('08:00', time(8, 0)),
            ('17:45', time(17, 45)),
            ('9:30', time(9, 30)),  # Single digit hour
            ('16:00 horas', time(16, 0))  # With 'horas' suffix
        ]
        
        for time_str, expected_time in test_times:
            parsed_time = parser.parse_time(time_str)
            assert parsed_time == expected_time
    
    def test_extract_appointments_from_html(self):
        """Test extracting appointment data from HTML content"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        # Mock HTML with appointment slots
        mock_html = """
        <div class="calendar-container">
            <div class="appointment-slot available" data-date="15/09/2025" data-time="09:30">
                <span class="date">15/09/2025</span>
                <span class="time">09:30</span>
                <span class="status">Disponible</span>
            </div>
            <div class="appointment-slot available" data-date="16/09/2025" data-time="14:15">
                <span class="date">16/09/2025</span>
                <span class="time">14:15</span>
                <span class="status">Disponible</span>
            </div>
            <div class="appointment-slot unavailable" data-date="17/09/2025" data-time="10:00">
                <span class="date">17/09/2025</span>
                <span class="time">10:00</span>
                <span class="status">No disponible</span>
            </div>
        </div>
        """
        
        appointments = parser.extract_appointments_from_html(mock_html, 'MAD001')
        
        assert isinstance(appointments, list)
        assert len(appointments) == 2  # Only available appointments
        
        # Check first appointment
        apt1 = appointments[0]
        assert apt1['date'] == date(2025, 9, 15)
        assert apt1['time'] == time(9, 30)
        assert apt1['office_code'] == 'MAD001'
        assert apt1['status'] == 'available'
    
    def test_filter_available_appointments(self):
        """Test filtering only available appointments"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        all_appointments = [
            {'date': date(2025, 9, 15), 'time': time(9, 30), 'status': 'available'},
            {'date': date(2025, 9, 16), 'time': time(14, 15), 'status': 'unavailable'},
            {'date': date(2025, 9, 17), 'time': time(10, 0), 'status': 'available'},
            {'date': date(2025, 9, 18), 'time': time(16, 30), 'status': 'booked'}
        ]
        
        available = parser.filter_available_appointments(all_appointments)
        
        assert len(available) == 2
        assert all(apt['status'] == 'available' for apt in available)
    
    def test_find_earliest_appointment(self):
        """Test finding the earliest available appointment"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        appointments = [
            {'date': date(2025, 9, 17), 'time': time(10, 0), 'office_code': 'MAD001'},
            {'date': date(2025, 9, 15), 'time': time(14, 30), 'office_code': 'MAD002'},
            {'date': date(2025, 9, 15), 'time': time(9, 30), 'office_code': 'MAD003'},
            {'date': date(2025, 9, 16), 'time': time(8, 0), 'office_code': 'MAD004'}
        ]
        
        earliest = parser.find_earliest_appointment(appointments)
        
        assert earliest['date'] == date(2025, 9, 15)
        assert earliest['time'] == time(9, 30)
        assert earliest['office_code'] == 'MAD003'
    
    def test_validate_appointment_data(self):
        """Test validation of appointment data structure"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        # Valid appointment
        valid_appointment = {
            'date': date(2025, 9, 15),
            'time': time(9, 30),
            'office_code': 'MAD001',
            'status': 'available'
        }
        
        assert parser.validate_appointment(valid_appointment) is True
        
        # Invalid appointments
        invalid_appointments = [
            {'date': 'invalid', 'time': time(9, 30), 'office_code': 'MAD001'},
            {'date': date(2025, 9, 15), 'time': 'invalid', 'office_code': 'MAD001'},
            {'date': date(2025, 9, 15), 'time': time(9, 30)},  # Missing office_code
            {}  # Empty
        ]
        
        for invalid_apt in invalid_appointments:
            assert parser.validate_appointment(invalid_apt) is False
    
    def test_parse_office_information(self):
        """Test parsing office information from appointment data"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        # Mock HTML with office information
        office_html = """
        <div class="office-info">
            <h3>Madrid Centro - Asylum Office</h3>
            <p class="address">Calle Mayor, 1, 28013 Madrid</p>
            <p class="district">Centro</p>
            <span class="office-code">MAD001</span>
        </div>
        """
        
        office_info = parser.parse_office_info(office_html)
        
        assert office_info['name'] == 'Madrid Centro - Asylum Office'
        assert office_info['address'] == 'Calle Mayor, 1, 28013 Madrid'
        assert office_info['district'] == 'Centro'
        assert office_info['office_code'] == 'MAD001'
    
    def test_handle_parsing_errors(self):
        """Test handling of malformed or unexpected HTML"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        # Empty HTML
        appointments = parser.extract_appointments_from_html('', 'MAD001')
        assert appointments == []
        
        # Malformed HTML
        malformed_html = '<div><span>Broken HTML without closing tags'
        appointments = parser.extract_appointments_from_html(malformed_html, 'MAD001')
        assert isinstance(appointments, list)
        
        # HTML with missing data
        incomplete_html = '<div class="appointment-slot"><span>No date/time</span></div>'
        appointments = parser.extract_appointments_from_html(incomplete_html, 'MAD001')
        assert appointments == []
    
    def test_date_range_filtering(self):
        """Test filtering appointments within date range"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        appointments = [
            {'date': date(2025, 9, 10), 'time': time(9, 30)},  # Too early
            {'date': date(2025, 9, 15), 'time': time(10, 0)},  # In range
            {'date': date(2025, 9, 20), 'time': time(14, 30)}, # In range
            {'date': date(2025, 10, 1), 'time': time(11, 0)},  # Too late
        ]
        
        start_date = date(2025, 9, 15)
        end_date = date(2025, 9, 30)
        
        filtered = parser.filter_by_date_range(appointments, start_date, end_date)
        
        assert len(filtered) == 2
        assert all(start_date <= apt['date'] <= end_date for apt in filtered)
    
    def test_time_slot_availability_detection(self):
        """Test detecting appointment slot availability status"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        # Test various availability indicators
        availability_tests = [
            ('Disponible', True),
            ('Available', True),
            ('No disponible', False),
            ('Ocupado', False),
            ('Completo', False),
            ('Full', False),
            ('', False)  # Empty status
        ]
        
        for status_text, expected_available in availability_tests:
            is_available = parser.is_slot_available(status_text)
            assert is_available == expected_available
    
    def test_appointment_sorting(self):
        """Test sorting appointments by date and time"""
        # This will fail until appointment_parsing module is implemented
        from appointment_parsing import AppointmentParser
        
        parser = AppointmentParser()
        
        unsorted_appointments = [
            {'date': date(2025, 9, 16), 'time': time(14, 0)},
            {'date': date(2025, 9, 15), 'time': time(16, 30)},
            {'date': date(2025, 9, 15), 'time': time(9, 30)},
            {'date': date(2025, 9, 17), 'time': time(8, 0)}
        ]
        
        sorted_appointments = parser.sort_appointments(unsorted_appointments)
        
        # Should be sorted by date, then by time
        expected_order = [
            (date(2025, 9, 15), time(9, 30)),
            (date(2025, 9, 15), time(16, 30)),
            (date(2025, 9, 16), time(14, 0)),
            (date(2025, 9, 17), time(8, 0))
        ]
        
        for i, (expected_date, expected_time) in enumerate(expected_order):
            assert sorted_appointments[i]['date'] == expected_date
            assert sorted_appointments[i]['time'] == expected_time

if __name__ == "__main__":
    # Run with: python -m pytest tests/test_appointment_parsing.py -v
    pytest.main([__file__, "-v"])
