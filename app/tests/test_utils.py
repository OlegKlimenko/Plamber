# -*- coding: utf-8 -*-

import os

from PIL import Image

from django.test import TestCase

from .. import utils

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, 'fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class UtilsTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    def test_generate_password(self):
        password = utils.generate_password()

        self.assertTrue(len(password), utils.PASSWORD_LENGTH)
        self.assertTrue(isinstance(password, str))
        self.assertTrue(password.isalnum())

    # ------------------------------------------------------------------------------------------------------------------
    def test_resize_image(self):
        img_path = os.path.join(TEST_DATA_DIR, 'test_resize_image.png')
        default_size = (400, 500)

        img = Image.open(img_path)
        self.assertEqual((img.width, img.height), default_size)

        utils.resize_image(img_path, 500)

        img = Image.open(img_path)
        self.assertEqual((img.width, img.height), (500, 625))

        utils.resize_image(img_path, default_size[0])

        img = Image.open(img_path)
        self.assertEqual((img.width, img.height), default_size)




