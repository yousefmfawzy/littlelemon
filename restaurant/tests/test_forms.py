from restaurant.forms import BookingForm
from restaurant.models import Booking, Menu , Category
from django.test import TestCase , Client
from django.urls import reverse

class TestBookingForm(TestCase):
    
    def test_valid_form(self):
        form_data= {
            'first_name':"test_name",
            'reservation_date':'2025-03-15',
            'reservation_slot':11 
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())    
    
    def test_missing_fields(self):
        form = BookingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)  # Ensure errors exist
        self.assertIn('reservation_date', form.errors)
        self.assertIn('reservation_slot', form.errors)
    
    def test_invalid_reservation_date(self):
        """Test form validation when an invalid date is provided"""
        form_data = {
            'first_name': 'Alice',
            'reservation_date': 'invalid-date',  # ❌ Incorrect format
            'reservation_slot': 3
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())  # ❌ Should fail
        self.assertIn('reservation_date', form.errors)

    def test_negative_reservation_slot(self):
        """Test if a negative reservation slot is rejected"""
        form_data = {
            'first_name': 'Charlie',
            'reservation_date': '2025-05-10',
            'reservation_slot': -1  # ❌ Invalid value
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())  # ❌ Should fail
        self.assertIn('reservation_slot', form.errors)