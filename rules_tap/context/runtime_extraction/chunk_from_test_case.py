from datetime import datetime
from enum import Enum
from unittest import TextTestResult
from contextlib import contextmanager
from django.test.runner import DiscoverRunner
from django.test import TestCase

chunk_times = None

class TrackAction(Enum):
    START = 'START'
    STOP = 'STOP'


@contextmanager
def chunk_time_tracker():
    global chunk_times
    chunk_times = []
    try:
        yield chunk_times
    finally:
        pass


def save_track_action(action: TrackAction):
    global chunk_times
    if chunk_times is None:
        raise Exception(f'Track context manager {chunk_time_tracker} not initialized')
    chunk_times.append((action, datetime.now()))


def startTest(self, test):
    super(TextTestResult, self).startTest(test)
    save_track_action(TrackAction.START)

def stopTest(self, test):
    save_track_action(TrackAction.STOP)
    super(TextTestResult, self).stopTest(test)

TextTestResult.startTest = startTest
TextTestResult.stopTest = stopTest

def run_tests():
    test_runner = DiscoverRunner(verbosity=2)
    all_tests = ['.']
    test_runner.keepdb = True
    test_runner.run_tests(all_tests)
