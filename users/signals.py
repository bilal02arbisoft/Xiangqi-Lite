from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Profile
import os

@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:

        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)
