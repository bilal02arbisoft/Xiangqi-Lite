from rest_framework import serializers

from friendship.models import FriendRequest, Friendship
from users.models import CustomUser as User
from users.serializers import CustomUserSerializer as UserSerializer


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying FriendRequest objects.
    Serializes 'from_user' and 'to_user' using the CustomUserSerializer,
    """
    from_user = UserSerializer()
    to_user = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = ['from_user', 'to_user', 'status', 'timestamp']


class FriendshipSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying Friendship objects.
    Serializes 'user1' and 'user2' using the CustomUserSerializer.
    """
    user1 = UserSerializer()
    user2 = UserSerializer()

    class Meta:
        model = Friendship
        fields = ['user1', 'user2', 'created']


class FriendRequestCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new friend request.
     Validates the 'username' field to ensure the user cannot send a request to themselves,
    """
    username = serializers.CharField()

    def validate_username(self, value):
        request_user = self.context['request'].user
        to_user = User.objects.get(username=value)

        if to_user == request_user:

            raise serializers.ValidationError('You cannot send a friend request to yourself.')

        if Friendship.objects.filter(user1=request_user, user2=to_user).exists() or \
           Friendship.objects.filter(user1=to_user, user2=request_user).exists():

            raise serializers.ValidationError('You are already friends with this user.')

        return value


class FriendRequestActionSerializer(serializers.Serializer):
    """
    Serializer for handling actions on a friend request (accept/reject).
    Validates the 'from_user' and 'action' fields, and checks whether the action
     has already been performed on the friend request.
    """
    from_user = serializers.CharField()
    action = serializers.ChoiceField(choices=['accepted', 'rejected'])

    def validate(self, data):
        request_user = self.context['request'].user
        from_username = data['from_user']
        from_user = User.objects.get(username=from_username)
        friend_request = FriendRequest.objects.get(from_user=from_user, to_user=request_user)
        if friend_request.status == data['action']:

            raise serializers.ValidationError(f"Friend request already {data['action']}.")
        self.context['friend_request'] = friend_request

        return data
