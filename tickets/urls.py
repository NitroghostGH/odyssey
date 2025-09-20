from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views, views_theme, views_position

urlpatterns = [
    path('', views.home, name='home'),
    path('board/<int:board_id>/', views.board_view, name='board-view'),
    path('board/<int:board_id>/ticket/new/', views.ticket_new, name='ticket_new'),
    path('ticket/<int:ticket_id>/edit/', views.ticket_edit, name='ticket-edit'),
    path('update-ticket-status/', views.update_ticket_status, name='update-ticket-status'),
    
    # Theme management endpoints
    path('themes/create/', views_theme.theme_creator, name='theme-creator'),
    path('api/themes/', views_theme.get_themes, name='get_themes'),
    path('api/themes/save/', views_theme.save_theme, name='save_theme'),
    path('api/themes/<int:theme_id>/delete/', views_theme.delete_theme, name='delete_theme'),
    
    # Ticket position management
    path('api/tickets/update-position/', views_position.update_ticket_position, name='update-ticket-position'),
    
    # Authentication
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]