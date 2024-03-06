import os
import logging, sys
from pathlib import Path
from colorama import Fore, Style

# LOGGER Configuration 
LOGS_DIR = Path(__file__).parent.parent.resolve()

class CustomFormatter(logging.Formatter):

    green = Fore.GREEN
    grey = Style.DIM
    yellow = Fore.YELLOW
    red = Fore.RED
    bold_red = f"{Style.BRIGHT}{Fore.RED}"
    reset = Style.RESET_ALL

    format = "%(asctime)s - %(filename)-20s - %(levelname)-8s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
logger = logging.getLogger('scanner_logger')
c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)

if os.path.exists(f'{LOGS_DIR}/logs') == False:
    os.mkdir(f'{LOGS_DIR}/logs')
with open(f'{LOGS_DIR}/logs/runtime.logs', 'w') as f:
    pass

f_handler = logging.FileHandler(f'{LOGS_DIR}/logs/runtime.logs')
f_handler.setLevel(logging.WARNING)

c_handler.setFormatter(CustomFormatter())
f_handler.setFormatter(CustomFormatter())

logger.addHandler(c_handler)
logger.addHandler(f_handler)
logging.basicConfig(level=logging.DEBUG, handlers=[logging.NullHandler()])