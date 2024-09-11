from django.urls import path

from friendship.views import (
    AcceptRejectFriendRequestView,
    FriendRequestsView,
    ListFriendsView,
    ListSentFriendRequestsView,
    SearchUsersView,
    SendFriendRequestView,
)

urlpatterns = [
    path('send-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('repond-request/', AcceptRejectFriendRequestView.as_view(), name='accept-friend-request'),
    path('sent-requests/', ListSentFriendRequestsView.as_view(), name='list-sent-friend-requests'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
    path('requests/', FriendRequestsView.as_view(), name='friend-requests'),
    path('users/search/', SearchUsersView.as_view(), name='search_users'),
]
