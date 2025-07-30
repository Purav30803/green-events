from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django import template
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import get_event_type_image, get_event_type_icon, get_event_type_color

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg) if arg else 0
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


# Signal to automatically create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


class Event(models.Model):
    EVENT_TYPES = [
        ('tree_planting', 'Tree Planting'),
        ('cleanup', 'Cleanup'),
        ('recycling', 'Recycling'),
        ('education', 'Environmental Education'),
        ('conservation', 'Wildlife Conservation'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_participants = models.IntegerField(default=50)
    current_participants = models.IntegerField(default=0)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_full(self):
        return self.current_participants >= self.max_participants
    
    @property
    def available_spots(self):
        return self.max_participants - self.current_participants
    
    @property
    def is_past_event(self):
        """Check if the event date has passed"""
        return self.date < date.today()
    
    def get_event_image_url(self):
        """
        Returns the image URL for this event.
        If the event has a custom image, it returns that.
        Otherwise, it returns a default image based on the event type.
        """
        if self.image:
            return self.image.url
        return get_event_type_image(self.event_type)
    
    def get_event_icon_class(self):
        """
        Returns the Bootstrap icon class for this event type.
        """
        return get_event_type_icon(self.event_type)
    
    def get_event_color_class(self):
        """
        Returns the color class for this event type.
        """
        return get_event_type_color(self.event_type)


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Contact(models.Model):
    CONTACT_TYPES = [
        ('event_request', 'Event Creation Request'),
        ('general_inquiry', 'General Inquiry'),
        ('technical_support', 'Technical Support'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES, default='general_inquiry')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    # Event Creation Request Fields
    event_title = models.CharField(max_length=200, blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=Event.EVENT_TYPES, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    event_time = models.TimeField(blank=True, null=True)
    event_location = models.CharField(max_length=200, blank=True, null=True)
    max_participants = models.IntegerField(blank=True, null=True)
    event_description = models.TextField(blank=True, null=True)
    organizer_name = models.CharField(max_length=100, blank=True, null=True)
    organizer_phone = models.CharField(max_length=15, blank=True, null=True)
    special_requirements = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_status_display()})"
    
    @property
    def is_event_request(self):
        return self.contact_type == 'event_request'
    
    class Meta:
        ordering = ['-created_at']


class VisitorCount(models.Model):
    """Model to store the total count of unique visitors"""
    total_visitors = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Visitor Count"
        verbose_name_plural = "Visitor Count"
    
    def __str__(self):
        return f"Total Visitors: {self.total_visitors}"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Get or create the single visitor count instance"""
        obj, created = cls.objects.get_or_create(id=1, defaults={'total_visitors': 0})
        return obj
    
    @classmethod
    def increment_visitor_count(cls):
        """Increment the visitor count by 1"""
        visitor_count = cls.get_or_create_singleton()
        visitor_count.total_visitors += 1
        visitor_count.save()
        return visitor_count.total_visitors

