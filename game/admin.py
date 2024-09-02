from django.contrib import admin

from game.models import Game


class GameAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Game model.
    """

    # List of fields to display in the admin list view
    list_display = ('id', 'red_player', 'black_player', 'status', 'turn', 'started_at', 'last_updated')

    # List of fields to filter by in the admin interface
    list_filter = ('status', 'turn', 'started_at', 'last_updated')

    # Fields that are searchable in the admin list view
    search_fields = ('red_player__user__username', 'black_player__user__username', 'status')

    # Configuring which fields to display and how to organize them in the admin form
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

    # Fields to use for the ordering of records in the admin list view
    ordering = ('-started_at',)

    # Making the ManyToManyField (viewers) easier to manage
    filter_horizontal = ('viewers',)

    def get_readonly_fields(self, request, obj=None):
        """
        Make certain fields read-only in the admin interface based on the object's state.
        """
        if obj:  # Editing an existing object
            return ['started_at', 'last_updated']
        return []


# Register the Game model with the custom admin configuration
admin.site.register(Game, GameAdmin)
