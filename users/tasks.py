from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_otp_email_task(subject, message, from_email, recipient_list):
    """
    Celery task to send an OTP email.
    """
    send_mail(subject, message, from_email, recipient_list)

@shared_task
def create_player_profile_task(user_id, skill_level):
    """
    Celery task to create a Player profile for a CustomUser instance.
    """
    from users.models import CustomUser, Player
    user = CustomUser.objects.get(id=user_id)
    Player.objects.create(user=user, skill_level=skill_level)
