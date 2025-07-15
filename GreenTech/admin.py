from django.contrib import admin
from .models import UserProfile, Event, EventRegistration

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'age', 'address']
    search_fields = ['user__username', 'user__email', 'phone_number', 'address']
    list_filter = ['age']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'location', 'current_participants', 'max_participants', 'organizer', 'is_active']
    list_filter = ['event_type', 'date', 'is_active']
    search_fields = ['title', 'location', 'organizer__username']
    date_hierarchy = 'date'
    readonly_fields = ['current_participants', 'created_at', 'updated_at']

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registered_at', 'attended']
    list_filter = ['attended', 'registered_at', 'event__event_type']
    search_fields = ['user__username', 'event__title']
    date_hierarchy = 'registered_at'
