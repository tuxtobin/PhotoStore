import logging
import os
import pickle
import concurrent.futures
import shutil
from store import photos


# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                              '%Y-%m-%d %H:%M')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Process each file in each directory
def processing(source, destination, dryrun, exiftool):
    logger.debug('Calling processing')
    workers = 5

    # Set variables
    dup_path = os.path.join(destination, 'Dup')
    bad_path = os.path.join(destination, 'Bad')
    master_hashes = dict()
    directory_hashes = dict()

    # Create list of all the source directories
    src_paths = [dir.path for dir in os.scandir(source) if dir.is_dir()]

    # Create list of all the destination directories
    dest_paths = [dir.path for dir in os.scandir(destintion) if dir.is_dir()]
    # Remote the duplicate and bad paths - don't want to process these
    paths.remove(dup_path)
    paths.remove(bad_path)

    for path in dest_paths:
        hash_file = os.path.join(path, 'file_hash.pkl')
        if os.path.isfile(hash_file):
            with open(hash_file, 'rb') as f:
                hash_map = pickle.load(f)
        directory_hashes.update(hash_map)

    for path in src_paths:
        process_files(path, destination, dryrun, exiftool, dup_path, bad_path, master_hashes, directory_hashes)

    return


# Check file doesn't already exist in target directory and return a suitable new name
def check_file(file):
    logger.debug('Checking file already exists')
    tmp_file = file
    incr = 1
    renamed = ''
    while os.path.exists(tmp_file):
        root, ext = os.path.splitext(file)
        tmp_file = root + '.' + str(incr) + ext
        incr += 1
        renamed = ' (renamed)'
    return tmp_file, renamed


def process_files(path, destination, dryrun, exiftool, dup_path, bad_path, master_hashes, directory_hashes):
    logger.debug('Processing directory {}'.format(path))
    invalid_types = ['.db', '.aae', '.info', '.scn', '.lib', '.ini', '.zip', '.thm', '.log', '.txt', '.pkl']

    files = [file for file in os.scandir(path) if file.is_file()]
    for file in files:
        # Ignore invalid file types
        if os.path.splitext(file.name)[1].lower() in invalid_types:
            continue

        logger.debug('Processing file {}'.format(file.name))
        photo_size = photos.photo_size(file.path)
        photo_hash = photos.photo_hash(file.path)
        photo_data = photos.photo_metadata(exiftool, file.path)

        if photo_size == 0:
            bad_file = os.path.join(bad_path, file.name)
            bad_file, renamed = check_file(bad_file)
            if not dryrun:
                shutil.copy2(file.path, bad_file)
            logger.info('{} is empty{}'.format(file.path, renamed))
        elif photo_data is None:
            bad_file = os.path.join(bad_path, file.path)
            bad_file, renamed = check_file(bad_file)
            if not dryrun:
                shutil.copy2(file.path, bad_file)
            logger.info('{} is bad{}'.format(file.path, renamed))
        elif photo_hash in master_hashes:
            dup_file = os.path.join(dup_path, file.path)
            dup_file, renamed = check_file(dup_file)
            if not dryrun:
                shutil.copy2(file.path, dup_file)
            logger.info('{} is duplicate of {}{}'.format(file.path, master_hashes[photo_hash], renamed))
        elif photo_hash in directory_hashes:
            logger.info('{} already exists {}'.format(file.path, directory_hashes[photo_hash]))
        else:
            photo = photos.Photo(file.name, path)
            photo.set_size(photo_size)
            photo.set_hash(photo_hash)
            photo.extract_date()
            photo.find_date()

            directory_date = getattr(photo, 'directory_date')
            dest_dir = os.path.join(destination, directory_date)
            dest_path = os.path.join(dest_dir, file.name)
            dest_path, renamed = check_file(dest_path)

            if not dryrun:
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                shutil.copy2(file.path, dest_path)

            logger.info('{} copied to {}{}'.format(file.path, dest_path, renamed))

            master_hashes[photo_hash] = file.path

    return
