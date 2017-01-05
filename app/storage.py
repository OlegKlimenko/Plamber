# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


# ----------------------------------------------------------------------------------------------------------------------
class OverwriteStorage(FileSystemStorage):
    """
    Class for implementing overwrite user's avatar when change.
    """

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        :param name:
        :param max_length:
        :return:
        """
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))

        return name
