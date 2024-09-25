import os

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from users.models import CustomUser, Profile
from users.tasks import create_player_profile_task


@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    """
    Signal handler that deletes the profile picture file from the filesystem
    when a Profile instance is deleted.
    """

    if instance.profile_picture and os.path.isfile(instance.profile_picture.path):
        os.remove(instance.profile_picture.path)

@receiver(post_save, sender=CustomUser)
def create_player_profile(sender, instance, created, **kwargs):
    """
    Signal handler that creates a Player profile for a new CustomUser instance
    if the instance was manually created and a skill level is provided.
    """

    if created and kwargs.get('manual', False):
        skill_level = kwargs.get('skill_level', None)
        create_player_profile_task.delay(instance.id, skill_level)
