from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import TicketForm
from .models import Board, Ticket, TicketActivity, TicketComment
from .models_theme import ThemePreference, UserTheme
from django.utils.timezone import now
from django import template

register = template.Library()

@login_required
def ticket_new(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.board = board
            ticket.created_by = request.user
            ticket.save()
            TicketActivity.objects.create(
                ticket=ticket,
                user=request.user,
                activity_type='created',
                description=f'Created {ticket.ticket_type} {ticket.title}'
            )
            return redirect('tickets:board-view', board_id=board.id)
    else:
        form = TicketForm(initial={'board': board, 'ticket_type': 'ticket'})
    return render(request, 'tickets/ticket_form.html', {
        'form': form,
        'board': board,
        'action': 'Create',
        'title': 'Create New Ticket'
    })

@register.filter
def get_urgency_label(ticket):
    labels = {
        5: 'Immediate – Production outage, data loss, or business actively losing money/customers',
        4: 'High – Imminent deadline, blocking team, or critical client commitment',
        3: 'Medium – Needed for current sprint/near-term release, or looming event',
        2: 'Low – Can be scheduled for a future sprint/cycle, no negative impact',
        1: 'None – No deadline, can be backlogged indefinitely',
    }
    return labels.get(ticket.urgency, '')

@register.filter
def get_importance_label(ticket):
    labels = {
        5: 'Critical – Essential for core strategy, major security/legal risk, or unblocks company/flagship launch',
        4: 'High – Significant value to many users, major pain point, or key roadmap item',
        3: 'Medium – Meaningful improvement, highly requested, or moderate technical debt',
        2: 'Low – Minor enhancement, edge-case bug, or small process improvement',
        1: 'Trivial – Cosmetic, no data, or easy workaround exists',
    }
    return labels.get(ticket.importance, '')

@login_required
def board_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    tickets = Ticket.objects.filter(board=board).order_by('sort_order')
    user_theme = None
    pref = getattr(request.user, 'theme_preference', None)
    if pref and pref.theme:
        user_theme = pref.theme
    else:
        # fallback: latest user-owned theme
        user_theme = UserTheme.objects.filter(user=request.user).order_by('-updated_at').first()
    all_user_themes = list(UserTheme.objects.filter(user=request.user).values('id','name'))
    public_themes = list(UserTheme.objects.filter(is_public=True).exclude(user=request.user).values('id','name'))
    grouped = {
        'tickets': tickets,
        'by_status': {
            'todo': tickets.filter(status='todo'),
            'in_progress': tickets.filter(status='in_progress'),
            'done': tickets.filter(status='done'),
        },
        'by_type': {
            'epic': tickets.filter(ticket_type='epic'),
            'ticket': tickets.filter(ticket_type='ticket'),
            'bug': tickets.filter(ticket_type='bug'),
        }
    }
    recent_activity = TicketActivity.objects.filter(ticket__board=board).select_related('ticket', 'user').order_by('-timestamp')[:10]
    return render(request, 'tickets/board.html', {
        'board': board,
        'grouped': grouped,
        'recent_activity': recent_activity,
        'user_theme': user_theme,
        'available_user_themes': all_user_themes,
        'available_public_themes': public_themes
    })

@login_required
def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comment_mode = request.POST.get('comment_mode') == '1'
    if request.method == "POST" and comment_mode:
        body = request.POST.get('comment_body', '').strip()
        if body:
            TicketComment.objects.create(ticket=ticket, user=request.user, body=body)
            TicketActivity.objects.create(
                ticket=ticket,
                user=request.user,
                activity_type='commented',
                description=f'Comment added ({len(body)} chars)'
            )
        return redirect('tickets:ticket-edit', ticket_id=ticket.id)
    if request.method == "POST" and not comment_mode:
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            before = {f: getattr(ticket, f) for f in ['title','description','status','priority','importance','urgency','ticket_type','assignee_id','parent_id']}
            updated = form.save()
            after = {f: getattr(updated, f) for f in before}
            changed_parts = []
            for k in before:
                if before[k] != after[k]:
                    changed_parts.append(f"{k}={before[k]}→{after[k]}")
            TicketActivity.objects.create(
                ticket=updated,
                user=request.user,
                activity_type='updated',
                description=('; '.join(changed_parts) if changed_parts else 'No material field changes')
            )
            return redirect('tickets:board-view', board_id=updated.board.id)
    else:
        form = TicketForm(instance=ticket)
    comments = ticket.comments.select_related('user').all()
    return render(request, 'tickets/ticket_form.html', {
        'form': form,
        'ticket': ticket,
        'comments': comments,
        'action': 'Edit',
        'title': 'Edit Ticket'
    })

@login_required
@login_required
def update_ticket_status(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        new_status = data.get('new_status')
        new_sort_order = data.get('sort_order')
        if not ticket_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Missing ticket_id or new_status'})
        valid_statuses = dict(Ticket.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'})
        ticket = get_object_or_404(Ticket, id=ticket_id)
        changes = []
        if ticket.status != new_status:
            old_status = ticket.status
            ticket.status = new_status
            changes.append(f'Status changed from {old_status} to {new_status}')
        if new_sort_order is not None:
            old_order = ticket.sort_order
            ticket.sort_order = new_sort_order
            changes.append('Priority reordered')
        ticket.updated_by = request.user
        ticket.save()
        if changes:
            TicketActivity.objects.create(
                ticket=ticket,
                user=request.user,
                activity_type='updated',
                description=', '.join(changes)
            )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def home(request):
    boards = Board.objects.all()
    return render(request, 'tickets/home.html', {'boards': boards})
