from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import VisitorCount


class VisitorTrackingTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_visitor_tracking(self):
        """Test that visitor count increases for new visitors"""
        # Get initial count
        initial_count = VisitorCount.get_or_create_singleton().total_visitors
        
        # First visit should increment count
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check if visitor cookie is set
        self.assertIn('visitor_id', response.cookies)
        
        # Count should be incremented
        new_count = VisitorCount.get_or_create_singleton().total_visitors
        self.assertEqual(new_count, initial_count + 1)
        
        # Second visit with same cookie should not increment
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Count should remain the same
        final_count = VisitorCount.get_or_create_singleton().total_visitors
        self.assertEqual(final_count, new_count)
    
    def test_visitor_count_display(self):
        """Test that visitor count is displayed in template"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Visitors')
        self.assertContains(response, '0')  # Should show 0 initially
