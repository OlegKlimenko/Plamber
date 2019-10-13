# -*- coding: utf-8 -*-

import os
import uuid

from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .constants import Queues
from .models import TheUser, Post, Book
from .tasks import email_dispatch


# ----------------------------------------------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_additional_data(sender, instance=None, created=False, **kwargs):
    """
    Creates '.models.TheUser' instance and auth_token for this instance after creating User instance.
    """
    if created:
        the_user = TheUser.objects.create(id_user=instance,
                                          auth_token=uuid.uuid5(uuid.NAMESPACE_DNS,
                                                                instance.username + str(instance.date_joined)))
        the_user.save()


# ----------------------------------------------------------------------------------------------------------------------
@receiver(post_delete, sender=TheUser)
def remove_user_obj(sender, instance=None, **kwargs):
    """
    Removes standard django User model if '.models.TheUser' instance was deleted.
    """
    user = instance.id_user
    user.delete()


# ----------------------------------------------------------------------------------------------------------------------
@receiver(post_delete, sender=Book)
def remove_book_media(sender, instance=None, **kwargs):
    """
    Removes book file and book cover after deleting '.models.Book' object.
    """
    if os.path.exists(instance.book_file.path):
        os.remove(instance.book_file.path)

    if instance.photo and os.path.exists(instance.photo.path):
        os.remove(instance.photo.path)


# ----------------------------------------------------------------------------------------------------------------------
@receiver(post_save, sender=Post)
def dispatch_post_emails(sender, instance=None, created=False, **kwargs):
    """
    Sends multiple emails with new project post data to subscribed users.
    """
    if created:
        email_dispatch.apply_async(args=(instance.heading, instance.text), queue=Queues.default)
