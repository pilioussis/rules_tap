from datetime import datetime
from contextlib import contextmanager
from django.test import TestCase

chunk_times = None

class TrackAction:
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


class TrackedTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        save_track_action(TrackAction.START)


    @classmethod
    def tearDownClass(cls):
        save_track_action(TrackAction.STOP)
        super().tearDownClass()
