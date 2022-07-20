from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Note(models.Model):
    """Model to create a notes object."""
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    img = models.ImageField(default='')
    img_name = models.CharField(max_length=100, default='')
    ascii_text = models.TextField(default='')
    braille_format = models.TextField(default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        app_label = 'vibraille'
        ordering = ['created']


class VibrailleUser(models.Model):
    """Override model to include phone field."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(null=True, unique=True)


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = VibrailleUser(user=user)
        user_profile.save()


post_save.connect(create_profile, sender=User)
