from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        return Profile.objects.create(user=instance)