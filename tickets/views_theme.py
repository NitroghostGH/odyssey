from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models_theme import UserTheme, ThemePreference
from .models import Ticket
import json

@login_required
def theme_creator(request):
    """View for the theme creation page"""
    if request.method == 'POST':
        theme_name = request.POST.get('name')
        is_public = request.POST.get('is_public') == 'on'
        colors = {
            'primary': request.POST.get('primary-color'),
            'secondary': request.POST.get('secondary-color'),
            'background': request.POST.get('background-color'),
            'surface': request.POST.get('surface-color'),
            'text': request.POST.get('text-color'),
            'accent': request.POST.get('accent-color')
        }
        
        if not theme_name:
            messages.error(request, 'Theme name is required')
            return redirect('theme-creator')
        
        theme = UserTheme.objects.create(
            user=request.user,
            name=theme_name,
            colors=colors,
            is_public=is_public
        )
        
        messages.success(request, f'Theme "{theme_name}" created successfully!')
        return redirect('board-view', board_id=request.GET.get('next', 1))
        
    return render(request, 'tickets/theme_creator.html', {
        'default_colors': {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'text': '#212529',
            'accent': '#28a745'
        }
    })

@login_required
def save_theme(request):
    """API endpoint for updating existing themes"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    try:
        data = json.loads(request.body)
        theme_id = data.get('theme_id')
        colors = data.get('colors')
        
        if not theme_id or not colors:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        theme = UserTheme.objects.get(id=theme_id, user=request.user)
        theme.colors = colors
        theme.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Theme updated successfully'
        })
        
    except UserTheme.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Theme not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_themes(request):
    # Get user's themes
    user_themes = UserTheme.objects.filter(user=request.user)
    
    # Get public themes from other users
    public_themes = UserTheme.objects.filter(
        is_public=True
    ).exclude(user=request.user)
    
    themes = {
        'user_themes': list(user_themes.values('id', 'name', 'colors', 'is_public')),
        'public_themes': list(public_themes.values('id', 'name', 'colors', 'user__username'))
    }
    
    return JsonResponse(themes)

@login_required
def get_single_theme(request, theme_id):
    theme = get_object_or_404(UserTheme, id=theme_id)
    return JsonResponse({'id': theme.id, 'name': theme.name, 'colors': theme.colors, 'is_public': theme.is_public, 'owner': theme.user.username})

@login_required
def set_theme_preference(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    try:
        data = json.loads(request.body)
        theme_id = data.get('theme_id')
        theme = None
        if theme_id == '':
            theme = None
        elif theme_id is not None:
            theme = UserTheme.objects.get(id=theme_id)
        pref, _ = ThemePreference.objects.get_or_create(user=request.user)
        pref.theme = theme
        pref.save()
        return JsonResponse({'success': True})
    except UserTheme.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Theme not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def delete_theme(request, theme_id):
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    try:
        theme = UserTheme.objects.get(id=theme_id, user=request.user)
        theme.delete()
        return JsonResponse({'success': True})
    except UserTheme.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Theme not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})