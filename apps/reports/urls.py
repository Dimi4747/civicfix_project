"""
Reports URLs - Issue Management & Reporting
"""
from django.urls import path
from . import views


app_name = 'reports'

urlpatterns = [
    # Web Views
    path('', views.report_list_view, name='list'),
    path('create/', views.report_create_view, name='create'),
    path('<uuid:report_id>/', views.report_detail_view, name='detail'),
    path('<uuid:report_id>/edit/', views.report_edit_view, name='edit'),
    path('<uuid:report_id>/delete/', views.report_delete_view, name='delete'),
    path('<uuid:report_id>/comment/', views.report_comment_view, name='comment'),
    path('<uuid:report_id>/vote/', views.report_vote_view, name='vote'),
    path('my-reports/', views.my_reports_view, name='my_reports'),
    
    # API
    path('api/reports/', views.ReportListAPIView.as_view(), name='api_reports_list'),
    path('api/reports/create/', views.ReportCreateAPIView.as_view(), name='api_reports_create'),
    path('api/reports/<uuid:report_id>/', views.ReportDetailAPIView.as_view(), name='api_reports_detail'),
    path('api/reports/<uuid:report_id>/update/', views.ReportUpdateAPIView.as_view(), name='api_reports_update'),
    path('api/reports/<uuid:report_id>/delete/', views.ReportDeleteAPIView.as_view(), name='api_reports_delete'),
    path('api/reports/<uuid:report_id>/comments/', views.ReportCommentsAPIView.as_view(), name='api_reports_comments'),
    path('api/reports/export/pdf/<uuid:report_id>/', views.export_report_pdf, name='api_export_pdf'),
]
