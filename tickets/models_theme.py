from django.db import models
from django.contrib.auth.models import User

class UserTheme(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='themes')
    colors = models.JSONField()  # Stores the theme color values
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.username}'s theme: {self.name}"


class ThemePreference(models.Model):
    """Stores a user's selected preferred theme (can be their own or a public one)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='theme_preference')
    theme = models.ForeignKey(UserTheme, null=True, blank=True, on_delete=models.SET_NULL, related_name='preferred_by')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} preference -> {self.theme_id}" 