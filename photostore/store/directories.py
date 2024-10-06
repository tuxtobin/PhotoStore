import logging
import os
from dirhash import dirhash
import pickle
from itertools import repeat


# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                              '%Y-%m-%d %H:%M')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Main entrypoint to perform checksums for all directories
def checksums(destination, compress):
    logger.debug('Calling checksums')
    workers = 5

    dup_path = os.path.join(destination, 'Dup')
    bad_path = os.path.join(destination, 'Bad')

    hash_file = os.path.join(destination, 'dir_hash.pkl')
    if os.path.isfile(hash_file):
        with open(hash_file, 'rb') as f:
            init_hash = pickle.load(f)
    else:
        init_hash = dict()

    # Create list of all the directories
    paths = [dir.path for dir in os.scandir(destination) if dir.is_dir()]
    # Remote the duplicate and bad paths - don't want to process these
    paths.remove(dup_path)
    paths.remove(bad_path)

    # Setup thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # Process each directory
        executor.map(directory_checksum, paths, repeat(compress))

    return


# Individual directory checksum
def directory_checksum(directory, compress):
    return
