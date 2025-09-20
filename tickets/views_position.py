from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Ticket
import json

@login_required
@require_http_methods(["POST"])
def update_ticket_position(request):
    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        importance = data.get('importance')
        urgency = data.get('urgency')
        
        if not all([ticket_id, importance, urgency]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            })
        
        # Get the ticket and update its position
        ticket = Ticket.objects.get(id=ticket_id)
        
        # Check if user has permission to update this ticket
        if request.user.is_staff or ticket.board.created_by == request.user:
            ticket.importance = int(importance)
            ticket.urgency = int(urgency)
            ticket.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Ticket position updated successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            })
            
    except Ticket.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Ticket not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })