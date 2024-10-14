import logging
import os
from dirhash import dirhash
import pickle
import concurrent.futures
import pyminizip


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
            hash_map = pickle.load(f)
    else:
        hash_map = dict()

    # Create list of all the directories
    paths = [dir.path for dir in os.scandir(destination) if dir.is_dir()]
    # Remote the duplicate and bad paths - don't want to process these
    paths.remove(dup_path) if os.path.isdir(dup_path) else False
    paths.remove(bad_path) if os.path.isdir(bad_path) else False
    # Remove directories that are empty
    [paths.remove(path) for path in paths if not os.listdir(path)]
    # Record whether path is already known about or not
    hashes = [hash_map[path] if path in hash_map else None for path in paths]

    # Setup thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # Process each directory
        hash_matches = list(executor.map(directory_checksum, paths, hashes))

    # Determine if the directory needs to be compressed, i.e. it's hash is not in the hash_map, and
    # it doesn't match the existing hash
    compress_list = [False if path in hash_map and hash_map[path] == hash else True for path, hash in
                     zip(paths, hash_matches)]
    # Updating the hash_map with the current hashes
    for path, hash in zip(paths, hash_matches):
        hash_map[path] = hash

    if compress:
        # Setup thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Process each directory
            executor.map(directory_compress, paths, compress_list)

    # Save the hashes
    hash_file = os.path.join(destination, 'dir_hash.pkl')
    with open(hash_file, 'wb') as f:
        pickle.dump(hash_map, f)

    return


# Individual directory checksum
def directory_checksum(directory, hash):
    logger.debug('Processing {}'.format(directory))
    # Calculate the directory hash
    dir_hash = dirhash(directory, 'md5')
    match = '✔' if hash == dir_hash else '✘'
    logger.info('{} - {} {}'.format(directory, dir_hash, match))
    # Return true if hashes match else false
    return dir_hash


# Check if directory compression is necessary
def directory_compress(directory, compress):
    logger.debug('Compression check {}'.format(directory))
    zip = '.'.join([directory, 'zip'])
    if compress or not os.path.isfile(zip):
        # Compress the directory
        compress_directory(directory, zip, '%Od.$H@sgq0O4jj6xKn8')
        return


# Individual directory compression
def compress_directory(directory, zip, password):
    logger.debug('Compressing {}'.format(directory))
    files = [file.path for file in os.scandir(directory) if file.is_file()]
    pyminizip.compress_multiple(files, [], zip, password, 0)
    return
