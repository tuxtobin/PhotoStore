import logging
import os
from dirhash import dirhash
import pickle
import concurrent.futures
from store import photos


# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                              '%Y-%m-%d %H:%M')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Main entrypoint to perform checksums for all directories
def checksums(destination):
    logger.debug('Calling checksums')
    workers = 5

    dup_path = os.path.join(destination, 'Dup')
    bad_path = os.path.join(destination, 'Bad')

    # Create list of all the directories
    paths = [dir.path for dir in os.scandir(destination) if dir.is_dir()]
    # Remote the duplicate and bad paths - don't want to process these
    paths.remove(dup_path)
    paths.remove(bad_path)

    # Setup thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # Process each directory
        executor.map(directory_checksum, paths)

    return


# Individual directory checksum
def directory_checksum(directory):
    logger.debug('Processing {}'.format(directory))
    # Setup hash dictionary
    photo_hashes = dict()
    # Create list of files in the current directory
    files = [file.path for file in os.scandir(directory) if file.is_file()]
    # Loop over each file
    for file in files:
        # Ignore logs or metadata
        if os.path.splitext(file)[1].lower() in ['.log', '.txt', '.pkl']:
            continue
        # Determine file hash and add to the dictionary
        photo_hash = photos.photo_hash(file)
        photo_hashes[file] = photo_hash

    # Save the hashes into the dirtionary
    hash_file = os.path.join(directory, 'file_hash.pkl')
    with open(hash_file, 'wb') as f:
        pickle.dump(photo_hashes, f)

    return
