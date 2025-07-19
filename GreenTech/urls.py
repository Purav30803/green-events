from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events, name='events'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('event/<int:event_id>/unregister/', views.unregister_from_event, name='unregister_from_event'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    
    # Custom Admin URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/events/', views.admin_events, name='admin_events'),
    path('admin/events/create/', views.admin_create_event, name='admin_create_event'),
    path('admin/events/<int:event_id>/', views.admin_event_detail, name='admin_event_detail'),
    path('admin/events/<int:event_id>/delete/', views.admin_delete_event, name='admin_delete_event'),
    path('admin/registrations/', views.admin_registrations, name='admin_registrations'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    
    # AJAX endpoints
    path('admin/events/<int:event_id>/toggle-status/', views.toggle_event_status, name='toggle_event_status'),
    path('admin/stats/', views.get_event_stats, name='get_event_stats'),
]