from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.signin,name='signin'),
    path('home',views.home,name='home'),
    path('signup',views.signup,name='signup'),
    path('signout',views.signout,name='signout'),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    path('home', views.home, name='home'),
    path('account/<str:pk>', views.account, name='account'),

    # path('dashboard',views.dashboard,name='dashboard')
]