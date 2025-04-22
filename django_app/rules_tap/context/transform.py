import os
from .logger import CODE_LOG_FILE, SQL_LOG_FILE, CONTEXT_FILE

def transform_logs():
    with open(os.path.join(CODE_LOG_FILE), 'r') as code_log_file:
        with open(os.path.join(SQL_LOG_FILE), 'r') as sql_log_file:
            with open(CONTEXT_FILE, 'w') as context_file:
                code_log_line = code_log_file.readline()
                sql_log_line = sql_log_file.readline()

                while code_log_line or sql_log_line:
                    if not code_log_line:
                        print('only sql', sql_log_line)
                        context_file.write(sql_log_line)
                        sql_log_line = sql_log_file.readline()
                    elif not sql_log_line:
                        print('only code', code_log_line)
                        context_file.write(code_log_line)
                        code_log_line = code_log_file.readline()
                    else:
                        code_log_time = code_log_line.split('|', 1)[0]
                        sql_log_time = sql_log_line.split('|', 1)[0]
                        print(code_log_time <= sql_log_time, code_log_time, sql_log_time)
                        print(code_log_line, sql_log_line)
                        if code_log_time <= sql_log_time:
                            print('code first', code_log_line)
                            context_file.write(code_log_line)
                            code_log_line = code_log_file.readline()
                        else:
                            print('sql first', sql_log_line)
                            context_file.write(sql_log_line)
                            sql_log_line = sql_log_file.readline()
                