from django.contrib import admin
from .models_theme import UserTheme

@admin.register(UserTheme)
class UserThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_public', 'user')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')