"""
Reports Views - Issue/Report Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.core.paginator import Paginator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
# from reportlab.lib.pagesizes import letter  # Temporarily disabled
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
from django.contrib.auth import get_user_model
from datetime import datetime
import io

from .models import Report, ReportComment, ReportAttachment, ReportHistory, ReportVote
from .forms import ReportForm, ReportCommentForm, ReportFilterForm, ReportStatusUpdateForm

User = get_user_model()


# ======================== Web Views ========================

def report_list_view(request):
    """List all reports with filtering, search and pagination"""
    reports = Report.objects.select_related('author', 'assigned_to').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        reports = reports.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        reports = reports.filter(category=category_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        reports = reports.filter(priority=priority_filter)
    
    # Sort
    sort_by = request.GET.get('sort_by', '-created_at')
    reports = reports.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'reports/list.html', context)


def report_detail_view(request, report_id):
    """View a single report with comments"""
    report = get_object_or_404(Report, id=report_id)
    
    # Increment views count
    report.views_count += 1
    report.save(update_fields=['views_count'])
    
    comments = report.comments.all()
    form = ReportCommentForm()
    
    # Check if current user can edit
    can_edit = request.user == report.author or (request.user.is_staff and request.user.is_moderator())
    
    context = {
        'report': report,
        'comments': comments,
        'form': form,
        'can_edit': can_edit,
        'status_badge': report.get_status_badge(),
    }
    
    return render(request, 'reports/detail.html', context)


@login_required
def report_create_view(request):
    """Create a new report"""
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.author = request.user
            report.save()
            
            # Handle attachments
            attachments = request.FILES.getlist('attachments')
            for attachment in attachments:
                ReportAttachment.objects.create(
                    report=report,
                    file=attachment,
                    filename=attachment.name,
                    file_size=attachment.size,
                    uploaded_by=request.user
                )
            
            # Log creation
            ReportHistory.objects.create(
                report=report,
                user=request.user,
                action='created',
                description=f"Rapport créé par {request.user.email}"
            )
            
            messages.success(request, "Rapport créé avec succès!")
            return redirect('reports:detail', report_id=report.id)
    else:
        form = ReportForm()
    
    return render(request, 'reports/create.html', {'form': form})


@login_required
def report_edit_view(request, report_id):
    """Edit an existing report"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.user != report.author and not request.user.is_moderator():
        messages.error(request, "Vous n'avez pas la permission de modifier ce rapport.")
        return redirect('reports:detail', report_id=report_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            
            # Log update
            ReportHistory.objects.create(
                report=report,
                user=request.user,
                action='updated',
                description=f"Rapport mis à jour par {request.user.email}"
            )
            
            messages.success(request, "Rapport mis à jour avec succès!")
            return redirect('reports:detail', report_id=report.id)
    else:
        form = ReportForm(instance=report)
    
    return render(request, 'reports/edit.html', {'form': form, 'report': report})


@login_required
def report_delete_view(request, report_id):
    """Delete a report"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.user != report.author and not request.user.is_admin():
        messages.error(request, "Vous n'avez pas la permission de supprimer ce rapport.")
        return redirect('reports:detail', report_id=report_id)
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, "Rapport supprimé avec succès!")
        return redirect('reports:list')
    
    return render(request, 'reports/delete_confirm.html', {'report': report})


@login_required
def report_comment_view(request, report_id):
    """Add a comment to a report"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        form = ReportCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.report = report
            comment.author = request.user
            comment.save()
            
            report.comments_count = report.comments.count()
            report.save(update_fields=['comments_count'])
            
            # Log comment
            ReportHistory.objects.create(
                report=report,
                user=request.user,
                action='commented',
                description=f"Commentaire ajouté par {request.user.email}"
            )
            
            messages.success(request, "Commentaire ajouté!")
    
    return redirect('reports:detail', report_id=report_id)


@login_required
def report_vote_view(request, report_id):
    """Vote on a report (upvote/downvote)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    report = get_object_or_404(Report, id=report_id)
    vote_value = request.POST.get('vote', 1)
    
    try:
        vote_value = int(vote_value)
        if vote_value not in [-1, 1]:
            return JsonResponse({'error': 'Invalid vote value'}, status=400)
        
        # Check if user already voted
        existing_vote = ReportVote.objects.filter(report=report, user=request.user).first()
        
        if existing_vote:
            if existing_vote.vote == vote_value:
                existing_vote.delete()
            else:
                existing_vote.vote = vote_value
                existing_vote.save()
        else:
            ReportVote.objects.create(report=report, user=request.user, vote=vote_value)
        
        # Update votes count
        report.votes_count = report.votes.count()
        report.save(update_fields=['votes_count'])
        
        return JsonResponse({
            'status': 'success',
            'votes_count': report.votes_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def my_reports_view(request):
    """View user's own reports"""
    reports = Report.objects.filter(author=request.user).order_by('-created_at')
    
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Mes Rapports'
    }
    
    return render(request, 'reports/my_reports.html', context)


