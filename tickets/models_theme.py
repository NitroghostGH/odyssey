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