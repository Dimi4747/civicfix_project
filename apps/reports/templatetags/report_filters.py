"""
Custom template filters for reports app
"""
from django import template
import os

register = template.Library()


@register.filter
def file_exists(file_field):
    """Check if a file exists on disk"""
    if not file_field:
        return False
    try:
        return os.path.exists(file_field.path)
    except (ValueError, AttributeError):
        return False
