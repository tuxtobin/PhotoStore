import argparse
import logging
import os
from pathlib import Path
from store import files, directories, process


# Main photo processing function
def store(args):
    logger.debug('Calling process')

    # Check that the source is good
    if not os.path.exists(args.source):
        logger.error('Source directory does not exist')
        exit(1)

    # Check that the destination is good
    if not os.path.exists(args.destination):
        logger.error('Destination directory does not exist')
        exit(1)

    # Check that the exiftool exists
    if not os.path.exists(args.exiftool):
        logger.error('Exiftool does not exist')
        exit(1)

    # Don't create directories if it's a dry run
    if not args.dryrun:
        Path(args.destination).mkdir(parents=True, exist_ok=True)
        dup_path = os.path.join(args.destination, 'Dup')
        bad_path = os.path.join(args.destination, 'Bad')
        Path(dup_path).mkdir(parents=True, exist_ok=True)
        Path(bad_path).mkdir(parents=True, exist_ok=True)

    # Process files
    process.processing(args.source, args.destination, args.dryrun, args.exiftool)

    return


# File functions
def file(args):
    logger.debug('Calling file')

    # Confirm the destination is good
    if not os.path.exists(args.destination):
        logger.error('Directory does not exist')
        exit(1)

    # Perform checksums
    files.checksums(args.destination)
    return


# Directory functions
def directory(args):
    logger.debug('Calling directory')

    # Confirm the destination is good
    if not os.path.exists(args.destination):
        logger.error('Directory does not exist')
        exit(1)

    # Perform directory checksums and compress (if requested)
    directories.checksums(args.destination, args.compress)
    return


def default(args):
    return


# Main function
def main():
    # Configure parent argparse with dummy function (prevents error when called without any arguments)
    parser = argparse.ArgumentParser(add_help=True)
    parser.set_defaults(func=default)
    sub_parser = parser.add_subparsers()

    # Configure separate subparsers for the individual functions
    parser_process = sub_parser.add_parser('store', help='Sort image files')
    parser_process.add_argument('-s', '--source', required=True, type=str, help='Source directory')
    parser_process.add_argument('-d', '--destination', required=True, type=str, help='Destination directory')
    parser_process.add_argument('-e', '--exiftool', required=False, type=str, help='Location of exiftool executable')
    parser_process.add_argument('-t', '--dryrun', required=False, action='store_true',
                                help='Run without copying any files')
    parser_process.set_defaults(func=store)

    parser_file = sub_parser.add_parser('file', help='Build file checksums')
    parser_file.add_argument('-d', '--destination', required=True, type=str,
                             help='Destination directory to process')
    parser_file.set_defaults(func=file)

    parser_directory = sub_parser.add_parser('directory', help='Directory processing')
    parser_directory.add_argument('-d', '--destination', required=True, type=str,
                                  help='Destination directory to process')
    parser_directory.add_argument('-c', '--compress', required=False, action='store_true',
                                  help='Compress directories where the hashes do not match')
    parser_directory.set_defaults(func=directory)

    args = parser.parse_args()
    args.func(args)
    return


# Entrypoint
if __name__ == "__main__":
    # Setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                                  '%Y-%m-%d %H:%M')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.debug('Calling main')
    main()
