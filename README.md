# Green Events & Volunteering Portal

A Django-based web application for discovering and signing up for local eco-friendly events and volunteering opportunities.

## Features

### 🏠 **Home Page (No Login Required)**
- Beautiful landing page with hero section
- Statistics dashboard showing total events and participants
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
- Real-time location display

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
- **Database**: SQLite (development)
- **Email**: SMTP (Gmail)

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DjangoProject
```

### 2. Install Dependencies
```bash
pip install django
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Sample Data
```bash
python manage.py create_sample_events
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

### 7. Access the Application
- **Home Page**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Events**: http://127.0.0.1:8000/events/

## Default Credentials

After running the sample data command, you can use:
- **Username**: admin
- **Password**: admin123

## Project Structure

```
DjangoProject/
├── GreenTech/                 # Main Django app
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── urls.py               # URL routing
│   ├── admin.py              # Admin interface
│   └── management/           # Custom commands
├── Iads/                     # Django project settings
│   ├── settings.py           # Project configuration
│   └── urls.py              # Main URL configuration
├── templates/                # HTML templates
│   └── GreenTech/
│       ├── base.html         # Base template
│       ├── home.html         # Home page
│       ├── events.html       # Events listing
│       ├── event_detail.html # Event details
│       ├── signin.html       # Login page
│       ├── signup.html       # Registration page
│       ├── user_profile.html # User profile
│       └── edit_profile.html # Edit profile
├── static/                   # Static files
└── media/                    # Uploaded files
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

## Deployment

For production deployment:

1. **Database**: Use PostgreSQL or MySQL
2. **Static Files**: Configure a CDN or web server
3. **Media Files**: Use cloud storage (AWS S3, etc.)
4. **Email**: Configure production email service
5. **Security**: Update `SECRET_KEY` and disable `DEBUG`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please contact the development team.

---

**Made with ❤️ for environmental conservation** 