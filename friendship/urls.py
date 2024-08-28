from django.urls import path
from .views import (
    SendFriendRequestView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    ListSentFriendRequestsView,
    ListFriendsView, FriendRequestsView,SearchUsersView
)

urlpatterns = [
    path('send-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('accept-request/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('reject-request/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('sent-requests/', ListSentFriendRequestsView.as_view(), name='list-sent-friend-requests'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
    path('requests/', FriendRequestsView.as_view(), name='friend-requests'),
    path('users/search/', SearchUsersView.as_view(), name='search_users'),
]

