from django.db import models
from users.managers import CustomUserManager
from django.conf import settings
from datetime import timedelta
import random
import string
from django.utils import timezone
from users.tasks import send_otp_email_task, send_verification_email_task
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
    is_email_verified = models.BooleanField(default=False)
    email_verification_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):

        return self.username

    def generate_otp(self):
        otp = ''.join(random.choices(string.digits, k=6))
        self.email_verification_otp = otp
        self.otp_generated_at = timezone.now()
        self.save()
        self.send_otp_email(otp)
        return otp

    def send_otp_email(self, otp):
        subject = 'Your Email Verification OTP'
        message = f'Your OTP for email verification is {otp}. It is valid for 10 minutes.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.email]
        send_otp_email_task.delay(subject, message, from_email, recipient_list)

    def send_verify_email(self):
        subject = 'Email Verification Successful'
        message = f'Your email has been verified.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.email]
        send_verification_email_task.delay(subject, message, from_email, recipient_list)

    def is_otp_valid(self, otp):
        now = timezone.now()
        if self.email_verification_otp == otp and (now - self.otp_generated_at) <= timedelta(minutes=10):
            self.is_email_verified = True
            self.save()
            return True
        return False

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
    rating = models.FloatField(default=600.0)
    country = models.CharField(max_length=50, null=True, blank=True)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='newbie')

    def save(self, *args, **kwargs):

        self.rating = self.SKILL_LEVEL_RATINGS.get(self.skill_level, 600.0)
        super().save(*args, **kwargs)





