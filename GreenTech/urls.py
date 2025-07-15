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
]