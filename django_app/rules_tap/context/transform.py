import os
import re
import inflection

from .logger import CODE_LOG_FILE, SQL_LOG_FILE, QUERY_DIR
from .test_case_logger import get_start_token, get_end_token
from contextlib import ExitStack




def starts_with_date_format(s: str) -> bool:
    """
    Determine if a string starts with the date format 'YYYY-MM-DD HH:MM:SS,SSS'.
    """
    date_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
    return bool(re.match(date_pattern, s))


def write_line(query_file, line: str):
    if not query_file:
        return
    
    query_file.write(line + '\n')

class QueryFileManager():
    class LineType:
        START = 'start'
        END = 'end'
        LOG = 'log'

    def __init__(self):
        self.query_number = 1
        self.query_file = None

    def get_line_type(self, line: str) -> LineType:
        if not self.query_file and line.endswith(get_start_token()):
            return self.LineType.START
        elif self.query_file and line.endswith(get_end_token()):
            return self.LineType.END
        else:
            return self.LineType.LOG

    def open_query_file(self):
        self.query_file = open(QUERY_DIR / f'query_{self.query_number}.txt', 'w')
    
    def close_query_file(self):
        if not self.query_file:
            raise Exception("Unable to close query file, no existing file")
        self.query_file.close()
        self.query_number += 1
        self.query_file = None

    def handle_code_log_line(self, line: str):
        line_type = self.get_line_type(line)
        if line_type == self.LineType.START:
            self.open_query_file()
        elif line_type == self.LineType.END:
            self.close_query_file()
        elif self.query_file:
            to_write = line[25:]
            if to_write:
                func_name, doc_string = to_write.split('|', 1)
                func_name = ': '.join(func_name.split('.')[-2:])
                self.query_file.write(inflection.humanize(inflection.underscore(func_name)) + '\n')
                if doc_string:
                    self.query_file.write(doc_string + '\n')
                

    def handle_sql_log_line(self, line: str):
        if self.query_file:
            if any(k in line for k in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                to_write = line.split(';', 1)[0]
                to_write = to_write[33:]
                self.query_file.write(to_write + '\n')


def transform_logs():
    query_file_manager = QueryFileManager()

    with ExitStack() as stack:
        code_log_file = stack.enter_context(open(CODE_LOG_FILE, 'r'))
        sql_log_file = stack.enter_context(open(SQL_LOG_FILE, 'r'))
            
        code_log_line = code_log_file.readline()
        sql_log_line = sql_log_file.readline()

        while code_log_line or sql_log_line:
            if not code_log_line:
                query_file_manager.handle_sql_log_line(sql_log_line)
                sql_log_line = sql_log_file.readline().strip()
            elif not sql_log_line:
                query_file_manager.handle_code_log_line(code_log_line)
                code_log_line = code_log_file.readline().strip()
            else:
                code_log_time = code_log_line.split('|', 1)[0]
                sql_log_time = sql_log_line.split('|', 1)[0]

                if code_log_time <= sql_log_time and starts_with_date_format(sql_log_line):
                    query_file_manager.handle_code_log_line(code_log_line)
                    code_log_line = code_log_file.readline().strip()
                else:
                    query_file_manager.handle_sql_log_line(sql_log_line)
                    sql_log_line = sql_log_file.readline().strip()

        