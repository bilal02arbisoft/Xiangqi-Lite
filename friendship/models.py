
from django.conf import settings
from django.db import models
from django.utils import timezone


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


    class Meta:
        unique_together = ('from_user', 'to_user')
        indexes = [
            models.Index(fields=['from_user']),
            models.Index(fields=['to_user']),
        ]

    def accept(self):
        self.status = 'accepted'
        self.save()
        Friendship.objects.create(user1=self.from_user, user2=self.to_user)
        Friendship.objects.create(user1=self.to_user, user2=self.from_user)

    def reject(self):
        self.status = 'rejected'
        self.save()


class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends_of', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user1', 'user2')
        indexes = [
            models.Index(fields=['user1']),
            models.Index(fields=['user2']),
        ]
