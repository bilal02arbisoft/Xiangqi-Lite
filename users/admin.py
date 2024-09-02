from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser, Player, Profile


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin panel configuration for the CustomUser model.
    """

    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_email_verified')
    list_filter = ('is_staff', 'is_active', 'is_email_verified')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ()}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Email Verification'), {'fields': ('is_email_verified',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)

    filter_horizontal = ('groups', 'user_permissions')

class ProfileAdmin(admin.ModelAdmin):
    """
    Custom admin panel configuration for the Profile model.
    """
    list_display = ('user', 'bio', 'country')
    search_fields = ('user__username', 'bio')
    raw_id_fields = ('user',)

class PlayerAdmin(admin.ModelAdmin):
    """
    Custom admin panel configuration for the Player model.
    """
    list_display = ('user', 'skill_level', 'rating', 'games_played')
    list_filter = ('skill_level',)
    search_fields = ('user__username',)
    raw_id_fields = ('user',)


admin.site.register(Player, PlayerAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
