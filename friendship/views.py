from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from users.models import CustomUser as User
from friendship.models import FriendRequest, Friendship
from users.serializers import CustomUserSerializer


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:

            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_user = User.objects.get(username=username)

            if to_user == request.user:

                return Response({'error': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

            if Friendship.objects.filter(user1=request.user, user2=to_user).exists() or \
               Friendship.objects.filter(user1=to_user, user2=request.user).exists():

                return Response({'error': 'You are already friends with this user.'}, status=status.HTTP_400_BAD_REQUEST)

            friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
            if created:

                return Response({'message': 'Friend request sent!'}, status=status.HTTP_201_CREATED)
            else:

                return Response({'message': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:

            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from_username = request.data.get('from_user')
        if not from_username:
            return Response({'error': 'From user is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_user = User.objects.get(username=from_username)
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=request.user)
            if friend_request.status == 'accepted':
                return Response({'message': 'Friend request already accepted.'}, status=status.HTTP_400_BAD_REQUEST)

            friend_request.accept()
            return Response({'message': 'Friend request accepted!'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)


class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from_username = request.data.get('from_user')
        if not from_username:
            return Response({'error': 'From user is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_user = User.objects.get(username=from_username)
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=request.user)
            if friend_request.status == 'rejected':
                return Response({'message': 'Friend request already rejected.'}, status=status.HTTP_400_BAD_REQUEST)

            friend_request.reject()
            return Response({'message': 'Friend request rejected!'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)


class ListSentFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        requests = FriendRequest.objects.filter(from_user=request.user)
        if not requests.exists():
            return Response({'message': 'No friend requests sent.'}, status=status.HTTP_200_OK)

        request_data = [{"to_user": fr.to_user.username, "status": fr.status, "timestamp": fr.timestamp} for fr in
                        requests]
        return Response(request_data, status=status.HTTP_200_OK)


class ListFriendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        friendships = Friendship.objects.filter(user1=request.user)

        friends_data = []
        for friendship in friendships:
            friend = friendship.user2
            friend_data = CustomUserSerializer(friend).data
            friend_data['since'] = friendship.created
            friends_data.append(friend_data)

        return Response(friends_data, status=status.HTTP_200_OK)

class FriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friend_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
        serialized_requests = [
            CustomUserSerializer(request.from_user).data
            for request in friend_requests
        ]

        return Response(serialized_requests)


class SearchUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        if query:

            users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)

            serializer = CustomUserSerializer(users, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)

