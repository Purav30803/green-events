from django.conf import settings
import os

def get_event_type_image(event_type):
    """
    Returns the appropriate image URL for a given event type.
    If the event has a custom image, it returns that.
    Otherwise, it returns a default image based on the event type.
    """
    # Default images for each event type
    event_type_images = {
        'tree_planting': '/static/images/event-types/tree_planting.svg',
        'cleanup': '/static/images/event-types/cleanup.svg',
        'recycling': '/static/images/event-types/recycling.svg',
        'education': '/static/images/event-types/education.svg',
        'conservation': '/static/images/event-types/conservation.svg',
        'other': '/static/images/event-types/other.svg',
    }
    
    return event_type_images.get(event_type, event_type_images['other'])

def get_event_type_icon(event_type):
    """
    Returns the appropriate Bootstrap icon class for a given event type.
    """
    event_type_icons = {
        'tree_planting': 'bi-tree-fill',
        'cleanup': 'bi-trash-fill',
        'recycling': 'bi-arrow-repeat',
        'education': 'bi-book-fill',
        'conservation': 'bi-heart-fill',
        'other': 'bi-calendar-event-fill',
    }
    
    return event_type_icons.get(event_type, event_type_icons['other'])

def get_event_type_color(event_type):
    """
    Returns the appropriate color class for a given event type.
    """
    event_type_colors = {
        'tree_planting': 'success',
        'cleanup': 'warning',
        'recycling': 'info',
        'education': 'primary',
        'conservation': 'danger',
        'other': 'secondary',
    }
    
    return event_type_colors.get(event_type, event_type_colors['other']) 