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