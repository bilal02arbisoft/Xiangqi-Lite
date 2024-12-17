import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils import timezone

from users.managers import CustomUserManager
from users.tasks import send_otp_email_task


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that extends AbstractBaseUser and PermissionsMixin.
    """
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]*$',
        message='Username must be alphanumeric (only letters and numbers are allowed).'
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        null=False,
        blank=False
    )
    username = models.CharField(
        unique=True,
        max_length=30,
        validators=[username_validator],
        null=False,
        blank=False
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    otp_generated_at = models.DateTimeField(blank=True, null=True)
    email_verification_otp = models.CharField(max_length=6, blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]


    def __str__(self):

        return self.username

    def generate_otp(self):
        """
        Generates a one-time password (OTP) for email verification and sends it to the user's email.
        """
        otp = ''.join(secrets.choice(string.digits) for _ in range(6))
        self.email_verification_otp = otp
        self.otp_generated_at = timezone.now()
        self.save()
        self._send_email('Your Email Verification OTP', f'Your OTP for email verification is {otp}.'
                                                        f' It is valid for 10 minutes.')

        return otp

    def _send_email(self, subject, message):
        """
        Sends an email to the user's email address.
        """
        send_otp_email_task.delay(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    def verify_email(self):
        """
        Sends an email confirming successful email verification.
        """
        self.is_email_verified = True
        self.email_verification_otp = None
        self.otp_generated_at = None
        self.save()
        self._send_email('Email Verification Successful', 'Your email has been verified.')

    def is_otp_valid(self, otp):
        """
        Validates the OTP provided by the user.
        """

        if self.email_verification_otp == otp and (timezone.now() - self.otp_generated_at) <= timedelta(minutes=10):
            self.verify_email()

            return True

        return False


class Profile(models.Model):
    """
    Model representing user profiles and additional info.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='profile',
        on_delete=models.CASCADE
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)



class Player(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player')
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    games_drawn = models.IntegerField(default=0)
    SKILL_LEVEL_CHOICES = [
        ('newbie', 'Newbie'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='newbie')
    SKILL_LEVEL_RATINGS = {
        'newbie': 600.0,
        'beginner': 1200.0,
        'intermediate': 1800.0,
        'advanced': 2400.0,
    }
    rating = models.FloatField(default=600.0)

    def save(self, *args, **kwargs):
        """
        Overriding save method to automatically set the rating based on the skill level.
        """
        self.rating = self.SKILL_LEVEL_RATINGS.get(self.skill_level, 600.0)
        super().save(*args, **kwargs)

    def __str__(self):

        return f'{self.user.username} - {self.skill_level} - {self.rating}'
