from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views import View
from datetime import date

from Iads import settings
from Iads.tokens import generate_token
from .decorators import *
from .models import Event, EventRegistration, UserProfile, Contact


# Mixins
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


# Home Page View
class HomeView(TemplateView):
    template_name = "GreenTech/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get upcoming events
        context['upcoming_events'] = Event.objects.filter(
            date__gte=date.today(),
            is_active=True
        ).order_by('date', 'start_time')[:6]
        
        # Get event statistics
        context['total_events'] = Event.objects.filter(is_active=True).count()
        context['total_participants'] = EventRegistration.objects.count()
        
        return context


# About Us View
class AboutView(TemplateView):
    template_name = "GreenTech/about.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get platform statistics
        context['total_events'] = Event.objects.filter(is_active=True).count()
        context['total_participants'] = EventRegistration.objects.count()
        return context


# Events List View
class EventsListView(ListView):
    model = Event
    template_name = "GreenTech/events.html"
    context_object_name = 'page_obj'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_active=True).order_by('date', 'start_time')
        
        # Filtering
        event_type = self.request.GET.get('event_type')
        location = self.request.GET.get('location')
        date_filter = self.request.GET.get('date')
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EVENT_TYPES
        context['current_filters'] = {
            'event_type': self.request.GET.get('event_type'),
            'location': self.request.GET.get('location'),
            'date': self.request.GET.get('date'),
        }
        return context


# Event Detail View
class EventDetailView(DetailView):
    model = Event
    template_name = "GreenTech/event_detail.html"
    context_object_name = 'event'
    
    def get_queryset(self):
        return Event.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_registered = False
        registration = None
        
        if self.request.user.is_authenticated:
            registration = EventRegistration.objects.filter(
                event=self.object, 
                user=self.request.user
            ).first()
            is_registered = registration is not None
        
        context['is_registered'] = is_registered
        context['registration'] = registration
        context['is_past_event'] = self.object.is_past_event
        return context


# Event Registration Views
class RegisterForEventView(LoginRequiredMixin, View):
    login_url = 'signin'
    
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id, is_active=True)
        
        # Check if event date has passed
        if event.is_past_event:
            messages.error(request, "Sorry, this event has already passed!")
            return redirect('event_detail', pk=event_id)
        
        # Check if already registered
        if EventRegistration.objects.filter(event=event, user=request.user).exists():
            messages.warning(request, "You are already registered for this event!")
            return redirect('event_detail', pk=event_id)
        
        # Check if event is full
        if event.is_full:
            messages.error(request, "Sorry, this event is full!")
            return redirect('event_detail', pk=event_id)
        
        # Create registration
        registration = EventRegistration.objects.create(
            event=event,
            user=request.user
        )
        
        # Update event participant count
        event.current_participants += 1
        event.save()
        
        messages.success(request, f"Successfully registered for {event.title}!")
        return redirect('event_detail', pk=event_id)


class UnregisterFromEventView(LoginRequiredMixin, View):
    login_url = 'signin'
    
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id, is_active=True)
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


# User Profile Views
class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "GreenTech/user_profile.html"
    login_url = 'signin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=self.request.user)
        
        # Get user's event registrations
        registrations = EventRegistration.objects.filter(user=self.request.user).order_by('-registered_at')
        
        # Get upcoming and past events
        context['profile'] = profile
        context['upcoming_registrations'] = registrations.filter(event__date__gte=date.today())
        context['past_registrations'] = registrations.filter(event__date__lt=date.today())
        
        return context


class EditProfileView(LoginRequiredMixin, View):
    login_url = 'signin'
    template_name = "GreenTech/edit_profile.html"
    
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        return render(request, self.template_name, {'profile': profile})
    
    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        profile.address = request.POST.get('address', '')
        profile.phone_number = request.POST.get('phone_number', '')
        profile.age = request.POST.get('age') or None
        profile.bio = request.POST.get('bio', '')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile')


# Authentication Views
class SignupView(View):
    template_name = "GreenTech/signup.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
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


class SigninView(View):
    template_name = "GreenTech/signin.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
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


class SignoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been successfully logged out", extra_tags="logout")
        return redirect('/')


class ActivateView(View):
    def get(self, request, uidb64, token):
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


# Admin Views
class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'GreenTech/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics
        context['total_events'] = Event.objects.count()
        context['active_events'] = Event.objects.filter(is_active=True).count()
        context['total_registrations'] = EventRegistration.objects.count()
        context['total_users'] = User.objects.count()
        context['total_contacts'] = Contact.objects.count()
        context['new_contacts'] = Contact.objects.filter(status='new').count()
        
        # Recent events
        context['recent_events'] = Event.objects.order_by('-created_at')[:5]
        
        # Upcoming events
        context['upcoming_events'] = Event.objects.filter(
            date__gte=timezone.now().date(),
            is_active=True
        ).order_by('date')[:5]
        
        # Recent registrations
        context['recent_registrations'] = EventRegistration.objects.select_related(
            'user', 'event'
        ).order_by('-registered_at')[:10]
        
        # Recent contacts
        context['recent_contacts'] = Contact.objects.order_by('-created_at')[:5]
        
        return context


class AdminEventsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Event
    template_name = 'GreenTech/admin_events.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Event.objects.select_related('organizer').order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(organizer__username__icontains=search_query)
            )
        
        # Filter by event type
        event_type = self.request.GET.get('event_type', '')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['event_type'] = self.request.GET.get('event_type', '')
        context['status'] = self.request.GET.get('status', '')
        context['event_types'] = Event.EVENT_TYPES
        return context


class AdminEventDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Event
    template_name = 'GreenTech/admin_event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registrations'] = EventRegistration.objects.filter(
            event=self.object
        ).select_related('user')
        context['event_types'] = Event.EVENT_TYPES
        return context
    
    def post(self, request, pk):
        event = self.get_object()
        
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


class AdminCreateEventView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'GreenTech/admin_create_event.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EVENT_TYPES
        return context
    
    def post(self, request):
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
        
        return self.get(request)


class AdminDeleteEventView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Event
    template_name = 'GreenTech/admin_delete_event.html'
    success_url = reverse_lazy('admin_events')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AdminRegistrationsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = EventRegistration
    template_name = 'GreenTech/admin_registrations.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EventRegistration.objects.select_related('user', 'event').order_by('-registered_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(event__title__icontains=search_query)
            )
        
        # Filter by event type
        event_type = self.request.GET.get('event_type', '')
        if event_type:
            queryset = queryset.filter(event__event_type=event_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['event_type'] = self.request.GET.get('event_type', '')
        context['event_types'] = Event.EVENT_TYPES
        return context


class AdminUsersView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'GreenTech/admin_users.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.select_related('userprofile').order_by('-date_joined')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filter by staff status
        staff_status = self.request.GET.get('staff_status', '')
        if staff_status == 'staff':
            queryset = queryset.filter(is_staff=True)
        elif staff_status == 'regular':
            queryset = queryset.filter(is_staff=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['staff_status'] = self.request.GET.get('staff_status', '')
        return context


class AdminUserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = User
    template_name = 'GreenTech/admin_user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.object)
        context['profile'] = profile
        context['registrations'] = EventRegistration.objects.filter(
            user=self.object
        ).select_related('event')
        return context
    
    def post(self, request, pk):
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(user=user)
        
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


# AJAX Views
class ToggleEventStatusView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        event.is_active = not event.is_active
        event.save()
        return JsonResponse({
            'success': True,
            'is_active': event.is_active,
            'message': 'Event activated' if event.is_active else 'Event deactivated'
        })


class GetEventStatsView(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
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


# Contact Views
class ContactView(View):
    template_name = "GreenTech/contact.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        try:
            contact = Contact.objects.create(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone_number=request.POST.get('phone_number', ''),
                contact_type=request.POST.get('contact_type', 'general_inquiry'),
                subject=request.POST.get('subject'),
                message=request.POST.get('message')
            )
            
            # Handle event creation request fields
            if request.POST.get('contact_type') == 'event_request':
                contact.event_title = request.POST.get('event_title')
                contact.event_type = request.POST.get('event_type')
                contact.event_date = request.POST.get('event_date')
                contact.event_time = request.POST.get('event_time')
                contact.event_location = request.POST.get('event_location')
                contact.max_participants = request.POST.get('max_participants') or None
                contact.event_description = request.POST.get('event_description')
                contact.organizer_name = request.POST.get('organizer_name')
                contact.organizer_phone = request.POST.get('organizer_phone')
                contact.special_requirements = request.POST.get('special_requirements')
                contact.save()
            
            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return redirect('contact')
        except Exception as e:
            messages.error(request, "There was an error submitting your message. Please try again.")
            return render(request, self.template_name)


class AdminContactsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Contact
    template_name = 'GreenTech/admin_contacts.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Contact.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(message__icontains=search_query)
            )
        
        # Filter by contact type
        contact_type = self.request.GET.get('contact_type', '')
        if contact_type:
            queryset = queryset.filter(contact_type=contact_type)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['contact_type'] = self.request.GET.get('contact_type', '')
        context['status'] = self.request.GET.get('status', '')
        context['contact_types'] = Contact.CONTACT_TYPES
        context['status_choices'] = Contact.STATUS_CHOICES
        return context


class AdminContactDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Contact
    template_name = 'GreenTech/admin_contact_detail.html'
    context_object_name = 'contact'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_types'] = Contact.CONTACT_TYPES
        context['status_choices'] = Contact.STATUS_CHOICES
        return context
    
    def post(self, request, pk):
        contact = self.get_object()
        
        # Update contact status and admin notes
        contact.status = request.POST.get('status')
        contact.admin_notes = request.POST.get('admin_notes', '')
        contact.save()
        
        messages.success(request, 'Contact query updated successfully!')
        return redirect('admin_contacts')


class UpdateContactStatusView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Contact.STATUS_CHOICES):
            contact.status = new_status
            contact.save()
            return JsonResponse({
                'success': True,
                'status': contact.get_status_display(),
                'message': f'Status updated to {contact.get_status_display()}'
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Invalid status'
        })