# app_name/urls.py

from django.urls import path
from .views import RegistrationView, LoginView, ProfileView, ProfileEditView ,home

urlpatterns = [
    path('accounts/register/', RegistrationView.as_view(), name='register'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/profile/view/', ProfileView.as_view(), name='profile_view'),
    path('accounts/profile/edit/', ProfileEditView.as_view() ,  name='profile_edit'),
    path('/', home, name='home')
]
