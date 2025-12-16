"""
Accounts Decorators - Role-based Access Control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def admin_required(view_func):
    """Decorator to check if user is admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Veuillez vous connecter.")
            return redirect('accounts:login')
        
        if request.user.role != 'admin':
            messages.error(request, "Accès refusé. Vous n'avez pas les permissions d'administrateur.")
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def moderator_required(view_func):
    """Decorator to check if user is moderator or admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Veuillez vous connecter.")
            return redirect('accounts:login')
        
        if request.user.role not in ['admin', 'moderator']:
            messages.error(request, "Accès refusé. Vous n'avez pas les permissions de modérateur.")
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_moderator_required(view_func):
    """Alias for moderator_required"""
    return moderator_required(view_func)
