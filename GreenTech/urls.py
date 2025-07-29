from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('events/', views.EventsListView.as_view(), name='events'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event/<int:event_id>/register/', views.RegisterForEventView.as_view(), name='register_for_event'),
    path('event/<int:event_id>/unregister/', views.UnregisterFromEventView.as_view(), name='unregister_from_event'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('signin/', views.SigninView.as_view(), name='signin'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signout/', views.SignoutView.as_view(), name='signout'),
    path('activate/<uidb64>/<token>', views.ActivateView.as_view(), name='activate'),
    
    # Custom Admin URLs
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/events/', views.AdminEventsView.as_view(), name='admin_events'),
    path('admin/events/create/', views.AdminCreateEventView.as_view(), name='admin_create_event'),
    path('admin/events/<int:pk>/', views.AdminEventDetailView.as_view(), name='admin_event_detail'),
    path('admin/events/<int:pk>/delete/', views.AdminDeleteEventView.as_view(), name='admin_delete_event'),
    path('admin/registrations/', views.AdminRegistrationsView.as_view(), name='admin_registrations'),
    path('admin/users/', views.AdminUsersView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/contacts/', views.AdminContactsView.as_view(), name='admin_contacts'),
    path('admin/contacts/<int:pk>/', views.AdminContactDetailView.as_view(), name='admin_contact_detail'),
    
    # AJAX endpoints
    path('admin/events/<int:event_id>/toggle-status/', views.ToggleEventStatusView.as_view(), name='toggle_event_status'),
    path('admin/stats/', views.GetEventStatsView.as_view(), name='get_event_stats'),
    path('admin/contacts/<int:contact_id>/update-status/', views.UpdateContactStatusView.as_view(), name='update_contact_status'),
]