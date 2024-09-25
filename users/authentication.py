from django.contrib.auth.backends import ModelBackend

from users.models import CustomUser


class UsernameOrEmailBackend(ModelBackend):
    """
    Custom authentication backend to allow login with either username or email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user based on either email or username and password.
        """
        user = self.get_user_by_email_or_username(username)
        if user and user.check_password(password) and self.user_can_authenticate(user):

            return user

        return None

    def get_user_by_email_or_username(self, identifier):
        """
        Utility method to fetch a user by email or username.
        """
        try:

            return CustomUser.objects.get(email=identifier)
        except CustomUser.DoesNotExist:
            try:

                return CustomUser.objects.get(username=identifier)
            except CustomUser.DoesNotExist:

                return None
