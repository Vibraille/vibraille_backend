from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    """Model to create a notes object."""
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    img = models.ImageField(default='')
    img_name = models.CharField(max_length=100, default='')
    ascii_text = models.TextField(default='')
    braille_format = models.TextField(default='')

    class Meta:
        app_label = 'vibraille'
        ordering = ['created']

    def is_valid(self):
        pass