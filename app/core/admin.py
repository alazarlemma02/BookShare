"""
Django Admin Customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.models import User, Book
from app import settings


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name', 'profile_picture_tag']

    fieldsets = [
        (None, {'fields': ('email', 'password', 'profile_picture')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    ]
    readonly_fields = ['last_login']

    add_fieldsets = [
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'profile_picture',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    ]

    def profile_picture_tag(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 50px; height:50px;" />'.format(
                    settings.MEDIA_URL + str(obj.profile_picture)
                )
            )
        return '-'

    profile_picture_tag.short_description = 'Profile Picture'


admin.site.register(User, UserAdmin)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin settings for Book."""
    list_display = ['title', 'author', 'owner', 'is_available']
    list_filter = ['is_available', 'condition']
    search_fields = ['title', 'author']
