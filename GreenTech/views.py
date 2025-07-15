from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import date
from .models import Event, EventRegistration, UserProfile
from .decorators import *
from Iads import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from Iads.tokens import generate_token
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from .models import Event, EventRegistration, UserProfile
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json


def home(request):
    """Home page - accessible without login"""
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        date__gte=date.today(),
        is_active=True
    ).order_by('date', 'start_time')[:6]
    
    # Get event statistics
    total_events = Event.objects.filter(is_active=True).count()
    total_participants = EventRegistration.objects.count()
    
    context = {
        'upcoming_events': upcoming_events,
        'total_events': total_events,
        'total_participants': total_participants,
    }
    return render(request, "GreenTech/home.html", context)


def events(request):
    """Events listing page - accessible without login"""
    events_list = Event.objects.filter(is_active=True).order_by('date', 'start_time')
    
    # Filtering
    event_type = request.GET.get('event_type')
    location = request.GET.get('location')
    date_filter = request.GET.get('date')
    
    if event_type:
        events_list = events_list.filter(event_type=event_type)
    if location:
        events_list = events_list.filter(location__icontains=location)
    if date_filter:
        events_list = events_list.filter(date=date_filter)
    
    # Pagination
    paginator = Paginator(events_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'event_types': Event.EVENT_TYPES,
        'current_filters': {
            'event_type': event_type,
            'location': location,
            'date': date_filter,
        }
    }
    return render(request, "GreenTech/events.html", context)


def event_detail(request, event_id):
    """Event detail page - accessible without login"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    is_registered = False
    registration = None
    
    if request.user.is_authenticated:
        registration = EventRegistration.objects.filter(event=event, user=request.user).first()
        is_registered = registration is not None
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'registration': registration,
    }
    return render(request, "GreenTech/event_detail.html", context)


@login_required(login_url='signin')
def register_for_event(request, event_id):
    """Register user for an event"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    
    if request.method == 'POST':
        # Check if already registered
        if EventRegistration.objects.filter(event=event, user=request.user).exists():
            messages.warning(request, "You are already registered for this event!")
            return redirect('event_detail', event_id=event_id)
        
        # Check if event is full
        if event.is_full:
            messages.error(request, "Sorry, this event is full!")
            return redirect('event_detail', event_id=event_id)
        
        # Create registration
        registration = EventRegistration.objects.create(
            event=event,
            user=request.user
        )
        
        # Update event participant count
        event.current_participants += 1
        event.save()
        
        messages.success(request, f"Successfully registered for {event.title}!")
        return redirect('event_detail', event_id=event_id)
    
    return redirect('event_detail', event_id=event_id)


@login_required(login_url='signin')
def unregister_from_event(request, event_id):
    """Unregister user from an event"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    
    if request.method == 'POST':
        registration = EventRegistration.objects.filter(event=event, user=request.user).first()
        
        if registration:
            registration.delete()
            
            # Update event participant count
            event.current_participants = max(0, event.current_participants - 1)
            event.save()
            
            messages.success(request, f"Successfully unregistered from {event.title}!")
        else:
            messages.error(request, "You are not registered for this event!")
    
    return redirect('event_detail', event_id=event_id)


@login_required(login_url='signin')
def user_profile(request):
    """User profile page"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Get user's event registrations
    registrations = EventRegistration.objects.filter(user=request.user).order_by('-registered_at')
    
    # Get upcoming and past events
    upcoming_registrations = registrations.filter(event__date__gte=date.today())
    past_registrations = registrations.filter(event__date__lt=date.today())
    
    context = {
        'profile': profile,
        'upcoming_registrations': upcoming_registrations,
        'past_registrations': past_registrations,
    }
    return render(request, "GreenTech/user_profile.html", context)