def export_report_pdf(request, report_id):
    """Export a report as PDF"""
    report = get_object_or_404(Report, id=report_id)
    
    # Check if reportlab is available
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
        )
        elements.append(Paragraph(f"Rapport: {report.title}", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Report details
        details = f"""
        <b>Statut:</b> {report.get_status_display()}<br/>
        <b>Catégorie:</b> {report.get_category_display()}<br/>
        <b>Priorité:</b> {report.get_priority_display()}<br/>
        <b>Auteur:</b> {report.author.get_full_name()}<br/>
        <b>Date de création:</b> {report.created_at.strftime('%d/%m/%Y %H:%M')}<br/>
        """
        elements.append(Paragraph(details, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Description
        elements.append(Paragraph("<b>Description:</b>", styles['Heading2']))
        elements.append(Paragraph(report.description, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Resolution notes if exists
        if report.resolution_notes:
            elements.append(Paragraph("<b>Notes de résolution:</b>", styles['Heading2']))
            elements.append(Paragraph(report.resolution_notes, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_{report.id}.pdf"'
        return response
        
    except ImportError:
        return HttpResponse(
            "L'export PDF n'est pas disponible. Installez reportlab: pip install reportlab",
            status=503
        )





# ======================== API Views ========================

class ReportListAPIView(generics.ListAPIView):
    """API endpoint to list all reports"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        reports = Report.objects.select_related('author').all()
        
        # Filtering
        status_filter = request.query_params.get('status')
        category_filter = request.query_params.get('category')
        search_query = request.query_params.get('search')
        
        if status_filter:
            reports = reports.filter(status=status_filter)
        if category_filter:
            reports = reports.filter(category=category_filter)
        if search_query:
            reports = reports.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Pagination
        page = request.query_params.get('page', 1)
        paginator = Paginator(reports, 20)
        page_obj = paginator.get_page(page)
        
        data = [{
            'id': str(r.id),
            'title': r.title,
            'description': r.description[:100],
            'status': r.status,
            'category': r.category,
            'priority': r.priority,
            'author': r.author.email,
            'created_at': r.created_at.isoformat(),
            'views_count': r.views_count,
        } for r in page_obj]
        
        return Response({
            'status': 'success',
            'count': reports.count(),
            'current_page': page,
            'total_pages': paginator.num_pages,
            'results': data
        })


class ReportCreateAPIView(generics.CreateAPIView):
    """API endpoint to create a report"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        try:
            report = Report.objects.create(
                title=request.data.get('title'),
                description=request.data.get('description'),
                category=request.data.get('category'),
                priority=request.data.get('priority'),
                location=request.data.get('location'),
                latitude=request.data.get('latitude'),
                longitude=request.data.get('longitude'),
                author=request.user
            )
            
            return Response({
                'status': 'success',
                'report_id': str(report.id),
                'message': 'Rapport créé avec succès'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ReportDetailAPIView(generics.RetrieveAPIView):
    """API endpoint to get report details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        
        return Response({
            'id': str(report.id),
            'title': report.title,
            'description': report.description,
            'status': report.status,
            'category': report.category,
            'priority': report.priority,
            'location': report.location,
            'author': {
                'id': str(report.author.id),
                'email': report.author.email,
                'name': report.author.get_full_name()
            },
            'created_at': report.created_at.isoformat(),
            'updated_at': report.updated_at.isoformat(),
            'views_count': report.views_count,
            'comments_count': report.comments_count,
            'votes_count': report.votes_count,
        })


class ReportUpdateAPIView(generics.UpdateAPIView):
    """API endpoint to update a report"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        
        if request.user != report.author and not request.user.is_moderator():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report.title = request.data.get('title', report.title)
        report.description = request.data.get('description', report.description)
        report.category = request.data.get('category', report.category)
        report.priority = request.data.get('priority', report.priority)
        report.save()
        
        return Response({'status': 'success', 'message': 'Rapport mis à jour'})


class ReportDeleteAPIView(generics.DestroyAPIView):
    """API endpoint to delete a report"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        
        if request.user != report.author and not request.user.is_admin():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report.delete()
        return Response({'status': 'success', 'message': 'Rapport supprimé'})


class ReportCommentsAPIView(generics.ListCreateAPIView):
    """API endpoint for report comments"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        comments = report.comments.all()
        
        data = [{
            'id': str(c.id),
            'author': c.author.email,
            'content': c.content,
            'is_internal': c.is_internal,
            'created_at': c.created_at.isoformat(),
        } for c in comments]
        
        return Response({
            'status': 'success',
            'count': len(data),
            'comments': data
        })
    
    def post(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        
        comment = ReportComment.objects.create(
            report=report,
            author=request.user,
            content=request.data.get('content'),
            is_internal=request.data.get('is_internal', False)
        )
        
        return Response({
            'status': 'success',
            'comment_id': str(comment.id),
            'message': 'Commentaire ajouté'
        }, status=status.HTTP_201_CREATED)

