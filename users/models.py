from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from picklefield.fields import PickledObjectField

from users.validators import validate_file_size


class UserProfile(models.Model):
    # User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')

    # Uneditable and from SSO
    roll_number = models.CharField(max_length=255, default='', null=True, blank=True)
    email = models.EmailField(default='', null=True, blank=True)

    # From SSO but editable
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    profile_picture = models.ImageField(upload_to='userMedia', null=True, blank=True, validators=[validate_file_size])

    # For Admin Interface
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

    # Stores the previous profile_json to check updation situation
    store_json = PickledObjectField(null=True, blank=True)

    def __str__(self):
        return self.user.username


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)
