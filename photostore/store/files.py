import logging
import os
from dirhash import dirhash
import pickle
import concurrent.futures
from store import photos


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                              '%Y-%m-%d %H:%M')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def checksums(destination):
    logger.debug('Calling checksums')

    dup_path = os.path.join(destination, 'Dup')
    bad_path = os.path.join(destination, 'Bad')

    paths = [dir.path for dir in os.scandir(destination) if dir.is_dir()]
    paths.remove(dup_path)
    paths.remove(bad_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(directory_checksum, paths)

    return


def directory_checksum(directory):
    logger.debug('Processing {}'.format(directory))
    photo_hashes = dict()
    files = [file.path for file in os.scandir(directory) if file.is_file()]
    for file in files:
        if os.path.splitext(file)[1].lower() in ['.log', '.txt', '.pkl']:
            continue
        photo_hash = photos.file_hash(file)
        photo_hashes[file] = photo_hash

    hash_file = os.path.join(directory, 'file_hash.pkl')
    with open(hash_file, 'wb') as f:
        pickle.dump(photo_hashes, f)

    return
