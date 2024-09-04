from django.contrib.auth.password_validation import validate_password
from django.db.models.signals import post_save
from rest_framework import serializers

from users.error_handling import handle_exceptions
from users.models import CustomUser, Player, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.
    """
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'country']


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    """
    profile = ProfileSerializer()
    skill_level = serializers.ChoiceField(choices=Player.SKILL_LEVEL_CHOICES, write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'profile', 'is_email_verified', 'skill_level']
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def validate_email(value):
        """
        Validate that the email is unique.
        """
        if CustomUser.objects.filter(email=value).exists():

            raise serializers.ValidationError('A user with this email already exists.')

        return value

    @staticmethod
    def validate_username(value):
        """
        Validate that the username is unique.
        """
        if CustomUser.objects.filter(username=value).exists():

            raise serializers.ValidationError('A user with this username already exists.')

        return value

    @staticmethod
    def validate_password(value):
        """
        Validate that the password meets all security requirements.
        """
        validate_password(value)

        return value

    def validate(self, data):
        """
        Validate that password and email are not the same.
        """
        password = data.get('password')
        email = data.get('email')
        if password and email and plain_password_equals_email(password, email):

            raise serializers.ValidationError('Password and email cannot be the same.')

        return data


    def create(self, validated_data):
        """
        Create a new user and associated profile.
        """
        profile_data = validated_data.pop('profile', {})
        skill_level = validated_data.pop('skill_level', None)
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        post_save.send(sender=user.__class__, instance=user, created=True, manual=True, skill_level=skill_level)
        if profile_data:

            Profile.objects.create(user=user, **profile_data)

        return user

    @handle_exceptions
    def update(self, instance, validated_data):
        """
        Update an existing user and associated profile.
        """
        profile_data = validated_data.pop('profile', {})
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile, created = Profile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for handling password change requests.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    @staticmethod
    def validate_new_password(value):
        """
        Validate the new password.
        """
        validate_password(value)

        return value

    def validate(self, data):
        """
        Validate the old and new passwords.
        """
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        user = self.context.get('user')

        if not user.check_password(old_password):

            raise serializers.ValidationError('Old password is incorrect.')
        if plain_password_equals_email(new_password, user.email):

            raise serializers.ValidationError('New password cannot be the same as the email.')
        if user.check_password(new_password):

            raise serializers.ValidationError('Please use a different password.')

        return data


class RequestOtpSerializer(serializers.Serializer):
    """
    Serializer for requesting an OTP.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate that the email exists in the system.
        """
        if not CustomUser.objects.filter(email=value).exists():

            raise serializers.ValidationError(f"This email {value} is not registered.")

        return value


    def save(self):
        """
        Generate and send OTP to the user's email.
        """
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)
        user.generate_otp()

        return user


class VerifyOtpSerializer(serializers.Serializer):
    """
    Serializer for verifying an OTP.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        """
        Validate the OTP and email combination.
        """
        user = CustomUser.objects.get(email=data['email'])
        if not user.is_otp_valid(data['otp']):

            raise serializers.ValidationError('Invalid or expired OTP.')

        return data

    def save(self):
        """
        Mark the user's email as verified.
        """
        user = CustomUser.objects.get(email=self.validated_data['email'])
        user.is_email_verified = True
        user.email_verification_otp = None
        user.otp_generated_at = None
        user.save()

        return user


def plain_password_equals_email(password, email):
    """
    Check if the password is the same as the email.
    """
    return password == email


def plain_password_equals_username(password, username):
    """
    Check if the password is the same as the username.
    """
    return password == username
