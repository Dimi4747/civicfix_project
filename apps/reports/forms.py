"""
Reports Forms - Report Creation & Management
"""
from django import forms
from django.contrib.auth import get_user_model
from apps.reports.models import Report, ReportComment, ReportAttachment


User = get_user_model()


class ReportForm(forms.ModelForm):
    """Form for creating and updating reports"""
    
    attachments = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif'
        })
    )
    
    class Meta:
        model = Report
        fields = ['title', 'description', 'category', 'priority', 'location', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Titre du rapport',
                'maxlength': 255
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 6,
                'placeholder': 'Description détaillée du problème'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Lieu du problème'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Latitude (optionnel)',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'placeholder': 'Longitude (optionnel)',
                'step': '0.000001'
            }),
        }


class ReportCommentForm(forms.ModelForm):
    """Form for adding comments to reports"""
    
    class Meta:
        model = ReportComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Ajouter un commentaire...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600'
            })
        }


class ReportFilterForm(forms.Form):
    """Form for filtering reports"""
    
    STATUS_FILTER = (
        ('', 'Tous les statuts'),
    ) + Report.STATUS_CHOICES
    
    PRIORITY_FILTER = (
        ('', 'Toutes les priorités'),
    ) + Report.PRIORITY_CHOICES
    
    CATEGORY_FILTER = (
        ('', 'Toutes les catégories'),
    ) + Report.CATEGORY_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
            'placeholder': 'Rechercher par titre ou description...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_FILTER,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
        })
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=CATEGORY_FILTER,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
        })
    )
    
    priority = forms.ChoiceField(
        required=False,
        choices=PRIORITY_FILTER,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
        })
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Plus récents'),
            ('created_at', 'Plus anciens'),
            ('-priority', 'Priorité élevée'),
            ('views_count', 'Moins vues'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
        })
    )


class ReportStatusUpdateForm(forms.ModelForm):
    """Form for updating report status (admin/moderator only)"""
    
    class Meta:
        model = Report
        fields = ['status', 'assigned_to', 'resolution_notes', 'internal_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
            }),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Notes de résolution...'
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Notes internes (non visibles aux utilisateurs)...'
            }),
        }
