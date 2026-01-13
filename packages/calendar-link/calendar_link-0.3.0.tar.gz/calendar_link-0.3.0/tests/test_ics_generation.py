"""Tests for ICS file generation using icalendar library."""

import pytest
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import icalendar

from calendar_link import CalendarEvent, CalendarGenerator
from calendar_link.exceptions import InvalidEventDataError


class TestICSGeneration:
    """Test ICS file generation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = CalendarGenerator()
        self.base_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo('America/New_York'))
        
    def test_basic_ics_generation(self):
        """Test basic ICS file generation."""
        event = CalendarEvent(
            title="Test Meeting",
            start_time=self.base_time,
            end_time=self.base_time + timedelta(hours=1),
            description="Test description",
            location="Test Location"
        )
        
        ics_content = self.generator.generate_ics(event)
        
        # Verify it's valid iCalendar format
        cal = icalendar.Calendar.from_ical(ics_content)
        
        # Check calendar properties
        assert cal.get('prodid') == '-//Calendar Link Generator//EN'
        assert cal.get('version') == '2.0'
        assert cal.get('calscale') == 'GREGORIAN'
        assert cal.get('method') == 'PUBLISH'
        
        # Check event
        events = list(cal.walk('vevent'))
        assert len(events) == 1
        
        ical_event = events[0]
        assert ical_event.get('summary') == "Test Meeting"
        assert ical_event.get('description') == "Test description"
        assert ical_event.get('location') == "Test Location"
        
    def test_all_day_event_ics(self):
        """Test ICS generation for all-day events."""
        event = CalendarEvent(
            title="All Day Event",
            start_time=datetime(2024, 1, 15, 0, 0, 0, tzinfo=ZoneInfo('UTC')),
            end_time=datetime(2024, 1, 16, 0, 0, 0, tzinfo=ZoneInfo('UTC')),
            all_day=True
        )
        
        ics_content = self.generator.generate_ics(event)
        cal = icalendar.Calendar.from_ical(ics_content)
        
        events = list(cal.walk('vevent'))
        ical_event = events[0]
        
# For all-day events, should be DATE format
        assert isinstance(ical_event.get('dtstart').dt, date)
        assert isinstance(ical_event.get('dtend').dt, date)
        
    def test_timezone_handling(self):
        """Test proper timezone handling in ICS files."""
        # Test with explicit timezone
        event = CalendarEvent(
            title="Timezone Test",
            start_time=datetime(2024, 1, 15, 10, 0, 0),
            end_time=datetime(2024, 1, 15, 11, 0, 0),
            timezone="America/New_York"
        )
        
        ics_content = self.generator.generate_ics(event)
        cal = icalendar.Calendar.from_ical(ics_content)
        
        events = list(cal.walk('vevent'))
        ical_event = events[0]
        
        # Should have timezone info
        start_dt = ical_event.get('dtstart').dt
        assert start_dt.tzinfo is not None
        
    def test_utc_timezone_fallback(self):
        """Test UTC fallback when no timezone specified."""
        event = CalendarEvent(
            title="UTC Test",
            start_time=datetime(2024, 1, 15, 10, 0, 0),  # No timezone
            end_time=datetime(2024, 1, 15, 11, 0, 0)
        )
        
        ics_content = self.generator.generate_ics(event)
        cal = icalendar.Calendar.from_ical(ics_content)
        
        events = list(cal.walk('vevent'))
        ical_event = events[0]
        
        # Should default to UTC
        start_dt = ical_event.get('dtstart').dt
        assert start_dt.tzinfo is not None
        
    def test_attendees_in_ics(self):
        """Test attendees are properly included in ICS."""
        event = CalendarEvent(
            title="Meeting with Attendees",
            start_time=self.base_time,
            end_time=self.base_time + timedelta(hours=1),
            attendees=["test@example.com", "user2@example.com"]
        )
        
        ics_content = self.generator.generate_ics(event)
        cal = icalendar.Calendar.from_ical(ics_content)
        
        events = list(cal.walk('vevent'))
        ical_event = events[0]
        
        attendees = ical_event.get('attendee')
        if isinstance(attendees, list):
            assert len(attendees) == 2
        else:
            # Single attendee
            assert attendees is not None
        
    def test_uid_generation(self):
        """Test unique ID generation for events."""
        event = CalendarEvent(
            title="Unique ID Test",
            start_time=self.base_time,
            end_time=self.base_time + timedelta(hours=1)
        )
        
        ics_content = self.generator.generate_ics(event)
        cal = icalendar.Calendar.from_ical(ics_content)
        
        events = list(cal.walk('vevent'))
        ical_event = events[0]
        
        uid = ical_event.get('uid')
        assert uid is not None
        assert "Unique_ID_Test" in uid
        assert "@calendar-link-generator" in uid
        
    def test_ics_output_format(self):
        """Test ICS output is properly formatted string."""
        event = CalendarEvent(
            title="Format Test",
            start_time=self.base_time,
            end_time=self.base_time + timedelta(hours=1)
        )
        
        ics_content = self.generator.generate_ics(event)
        
        # Should be a string
        assert isinstance(ics_content, str)
        
        # Should start with BEGIN:VCALENDAR
        assert ics_content.startswith("BEGIN:VCALENDAR")
        
        # Should end with END:VCALENDAR
        assert ics_content.rstrip().endswith("END:VCALENDAR")
        
        # Should contain required components
        assert "BEGIN:VEVENT" in ics_content
        assert "END:VEVENT" in ics_content
        assert "VERSION:2.0" in ics_content
        
    def test_minimal_event_ics(self):
        """Test ICS generation with minimal event data."""
        event = CalendarEvent(
            title="Minimal Event",
            start_time=self.base_time,
            end_time=self.base_time + timedelta(hours=1)
        )
        
        ics_content = self.generator.generate_ics(event)
        cal = icalendar.Calendar.from_ical(ics_content)
        
        # Should still be valid
        events = list(cal.walk('vevent'))
        assert len(events) == 1
        
        ical_event = events[0]
        assert ical_event.get('summary') == "Minimal Event"
        
    def test_ensure_timezone_method(self):
        """Test the _ensure_timezone helper method."""
        # Test with timezone already set
        dt_with_tz = datetime(2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo('UTC'))
        result = self.generator._ensure_timezone(dt_with_tz)
        assert result.tzinfo is not None
        
        # Test without timezone
        dt_without_tz = datetime(2024, 1, 15, 10, 0, 0)
        result = self.generator._ensure_timezone(dt_without_tz)
        assert result.tzinfo is not None
        assert str(result.tzinfo) == 'UTC'
        
        # Test with explicit timezone
        result = self.generator._ensure_timezone(dt_without_tz, "America/New_York")
        assert result.tzinfo is not None
        assert str(result.tzinfo) == 'America/New_York'
        
    def test_invalid_timezone_fallback(self):
        """Test fallback to UTC for invalid timezone."""
        dt_without_tz = datetime(2024, 1, 15, 10, 0, 0)
        result = self.generator._ensure_timezone(dt_without_tz, "Invalid/Timezone")
        assert result.tzinfo is not None
        assert str(result.tzinfo) == 'UTC'


class TestICSValidation:
    """Test ICS file validation and RFC compliance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = CalendarGenerator()
        
    def test_rfc5545_compliance(self):
        """Test basic RFC 5545 compliance."""
        event = CalendarEvent(
            title="RFC Compliance Test",
            start_time=datetime(2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo('UTC')),
            end_time=datetime(2024, 1, 15, 11, 0, 0, tzinfo=ZoneInfo('UTC')),
            description="Test event for RFC compliance"
        )
        
        ics_content = self.generator.generate_ics(event)
        
        # Parse with icalendar to verify compliance
        cal = icalendar.Calendar.from_ical(ics_content)
        
        # Required properties for VCALENDAR
        assert cal.get('version') == '2.0'
        assert cal.get('prodid') is not None
        
        # Required properties for VEVENT
        events = list(cal.walk('vevent'))
        assert len(events) == 1
        
        ical_event = events[0]
        assert ical_event.get('uid') is not None
        assert ical_event.get('dtstamp') is not None
        assert ical_event.get('dtstart') is not None
        assert ical_event.get('dtend') is not None
        assert ical_event.get('summary') is not None