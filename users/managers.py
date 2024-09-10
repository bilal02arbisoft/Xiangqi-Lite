from django.contrib.auth.models import BaseUserManager

from users.error_handling import handle_exceptions


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser model with methods to create users and superusers.
    """
    @handle_exceptions
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given email, username, and password.
        """
        if not username:

            raise ValueError('The Username field must be set')
        if not email:

            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    @handle_exceptions
    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:

            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:

            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, username, password, **extra_fields)