@login_required(login_url='signin')
def edit_profile(request):
    """Edit user profile"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        profile.address = request.POST.get('address', '')
        profile.phone_number = request.POST.get('phone_number', '')
        profile.age = request.POST.get('age') or None
        profile.bio = request.POST.get('bio', '')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile')
    
    context = {'profile': profile}
    return render(request, "GreenTech/edit_profile.html", context)


# Authentication views
@unauthenticated_user
def signup(request):
    if request.method == "POST":
        Name = request.POST['Name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=Name):
            messages.error(request, "Username already exists", extra_tags="validation")
            return redirect('/signup')

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists", extra_tags="validation")
            return redirect('/signup')

        if password != confirm_password:
            messages.error(request, "Password does not match", extra_tags="validation")
            return redirect('/signup')

        if not Name.isalnum():
            messages.error(request, "Username should only contain letters and numbers", extra_tags="validation")
            return redirect('/signup')

        myuser = User.objects.create_user(Name, email, password)
        myuser.first_name = Name
        myuser.email = email
        myuser.is_active = False
        myuser.save()
        
        # Create user profile
        UserProfile.objects.create(user=myuser)

        messages.success(request, "Your account has been successfully created. Check mail to verify.",
                         extra_tags="valid")

        # welcome email
        subject = "Welcome to Green Events & Volunteering Portal"
        message = f"Hi {myuser.first_name}! Welcome to Green Events & Volunteering Portal!!!\nWe are glad to have you here!!!\nWe have sent you a confirmation email to {myuser.email}.\nPlease confirm your email to continue using our services.\n\nThank You!!!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your email"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send()

        return redirect('/')

    return render(request, "GreenTech/signup.html")


@unauthenticated_user
def signin(request):
    if (request.method == "POST"):
        Name = request.POST['Name']
        password = request.POST['Password']
        user = authenticate(username=Name, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            validate = User.objects.filter(username=Name).exists()
            if validate:
                messages.error(request, "Invalid Password", extra_tags="pass")
                return redirect('/signin')
            else:
                messages.error(request, "Invalid Username", extra_tags="user")
                return redirect('/signin')
    return render(request, "GreenTech/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out", extra_tags="logout")
    return redirect('/')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('/')
    else:
        return render(request, 'activation_failed.html')


def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Custom admin dashboard"""
    # Get statistics
    total_events = Event.objects.count()
    active_events = Event.objects.filter(is_active=True).count()
    total_registrations = EventRegistration.objects.count()
    total_users = User.objects.count()
    
    # Recent events
    recent_events = Event.objects.order_by('-created_at')[:5]
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now().date(),
        is_active=True
    ).order_by('date')[:5]
    
    # Recent registrations
    recent_registrations = EventRegistration.objects.select_related('user', 'event').order_by('-registered_at')[:10]
    
    context = {
        'total_events': total_events,
        'active_events': active_events,
        'total_registrations': total_registrations,
        'total_users': total_users,
        'recent_events': recent_events,
        'upcoming_events': upcoming_events,
        'recent_registrations': recent_registrations,
    }
    return render(request, 'GreenTech/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_events(request):
    """Manage events"""
    events = Event.objects.select_related('organizer').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(organizer__username__icontains=search_query)
        )
    
    # Filter by event type
    event_type = request.GET.get('event_type', '')
    if event_type:
        events = events.filter(event_type=event_type)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        events = events.filter(is_active=True)
    elif status == 'inactive':
        events = events.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'event_type': event_type,
        'status': status,
        'event_types': Event.EVENT_TYPES,
    }
    return render(request, 'GreenTech/admin_events.html', context)

