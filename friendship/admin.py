from django.contrib import admin

from friendship.models import FriendRequest, Friendship


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('from_user__username', 'to_user__username')
    ordering = ('-timestamp',)

class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created')
    list_filter = ('created',)
    search_fields = ('user1__username', 'user2__username')
    ordering = ('-created',)


admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Friendship, FriendshipAdmin)
