import os
from datetime import datetime
from uuid import uuid4

from fujitsu_quantum.config import Config


def write_error_log(text: str) -> str:
    """Writes the given text to an error log file.

    Returns:
        str: The error log file path
    """

    log_dir = Config.config_dir + '/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # append uuid4 to the file name to prevent multiple process from writing to the same file
    log_file_name = datetime.now().strftime('%Y-%m-%d--%H-%M-%S-error-') + str(uuid4()) + ".txt"
    log_file_path = log_dir + '/' + log_file_name

    with open(log_file_path, 'w') as f:
        f.write(text)

    return log_file_path
