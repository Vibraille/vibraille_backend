from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    """Model to create a notes object."""
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ascii_text = models.TextField(default='')
    braille_format = models.TextField(default='')

    class Meta:
        ordering = ['created']