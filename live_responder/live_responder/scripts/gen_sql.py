import sys
from colorama import Back, Fore, Style
from live_responder.config import load_config
from live_responder.logging import logger
from live_responder.sql_gen.gen_sql import generate_sql

if __name__ == "__main__":
	config = load_config()
	arg = sys.argv[1]
	sql = generate_sql(arg, config, search_k=3)

	logger.info(f"{Back.GREEN}{Fore.BLACK} Explanation {Style.RESET_ALL}\n{sql['explanation']}\n")
	logger.info(f"{Back.GREEN}{Fore.BLACK} SQL {Style.RESET_ALL}\n{sql['sql']}\n")
