import hashlib
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                              '%Y-%m-%d %H:%M')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def file_hash(file):
    with open(file, 'rb', buffering=0) as fh:
        return hashlib.file_digest(fh, 'sha256').hexdigest()
