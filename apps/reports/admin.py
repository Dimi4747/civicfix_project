from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Report, ReportAttachment, ReportComment, ReportHistory, ReportVote


class ReportAttachmentInline(admin.TabularInline):
    """Inline admin for report attachments"""
    model = ReportAttachment
    readonly_fields = ('uploaded_at', 'file_size')
    extra = 0


class ReportCommentInline(admin.TabularInline):
    """Inline admin for report comments"""
    model = ReportComment
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Custom admin for Report model"""
    list_display = ('title', 'status', 'priority', 'category', 'author', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'author__email', 'location')
    readonly_fields = ('id', 'views_count', 'comments_count', 'votes_count', 'created_at', 'updated_at')
    inlines = [ReportAttachmentInline, ReportCommentInline]
    
    fieldsets = (
        (_('Information général'), {
            'fields': ('id', 'title', 'description', 'category', 'location')
        }),
        (_('Statut & Priorité'), {
            'fields': ('status', 'priority', 'author', 'assigned_to')
        }),
        (_('Localisation'), {
            'fields': ('latitude', 'longitude')
        }),
        (_('Résolution'), {
            'fields': ('resolution_notes', 'internal_notes', 'resolved_at')
        }),
        (_('Statistiques'), {
            'fields': ('views_count', 'comments_count', 'votes_count')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(ReportAttachment)
class ReportAttachmentAdmin(admin.ModelAdmin):
    """Admin for ReportAttachment model"""
    list_display = ('filename', 'report', 'uploaded_by', 'file_size', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'report__title')
    readonly_fields = ('uploaded_at', 'file_size')


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    """Admin for ReportComment model"""
    list_display = ('author', 'report', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('content', 'author__email', 'report__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    """Admin for ReportHistory model"""
    list_display = ('report', 'action', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('report__title', 'description')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(ReportVote)
class ReportVoteAdmin(admin.ModelAdmin):
    """Admin for ReportVote model"""
    list_display = ('report', 'user', 'vote', 'created_at')
    list_filter = ('vote', 'created_at')
    search_fields = ('report__title', 'user__email')
    readonly_fields = ('created_at',)
