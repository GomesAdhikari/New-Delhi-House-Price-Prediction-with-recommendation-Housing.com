import logging
import os
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%d-%m-%Y %H-%M-%S')}.log"

log_folder = os.path.join(os.getcwd(),
                          'logs',
                          (LOG_FILE))

os.makedirs(log_folder,exist_ok=True)

log_file_path = os.path.join(log_folder,LOG_FILE)

logging.basicConfig(level=logging.INFO,
                    filename=log_file_path,
                    format='[%(asctime)s] - %(levelname)s - %(name)s - %(lineno)s - %(message)s')

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

fmt = '[%(asctime)s] - %(levelname)s - %(name)s - %(lineno)s - %(message)s'
Formatter = logging.Formatter(fmt)

Streamhandler = logging.StreamHandler()
Streamhandler.setFormatter(Formatter)
logger.addHandler(Streamhandler)

if __name__ == '__main__':
    logger.info('Logging Has started')
