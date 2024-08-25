from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_email_verified')
    list_filter = ('is_staff', 'is_active', 'is_email_verified')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ()}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Email Verification'), {'fields': ('is_email_verified',)}),
    )

    # Fields for the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


# Register the CustomUserAdmin with the CustomUser model
admin.site.register(CustomUser, CustomUserAdmin)
