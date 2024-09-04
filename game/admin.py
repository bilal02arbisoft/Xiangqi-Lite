from django.contrib import admin

from game.models import Game


class GameAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Game model.
    """

    list_display = ('id', 'red_player', 'black_player', 'status', 'turn', 'started_at', 'last_updated')
    list_filter = ('status', 'turn', 'started_at', 'last_updated')
    search_fields = ('red_player__user__username', 'black_player__user__username', 'status')
    fieldsets = (
        (None, {
            'fields': ('red_player', 'black_player', 'fen', 'initial_fen', 'moves')
        }),
        ('Game State', {
            'fields': ('status', 'turn', 'red_time_remaining', 'black_time_remaining')
        }),
        ('Timing', {
            'fields': ('started_at', 'last_updated')
        }),
    )

    ordering = ('-started_at',)
    filter_horizontal = ('viewers',)

    def get_readonly_fields(self, request, obj=None):
        """
        Make certain fields read-only in the admin interface based on the object's state.
        """
        if obj:
            return ['started_at', 'last_updated']
        return []


admin.site.register(Game, GameAdmin)
