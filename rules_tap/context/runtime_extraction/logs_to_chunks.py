import re
from datetime import datetime
from colorama import Fore, Style, Back
from rules_tap.common import get_hash, Config

from .chunk_from_test_case import TrackAction
from contextlib import ExitStack
from .loggers import RuntimeLogger


class FileTracker:
    def __init__(self, runtime_logger: RuntimeLogger, stack: ExitStack):
        self.runtime_logger = runtime_logger
        self.file = stack.enter_context(open(runtime_logger.logfile, 'r'))
        self.next_line()
    
    def next_line(self):
        full_line = self.file.readline()
        if not full_line:
            self.line = None
            self.time = None
            return
        full_line = full_line.strip()
        if not full_line:
            self.next_line()
            return
        split_line = full_line.split('|', 1)
        if len(split_line) == 1:
            self.line = full_line
        else:
            self.line = self.runtime_logger.line_processor(split_line[1])
            self.time = datetime.strptime(split_line[0], '%Y-%m-%d %H:%M:%S,%f')


class TrackerGroup:
    def __init__(self, file_trackers: list[FileTracker]):
        self.file_trackers = file_trackers

    def read_up_to_date(self, date: datetime):
        out = []
        while True:
            had_line = False
            for file_tracker in self.file_trackers:
                if file_tracker.time and file_tracker.time < date:
                    if file_tracker.line:
                        out.append(file_tracker.line)
                    file_tracker.next_line()
                    had_line = True
            if not had_line:
                break
        return out


def create_chunks(config: Config, runtime_loggers: list[RuntimeLogger], chunk_times: list[tuple[TrackAction, datetime]]):
    print()
    print(f"{Back.BLUE}{Fore.WHITE} Parsing logs for test cases: {Style.RESET_ALL}")
    with ExitStack() as stack:
        file_trackers = []
        for logger in runtime_loggers:
            file_trackers.append(FileTracker(logger, stack))
            
        tracker_group = TrackerGroup(file_trackers)   
        for action, time in chunk_times:
            if action == TrackAction.START:
                tracker_group.read_up_to_date(time)
                continue
            lines = tracker_group.read_up_to_date(time)
            if not lines:
                print(f"{Fore.YELLOW}No lines found for time: {time}{Style.RESET_ALL}")
                continue
            
            # Remove duplicates
            lines = list(dict.fromkeys(lines))
            
            text = '\n\n'.join(lines)
            hash_id = get_hash(text)
            file_name = config.chunk_dir / f'runtime_{hash_id}.txt'

            with open(file_name, 'w') as f:
                f.write(text)
                print(f'{Back.BLUE} - {Style.RESET_ALL} Created chunk: {Fore.CYAN}{file_name}{Style.RESET_ALL}')

