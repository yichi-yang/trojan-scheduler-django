from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {'fields': ('avatar', 'email_verified', 'invalidate_token_before',
                                        'nickname', 'display_name_choice', 'show_name', 'show_email', 'show_date_joined')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {'fields': ('avatar', 'nickname', 'display_name_choice',
                                        'show_name', 'show_email', 'show_date_joined')}),
    )


admin.site.register(User, CustomUserAdmin)
