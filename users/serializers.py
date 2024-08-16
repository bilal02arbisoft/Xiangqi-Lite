from rest_framework import serializers
from users.models import CustomUser, Profile
from django.contrib.auth.password_validation import validate_password


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'rating', 'profile_picture', 'country', 'skill_level']


class CustomUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def validate_email(value):
        if CustomUser.objects.filter(email=value).exists():

            raise serializers.ValidationError("A user with this email already exists.")

        return value

    @staticmethod
    def validate_username(value):
        if CustomUser.objects.filter(username=value).exists():

            raise serializers.ValidationError("A user with this username already exists.")

        return value

    @staticmethod
    def validate_password(value):
        validate_password(value)

        return value

    def validate(self, data):
        password = data.get('password')
        email = data.get('email')
        if password and email and plain_password_equals_email(password, email):

            raise serializers.ValidationError("Password and email cannot be the same.")

        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        if profile_data:

            Profile.objects.create(user=user, **profile_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile = getattr(instance, 'profile', None)
        if profile is not None:

            if profile_data:

                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
        else:
            if profile_data:

                Profile.objects.create(user=instance, **profile_data)

        return instance

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    @staticmethod
    def validate_new_password(value):
        validate_password(value)

        return value

    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        user = self.context.get('user')

        if not user.check_password(old_password):

            raise serializers.ValidationError("Old password is incorrect.")
        if plain_password_equals_email(new_password, user.email):

            raise serializers.ValidationError("New password cannot be the same as the email.")

        if user.check_password(new_password):

            raise serializers.ValidationError("Pls use different password.")

        return data


def plain_password_equals_email(password, email):

    return password == email


def plain_password_equals_username(password, username):

    return password == username
