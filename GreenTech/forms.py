from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import UserProfile, Event, Contact, EventRegistration


class UserRegistrationForm(UserCreationForm):
    """Form for user registration/signup"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    address = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your address'
        })
    )
    phone_number = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number'
        })
    )
    age = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your age'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize password field widgets
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                address=self.cleaned_data.get('address', ''),
                phone_number=self.cleaned_data.get('phone_number', ''),
                age=self.cleaned_data.get('age')
            )
        return user


class UserLoginForm(forms.Form):
    """Form for user login/signin"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = ['address', 'phone_number', 'age', 'bio', 'profile_picture']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your age',
                'min': '1',
                'max': '120'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 1 or age > 120):
            raise ValidationError('Age must be between 1 and 120.')
        return age


class ContactForm(forms.ModelForm):
    """Form for contact/feedback submissions"""
    class Meta:
        model = Contact
        fields = [
            'name', 'email', 'phone_number', 'contact_type', 'subject', 'message',
            'event_title', 'event_type', 'event_date', 'event_time', 'event_location',
            'max_participants', 'event_description', 'organizer_name', 'organizer_phone',
            'special_requirements'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number (optional)'
            }),
            'contact_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'contact_type'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief subject of your message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '5',
                'placeholder': 'Your message...'
            }),
            # Event creation fields
            'event_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Community Tree Planting'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'event_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'event_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Central Park, Downtown'
            }),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 50',
                'min': '1',
                'max': '1000'
            }),
            'event_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Describe your event...'
            }),
            'organizer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name as organizer'
            }),
            'organizer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number as organizer'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Any special requirements or notes...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make event fields not required initially
        event_fields = [
            'event_title', 'event_type', 'event_date', 'event_time', 
            'event_location', 'max_participants', 'event_description',
            'organizer_name', 'organizer_phone', 'special_requirements'
        ]
        for field in event_fields:
            self.fields[field].required = False

    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < date.today():
            raise ValidationError('Event date cannot be in the past.')
        return event_date

    def clean(self):
        cleaned_data = super().clean()
        contact_type = cleaned_data.get('contact_type')
        
        # If it's an event request, make event fields required
        if contact_type == 'event_request':
            event_fields = [
                'event_title', 'event_type', 'event_date', 'event_time',
                'event_location', 'event_description', 'organizer_name'
            ]
            for field in event_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required for event creation requests.')
        
        return cleaned_data


class EventCreationForm(forms.ModelForm):
    """Form for creating events (admin use)"""
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'location', 'latitude', 'longitude',
            'date', 'start_time', 'end_time', 'max_participants', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Event description...'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event location'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitude (optional)',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitude (optional)',
                'step': 'any'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum number of participants',
                'min': '1'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_date(self):
        event_date = self.cleaned_data.get('date')
        if event_date and event_date < date.today():
            raise ValidationError('Event date cannot be in the past.')
        return event_date

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError('End time must be after start time.')
        
        return cleaned_data


class EventRegistrationForm(forms.ModelForm):
    """Form for event registration"""
    class Meta:
        model = EventRegistration
        fields = [] 

    def __init__(self, event=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        
        if self.event and self.user:
            # Check if user is already registered
            if EventRegistration.objects.filter(event=self.event, user=self.user).exists():
                raise ValidationError('You are already registered for this event.')
            
            # Check if event is full
            if self.event.is_full:
                raise ValidationError('This event is already full.')
            
            # Check if event is in the past
            if self.event.is_past_event:
                raise ValidationError('Cannot register for past events.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.event and self.user:
            instance.event = self.event
            instance.user = self.user
            if commit:
                instance.save()
                # Update event participant count
                self.event.current_participants += 1
                self.event.save()
        return instance


class ContactStatusUpdateForm(forms.ModelForm):
    """Form for updating contact status (admin use)"""
    class Meta:
        model = Contact
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Add admin notes...'
            })
        }


class EventSearchForm(forms.Form):
    """Form for searching/filtering events"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...'
        })
    )
    event_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Event.EVENT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError('Start date must be before or equal to end date.')
        
        return cleaned_data


class UserSearchForm(forms.Form):
    """Form for searching users (admin use)"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by username, email, or name...'
        })
    )
    is_active = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Users'),
            ('True', 'Active Users'),
            ('False', 'Inactive Users')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    is_staff = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Users'),
            ('True', 'Staff Users'),
            ('False', 'Regular Users')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class ContactSearchForm(forms.Form):
    """Form for searching contacts (admin use)"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or subject...'
        })
    )
    contact_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Contact.CONTACT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Contact.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError('Start date must be before or equal to end date.')
        
        return cleaned_data 