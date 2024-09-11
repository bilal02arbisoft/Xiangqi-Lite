from error_handling import handle_exceptions
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from friendship.models import FriendRequest, Friendship
from friendship.serializers import (
    FriendRequestActionSerializer,
    FriendRequestCreateSerializer,
    FriendRequestSerializer,
    FriendshipSerializer,
)
from users.models import CustomUser as User
from users.serializers import CustomUserSerializer


class BaseAPIView(APIView):
    """
    Base API view that requires authentication.
    """
    permission_classes = [IsAuthenticated]


class BaseFriendRequestView(BaseAPIView):
    """
    Base class for handling friend request-specific logic.
    """
    def get_user(self, username):
        """
        Helper method to fetch a user by username.
        """
        return User.objects.get(username=username)

    def get_friend_request(self, from_user, to_user):
        """
        Helper method to fetch a friend request.
        """
        return FriendRequest.objects.get(from_user=from_user, to_user=to_user)


class SendFriendRequestView(BaseFriendRequestView):

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        serializer = FriendRequestCreateSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        to_user = User.objects.get(username=username)
        friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)

        return Response(
            {'message': 'Friend request sent!' if created else 'Friend request already sent.'},
            status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
        )



class AcceptRejectFriendRequestView(BaseFriendRequestView):

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        serializer = FriendRequestActionSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        friend_request = serializer.context['friend_request']
        action = serializer.validated_data['action']

        if action == 'accepted':
            friend_request.accept()

            return Response({'message': 'Friend request accepted!'}, status=status.HTTP_200_OK)
        elif action == 'rejected':

            friend_request.reject()

            return Response({'message': 'Friend request rejected!'}, status=status.HTTP_200_OK)



class ListSentFriendRequestsView(BaseAPIView):
    """
    Inherits only the permission requirement from BaseAPIView.
    """
    @handle_exceptions
    def get(self, request, *args, **kwargs):
        requests = FriendRequest.objects.filter(from_user=request.user)
        if not requests.exists():

            return Response({'message': 'No friend requests sent.'}, status=status.HTTP_204_NO_CONTENT)

        serializer = FriendRequestSerializer(requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ListFriendsView(BaseAPIView):

    @handle_exceptions
    def get(self, request, *args, **kwargs):
        friendships = Friendship.objects.filter(user1=request.user)
        serializer = FriendshipSerializer(friendships, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class FriendRequestsView(BaseAPIView):

    @handle_exceptions
    def get(self, request):
        friend_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
        serializer = FriendRequestSerializer(friend_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchUsersView(BaseAPIView):

    @handle_exceptions
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        if query:

            users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)

            serializer = CustomUserSerializer(users, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'detail': 'No query provided.'}, status=status.HTTP_400_BAD_REQUEST)
