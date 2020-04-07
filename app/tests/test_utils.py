# -*- coding: utf-8 -*-

import os

from django.test import TestCase, mock
from PIL import Image

from .. import utils

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, 'fixtures')


# ----------------------------------------------------------------------------------------------------------------------
class JsonMock:
    def __init__(self, value):
        self.value = value

    def json(self):
        return {'success': self.value}


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

    # ------------------------------------------------------------------------------------------------------------------
    @mock.patch('app.utils.requests.post', new=mock.Mock(return_value=JsonMock(True)))
    def test_validate_captcha_success(self):
        result = utils.validate_captcha('some_key')
        self.assertTrue(result)

    # ------------------------------------------------------------------------------------------------------------------
    @mock.patch('app.utils.requests.post', new=mock.Mock(return_value=JsonMock(False)))
    def test_validate_captcha_fail(self):
        result = utils.validate_captcha('some_key')
        self.assertFalse(result)
