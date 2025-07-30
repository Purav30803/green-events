# Green Events & Volunteering Portal

A Django-based web application for discovering and signing up for local eco-friendly events and volunteering opportunities.

## Features

### 🏠 **Home Page (No Login Required)**

- Beautiful landing page with hero section
- Featured upcoming events
- Information about the platform's benefits

### 📅 **Event Discovery**

- Browse all available events without login
- Filter events by type, location, and date
- Pagination for better user experience
- Event cards with key information

### 🗺️ **Map Integration**

- Interactive maps using Leaflet.js
- Event location markers
- Location display of the place where the event is happening

### 👤 **User Authentication**

- User registration with email verification
- Secure login/logout functionality
- Profile management with photo upload

### 📋 **Event Registration**

- Register for events (login required)
- View registration status
- Cancel registrations
- Track event capacity

### 👤 **User Profiles**

- Personal profile with bio and contact info
- Volunteering history tracking
- Upcoming and past events
- Profile picture upload

### 🎨 **Modern UI/UX**

- Responsive Bootstrap 5 design
- Beautiful green theme
- Interactive elements and animations
- Mobile-friendly interface

## Technology Stack

- **Backend**: Django 5.2.4
- **Frontend**: Bootstrap 5.3.0, Bootstrap Icons
- **Maps**: Leaflet.js
- **Database**: PostgreSQL
- **Email**: SMTP (Gmail)

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/Purav30803/green-events.git
cd DjangoProject
```

### 2. Create & activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env file

Replace all these variables with the actual values

```bash
EMAIL_HOST_USER= #abc@def.com
EMAIL_HOST_PASSWORD= #abcb qbdd djdd djdjd
EMAIL_HOST= #smtp.example.com
EMAIL_PORT= #587
DB_ENGINE= #django.db.backends.YOURDB
DB_NAME= #example_name
DB_USER= #example_user
DB_PASSWORD= #password
DB_HOST= #host of db
DB_PORT= #5432
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin

```bash
python manage.py setup_admin
```

### 7. Create Sample Events (Optional)

To populate the system with sample events:

```bash
python manage.py create_sample_events
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

### 9. Access the Application

- **Home Page**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Events**: http://127.0.0.1:8000/events/

## Default Credentials

After running the setup_admin command, you can use:

- **Username**: admin
- **Password**: admin123

## Project Structure
```bash
DjangoProject/
├── .git/                     # Git version control
├── .idea/                    # IDE configuration
├── .venv/                    # Python virtual environment
├── .gitignore                # Git ignore file
├── requirements.txt           # Python dependencies
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── README.md                # Project documentation
├── ADMIN_SETUP.md           # Admin setup instructions
│
├── Iads/                    # Django project settings
│   ├── __init__.py
│   ├── asgi.py             # ASGI configuration
│   ├── settings.py         # Project configuration
│   ├── tokens.py           # Email token generation
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
│
├── GreenTech/              # Main Django app
│   ├── __init__.py
│   ├── admin.py           # Admin interface configuration
│   ├── apps.py            # App configuration
│   ├── decorators.py      # Custom decorators
│   ├── forms.py           # Django forms (12 forms)
│   ├── models.py          # Database models (5 models)
│   ├── tests.py           # Unit tests
│   ├── urls.py            # URL routing
│   ├── utils.py           # Utility functions
│   ├── views.py           # View classes (28 views)
│   │
│   ├── migrations/        # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_event_eventregistration_userprofile_and_more.py
│   │   ├── 0003_contact.py
│   │   ├── 0004_contact_event_fields.py
│   │   └── 0005_visitorcount.py
│   │
│   └── management/        # Custom management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           ├── create_sample_events.py
│           ├── init_visitor_count.py
│           └── setup_admin.py
│
├── templates/              # HTML templates
│   ├── activation_failed.html
│   ├── email_confirmation.html
│   └── GreenTech/         # App-specific templates (24 templates)
│       ├── about.html
│       ├── account.html
│       ├── admin_contact_detail.html
│       ├── admin_contacts.html
│       ├── admin_create_event.html
│       ├── admin_dashboard.html
│       ├── admin_event_detail.html
│       ├── admin_events.html
│       ├── admin_nav.html
│       ├── admin_registrations.html
│       ├── admin_users.html
│       ├── base.html
│       ├── contact.html
│       ├── edit_profile.html
│       ├── event_detail.html
│       ├── events.html
│       ├── home.html
│       ├── password_reset_confirm.html
│       ├── password_reset_email.html
│       ├── password_reset_request.html
│       ├── signin.html
│       ├── signup.html
│       └── user_profile.html
│
├── static/                 # Static files
│   ├── css/
│   │   ├── dash.css
│   │   └── style.css
│   └── images/
│       └── event-types/
│           ├── cleanup.svg
│           ├── conservation.svg
│           ├── education.svg
│           ├── other.svg
│           ├── recycling.svg
│           └── tree_planting.svg
│
└── media/                  # Uploaded files
    └── profile_pics/
```
## Key Features Explained

### 1. **No Login Required for Browsing**

- Users can view all events without creating an account
- Home page is accessible to everyone
- Event details and maps are publicly available

### 2. **Login Required for Registration**

- Users must sign in to register for events
- Secure authentication system
- Email verification for new accounts

### 3. **Event Management**

- Different event types (Tree Planting, Cleanup, Recycling, etc.)
- Location tracking with coordinates
- Capacity management
- Date and time scheduling

### 4. **User Experience**

- Responsive design works on all devices
- Intuitive navigation
- Clear call-to-action buttons
- Professional green theme

### 5. **Map Integration**

- Interactive maps show event locations
- Click markers for event details
- Real-time location data

## Customization

### Adding New Event Types

Edit `GreenTech/models.py` and add new choices to the `EVENT_TYPES` list.

### Styling Changes

Modify the CSS in `templates/GreenTech/base.html` or create custom CSS files.

### Email Configuration

Update email settings in `Iads/settings.py` for production use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For support or questions, please contact the development team.

---

**Made with ❤️ for environmental conservation**
