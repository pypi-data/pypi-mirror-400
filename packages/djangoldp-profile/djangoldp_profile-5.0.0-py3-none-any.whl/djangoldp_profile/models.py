from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djangoldp.models import Model
from djangoldp.permissions import ReadOnly, OwnerPermissions

class Profile(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    slug = models.SlugField(unique=True, blank=True)
    available = models.BooleanField(null=True, blank=True)
    job = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)

    def jabberID(self):
        try:
            return self.user.chatProfile.jabberID
        except:
            return None

    class Meta:
        auto_author = 'user'
        permission_classes = [ReadOnly|OwnerPermissions]
        lookup_field = 'slug'


    def __str__(self):
        return '{} ({})'.format(self.user.get_full_name(), self.user.username)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, slug=instance.username)
    else:
        try:
            instance.profile.slug = instance.username
            instance.profile.save()
        except:
            pass