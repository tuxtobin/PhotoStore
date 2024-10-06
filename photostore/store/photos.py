import hashlib
import logging


# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                              '%Y-%m-%d %H:%M')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Determine file size
def photo_size(file):
    stat = os.stat(file)
    return stat.st_size


# Generate file hash
def photo_hash(file):
    with open(file, 'rb', buffering=0) as fh:
        return hashlib.file_digest(fh, 'sha256').hexdigest()
