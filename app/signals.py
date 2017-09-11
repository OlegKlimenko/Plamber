# -*- coding: utf-8 -*-

import uuid

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TheUser


# ----------------------------------------------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_additional_data(sender, instance=None, created=False, **kwargs):
    """
    Creates '.models.TheUser' instance and auth_token for this instance after creating User instance.
    """
    if created:
        the_user = TheUser.objects.create(id_user=instance,
                                          auth_token=uuid.uuid5(uuid.NAMESPACE_DNS, instance.username))
        the_user.save()
