# This file is kept for potential future use
# All admin functionality is now handled by custom views in views.py

from django.contrib import admin
from .models import Event, EventRegistration, UserProfile, Contact, VisitorCount

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_type', 'subject', 'status', 'created_at')
    list_filter = ('contact_type', 'status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message', 'event_title', 'organizer_name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone_number', 'contact_type')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Event Creation Details', {
            'fields': ('event_title', 'event_type', 'event_date', 'event_time', 'event_location', 
                      'max_participants', 'event_description', 'organizer_name', 'organizer_phone', 
                      'special_requirements'),
            'classes': ('collapse',),
            'description': 'These fields are only used for Event Creation Requests'
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if obj and obj.contact_type == 'event_request':
            # Show event fields for event requests
            return self.fieldsets
        else:
            # Hide event fields for other contact types
            fieldsets = list(self.fieldsets)
            fieldsets[2] = ('Event Creation Details', {
                'fields': ('event_title', 'event_type', 'event_date', 'event_time', 'event_location', 
                          'max_participants', 'event_description', 'organizer_name', 'organizer_phone', 
                          'special_requirements'),
                'classes': ('collapse',),
                'description': 'These fields are only used for Event Creation Requests'
            })
            return fieldsets

@admin.register(VisitorCount)
class VisitorCountAdmin(admin.ModelAdmin):
    list_display = ('total_visitors', 'last_updated')
    readonly_fields = ('total_visitors', 'last_updated')
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not VisitorCount.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
