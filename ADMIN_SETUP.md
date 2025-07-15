# GreenTech Admin Panel Setup Guide

## Overview

The GreenTech admin panel provides a comprehensive interface for managing environmental events, user registrations, and user profiles. It includes both the standard Django admin and a custom GreenTech-specific admin interface.

## Setup Instructions

### 1. Initial Setup

Run the following command to set up admin users and initial data:

```bash
python manage.py setup_admin
```

This will create:
- A superuser account (username: `admin`, password: `admin123`)
- A GreenTech admin account (username: `greentech_admin`, password: `greentech123`)

### 2. Create Sample Events (Optional)

To populate the system with sample events:

```bash
python manage.py create_sample_events
```

### 3. Run the Development Server

```bash
python manage.py runserver
```

## Admin Panel Access

### Main Django Admin
- **URL**: `http://localhost:8000/admin/`
- **Access**: Superuser account
- **Features**: Full Django admin access including all models

### GreenTech Custom Admin
- **URL**: `http://localhost:8000/greentech-admin/`
- **Access**: Staff users
- **Features**: Customized interface specifically for GreenTech event management

## Admin Panel Features

### Event Management

#### List View Features:
- **Event Title**: Click to edit individual events
- **Event Type**: Filter by event category (Tree Planting, Cleanup, etc.)
- **Date**: Chronological listing with date hierarchy
- **Location**: Searchable location field
- **Participants**: Real-time participant count with color coding
- **Organizer**: Event creator information
- **Status**: Active/Inactive status with visual indicators
- **Created Date**: Timestamp of event creation

#### Event Actions:
- **Activate Events**: Bulk activate selected events
- **Deactivate Events**: Bulk deactivate selected events
- **Duplicate Events**: Create copies of existing events

#### Event Details:
- **Basic Information**: Title, description, event type, image
- **Location & Timing**: Address, coordinates, date, start/end times
- **Capacity & Participants**: Max participants, current count, participant list
- **Organizer & Status**: Event organizer and active status
- **Timestamps**: Creation and update times

### Registration Management

#### List View Features:
- **User**: Participant information
- **Event**: Associated event details
- **Event Type**: Category of the event
- **Registration Date**: When user registered
- **Attendance**: Visual attendance status
- **Event Date**: When the event occurs

#### Registration Actions:
- **Mark Attended**: Bulk mark registrations as attended
- **Mark Not Attended**: Bulk mark registrations as not attended

### User Profile Management

#### Profile Features:
- **User Information**: Basic user details, age, bio
- **Contact Information**: Phone number, address
- **Profile Picture**: User avatar management

## Advanced Features

### Search and Filtering
- **Search**: Search across titles, descriptions, locations, and user information
- **Filters**: Filter by event type, date, status, attendance, and more
- **Date Hierarchy**: Navigate events by date ranges

### Bulk Operations
- **Multi-select**: Select multiple events/registrations for bulk operations
- **Bulk Actions**: Apply actions to multiple items simultaneously
- **Status Updates**: Quickly activate/deactivate multiple events

### Data Export
- **CSV Export**: Export event and registration data
- **Date Filtering**: Export data for specific date ranges

## Customization

### Adding New Event Types
To add new event types, modify the `EVENT_TYPES` choices in `GreenTech/models.py`:

```python
EVENT_TYPES = [
    ('tree_planting', 'Tree Planting'),
    ('cleanup', 'Cleanup'),
    ('recycling', 'Recycling'),
    ('education', 'Environmental Education'),
    ('conservation', 'Wildlife Conservation'),
    ('your_new_type', 'Your New Type'),  # Add new types here
    ('other', 'Other'),
]
```

### Customizing Admin Display
Modify the admin classes in `GreenTech/admin.py` to:
- Add new list display fields
- Customize filters
- Add new actions
- Modify field layouts

## Security Considerations

### User Permissions
- **Superuser**: Full access to all Django admin features
- **Staff Users**: Access to GreenTech admin panel
- **Regular Users**: No admin access

### Data Protection
- **Read-only Fields**: Critical fields like participant counts are read-only
- **Validation**: Form validation prevents invalid data entry
- **Audit Trail**: Creation and update timestamps are automatically tracked

## Troubleshooting

### Common Issues

1. **Admin Panel Not Accessible**
   - Ensure you're logged in with a staff account
   - Check that the user has `is_staff=True`

2. **Events Not Showing**
   - Verify events are marked as `is_active=True`
   - Check date filters in the admin interface

3. **Registration Issues**
   - Ensure users are properly authenticated
   - Check event capacity limits

### Support Commands

```bash
# Reset admin password
python manage.py changepassword admin

# Create new superuser
python manage.py createsuperuser

# Check database migrations
python manage.py showmigrations

# Run database migrations
python manage.py migrate
```

## API Integration

The admin panel works seamlessly with the GreenTech API endpoints:
- Event creation/editing via admin updates the API
- Registration management syncs with user interfaces
- Profile updates reflect across the platform

For more information about the API, see the main README.md file. 