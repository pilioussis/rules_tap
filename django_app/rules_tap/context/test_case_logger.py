import uuid
from django.test import TestCase
from .logger import logger



test_case_token = str(uuid.uuid4())

def get_start_token():
    return f"Begin test {test_case_token}"

def get_end_token():
    return f"End test {test_case_token}"

class TapTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logger.info(get_start_token())


    @classmethod
    def tearDownClass(cls):
        logger.info(get_end_token())
        super().tearDownClass()