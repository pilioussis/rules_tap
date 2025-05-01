from datetime import datetime
from enum import Enum
from unittest import TextTestResult
from contextlib import contextmanager
from django.test.runner import DiscoverRunner


def run_tests():
    test_runner = DiscoverRunner(verbosity=2)
    all_tests = ['.'] # Should prolly go in a config
    test_runner.keepdb = True
    test_runner.run_tests(all_tests)


class TrackAction(Enum):
    START = 'START'
    STOP = 'STOP'

# Global variable to store start and stop signals
_chunk_times = None


@contextmanager
def chunk_time_tracker():
    """ Reset and expose the global _chunk_times variable to the calling context """
    global _chunk_times
    _chunk_times = []
    try:
        yield _chunk_times
    finally:
        pass


def save_track_action(action: TrackAction):
    """ Store start and stop signals in the _chunk_times global variable. """
    global _chunk_times
    if _chunk_times is None:
        raise Exception(f'Track context manager {chunk_time_tracker} not initialized')
    _chunk_times.append((action, datetime.now()))


# Functions to capture when tests start/stop
def startTest(self, test):
    super(TextTestResult, self).startTest(test)
    save_track_action(TrackAction.START)

def stopTest(self, test):
    save_track_action(TrackAction.STOP)
    super(TextTestResult, self).stopTest(test)

# Monkey patch base test case functions
TextTestResult.startTest = startTest
TextTestResult.stopTest = stopTest