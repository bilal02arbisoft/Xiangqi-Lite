import os

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from users.models import CustomUser, Player, Profile


@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:

        if os.path.isfile(instance.profile_picture.path):

            os.remove(instance.profile_picture.path)

@receiver(post_save, sender=CustomUser)
def create_player_profile(sender, instance, created, **kwargs):
    if created and kwargs.get('manual', False):

        skill_level = kwargs.get('skill_level', None)
        Player.objects.create(
            user=instance,
            skill_level=skill_level
        )
        instance.temp_skill_level = None
        instance.save()
