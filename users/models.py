from django.db import models
from users.managers import CustomUserManager
from django.conf import settings
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]*$',
        message='Username must be alphanumeric (only letters and numbers are allowed).'
    )
    email = models.EmailField(unique=True, validators=[EmailValidator()], null=False, blank=False)
    username = models.CharField(unique=True, max_length=30, validators=[username_validator], null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):

        return self.email


class Profile(models.Model):
    SKILL_LEVEL_CHOICES = [
        ('newbie', 'Newbie'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    SKILL_LEVEL_RATINGS = {
        'newbie': 600.0,
        'beginner': 1200.0,
        'intermediate': 1800.0,
        'advanced': 2400.0,
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    rating = models.FloatField(default=600.0)  # Default rating for 'newbie'
    country = models.CharField(max_length=50, null=True, blank=True)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='newbie')

    def save(self, *args, **kwargs):

        self.rating = self.SKILL_LEVEL_RATINGS.get(self.skill_level, 600.0)
        super().save(*args, **kwargs)





