"""
Accounts URLs - Authentication & User Management
"""
from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-change/', views.password_change_view, name='password_change'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('user/<uuid:user_id>/', views.user_detail_view, name='user_detail'),
    
    # API
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/profile/', views.ProfileAPIView.as_view(), name='api_profile'),
    path('api/users/', views.UserListAPIView.as_view(), name='api_users_list'),
]