@login_required
@user_passes_test(is_admin)
def admin_event_detail(request, event_id):
    """View and edit event details"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        # Handle event updates
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.event_type = request.POST.get('event_type')
        event.location = request.POST.get('location')
        event.date = request.POST.get('date')
        event.start_time = request.POST.get('start_time')
        event.end_time = request.POST.get('end_time')
        event.max_participants = request.POST.get('max_participants')
        event.is_active = request.POST.get('is_active') == 'on'
        
        # Handle coordinates
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude and longitude:
            event.latitude = float(latitude)
            event.longitude = float(longitude)
        
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('admin_events')
    
    # Get registrations for this event
    registrations = EventRegistration.objects.filter(event=event).select_related('user')
    
    context = {
        'event': event,
        'registrations': registrations,
        'event_types': Event.EVENT_TYPES,
    }
    return render(request, 'GreenTech/admin_event_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_create_event(request):
    """Create new event"""
    if request.method == 'POST':
        try:
            event = Event.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                event_type=request.POST.get('event_type'),
                location=request.POST.get('location'),
                date=request.POST.get('date'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
                max_participants=request.POST.get('max_participants'),
                organizer=request.user,
                is_active=request.POST.get('is_active') == 'on'
            )
            
            # Handle coordinates
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            if latitude and longitude:
                event.latitude = float(latitude)
                event.longitude = float(longitude)
                event.save()
            
            messages.success(request, 'Event created successfully!')
            return redirect('admin_events')
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    context = {
        'event_types': Event.EVENT_TYPES,
    }
    return render(request, 'GreenTech/admin_create_event.html', context)

@login_required
@user_passes_test(is_admin)
def admin_delete_event(request, event_id):
    """Delete event"""
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('admin_events')
    
    return render(request, 'GreenTech/admin_delete_event.html', {'event': event})

@login_required
@user_passes_test(is_admin)
def admin_registrations(request):
    """Manage event registrations"""
    registrations = EventRegistration.objects.select_related('user', 'event').order_by('-registered_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        registrations = registrations.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(event__title__icontains=search_query)
        )
    
    # Filter by attendance
    attended = request.GET.get('attended', '')
    if attended == 'yes':
        registrations = registrations.filter(attended=True)
    elif attended == 'no':
        registrations = registrations.filter(attended=False)
    
    # Filter by event type
    event_type = request.GET.get('event_type', '')
    if event_type:
        registrations = registrations.filter(event__event_type=event_type)
    
    # Pagination
    paginator = Paginator(registrations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'attended': attended,
        'event_type': event_type,
        'event_types': Event.EVENT_TYPES,
    }
    return render(request, 'GreenTech/admin_registrations.html', context)

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Manage users"""
    users = User.objects.select_related('userprofile').order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by staff status
    staff_status = request.GET.get('staff_status', '')
    if staff_status == 'staff':
        users = users.filter(is_staff=True)
    elif staff_status == 'regular':
        users = users.filter(is_staff=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'staff_status': staff_status,
    }
    return render(request, 'GreenTech/admin_users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """View and edit user details"""
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update user information
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        # Update profile information
        profile.phone_number = request.POST.get('phone_number')
        profile.address = request.POST.get('address')
        profile.age = request.POST.get('age') or None
        profile.bio = request.POST.get('bio')
        profile.save()
        
        messages.success(request, 'User updated successfully!')
        return redirect('admin_users')
    
    # Get user's event registrations
    registrations = EventRegistration.objects.filter(user=user).select_related('event')
    
    context = {
        'user_obj': user,
        'profile': profile,
        'registrations': registrations,
    }
    return render(request, 'GreenTech/admin_user_detail.html', context)

# AJAX endpoints for dynamic updates
@login_required
@user_passes_test(is_admin)
def toggle_event_status(request, event_id):
    """Toggle event active status"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        event.is_active = not event.is_active
        event.save()
        return JsonResponse({
            'success': True,
            'is_active': event.is_active,
            'message': 'Event activated' if event.is_active else 'Event deactivated'
        })
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_admin)
def toggle_registration_attendance(request, registration_id):
    """Toggle registration attendance"""
    if request.method == 'POST':
        registration = get_object_or_404(EventRegistration, id=registration_id)
        registration.attended = not registration.attended
        registration.save()
        return JsonResponse({
            'success': True,
            'attended': registration.attended,
            'message': 'Marked as attended' if registration.attended else 'Marked as not attended'
        })
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_admin)
def get_event_stats(request):
    """Get event statistics for dashboard"""
    if request.method == 'GET':
        total_events = Event.objects.count()
        active_events = Event.objects.filter(is_active=True).count()
        total_registrations = EventRegistration.objects.count()
        attended_registrations = EventRegistration.objects.filter(attended=True).count()
        
        # Events by type
        events_by_type = Event.objects.values('event_type').annotate(count=Count('id'))
        
        return JsonResponse({
            'total_events': total_events,
            'active_events': active_events,
            'total_registrations': total_registrations,
            'attended_registrations': attended_registrations,
            'events_by_type': list(events_by_type),
        })
    return JsonResponse({'success': False})