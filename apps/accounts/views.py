"""
Accounts Views - Authentication & User Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    CustomPasswordChangeForm
)
from .models import UserProfile, LoginHistory


User = get_user_model()


# ======================== Web Views ========================

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile is auto-created by signal, no need to create manually
            
            # Auto-login after registration
            login(request, user)
            messages.success(request, "Inscription réussie! Bienvenue sur CivicFix.")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view with security tracking"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.account_locked_until and user.account_locked_until > timezone.now():
                    messages.error(request, "Votre compte est temporairement bloqué. Réessayez plus tard.")
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                
                # Reset failed login attempts
                user.failed_login_attempts = 0
                user.last_login_ip = get_client_ip(request)
                user.save()
                
                # Log login
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    success=True,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                if remember_me:
                    request.session.set_expiry(timedelta(weeks=2))
                
                messages.success(request, f"Bienvenue {user.first_name}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                user_obj = User.objects.filter(email=email).first()
                if user_obj:
                    user_obj.failed_login_attempts += 1
                    if user_obj.failed_login_attempts >= 5:
                        user_obj.account_locked_until = timezone.now() + timedelta(hours=1)
                    user_obj.save()
                    
                    LoginHistory.objects.create(
                        user=user_obj,
                        ip_address=get_client_ip(request),
                        success=False
                    )
                
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    profile = get_object_or_404(UserProfile, user=request.user)
    context = {
        'profile': profile,
        'reports_count': request.user.get_reports_count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit user profile"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile': profile})


@login_required
def password_change_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mot de passe changé avec succès.")
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})


def password_reset_view(request):
    """Password reset view"""
    # TODO: Implement password reset with email
    messages.info(request, "Fonctionnalité en cours de développement.")
    return redirect('accounts:login')


def user_detail_view(request, user_id):
    """View user public profile"""
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'reports_count': user.get_reports_count(),
    }
    return render(request, 'accounts/user_detail.html', context)


# ======================== API Views ========================

class RegisterAPIView(generics.CreateAPIView):
    """API endpoint for user registration"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = User.objects.create_user(
                email=data.get('email'),
                username=data.get('username'),
                password=data.get('password'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            UserProfile.objects.create(user=user)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Utilisateur créé avec succès',
                'user_id': str(user.id),
                'email': user.email,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    """API endpoint for user login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Connexion réussie',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'role': user.role,
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        
        return Response({
            'status': 'error',
            'message': 'Email ou mot de passe incorrect'
        }, status=status.HTTP_401_UNAUTHORIZED)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """API endpoint for user profile"""
    serializer_class = None  # TODO: Create UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        return Response({
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'phone': user.phone,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else None,
            'profile': {
                'department': profile.department,
                'organization': profile.organization,
                'job_title': profile.job_title,
                'location': profile.location,
            }
        })


class UserListAPIView(generics.ListAPIView):
    """API endpoint for listing users (admins only)"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'error': 'Accès refusé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        users = User.objects.all().values('id', 'email', 'username', 'role', 'created_at')
        return Response({
            'status': 'success',
            'count': users.count(),
            'users': list(users)
        })


# ======================== Utility Functions ========================

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

