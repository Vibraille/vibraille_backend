from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import VibrailleUser


class VibrailleUserInline(admin.StackedInline):
    model = VibrailleUser
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (VibrailleUserInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
