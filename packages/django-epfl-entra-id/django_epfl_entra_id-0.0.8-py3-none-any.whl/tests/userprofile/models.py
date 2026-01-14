from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """UserProfile model"""

    user = models.OneToOneField(
        User, null=True, related_name="profile", on_delete=models.CASCADE
    )

    sciper = models.CharField(max_length=10, null=True, blank=True, unique=True)
    classe = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(max_length=100, null=True, blank=True)


# Trigger for creating a profile on user creation
def user_post_save(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


# Register the trigger
models.signals.post_save.connect(user_post_save, sender=User)
