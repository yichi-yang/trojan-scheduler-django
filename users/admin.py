from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Misc", {'fields': ('avatar', 'email_verified', 'invalidate_token_before')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Misc", {'fields': ('avatar',)}),
    )


admin.site.register(User, CustomUserAdmin)
