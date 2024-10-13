import hashlib
import logging
import exiftool
import datetime


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


# Extract image/movie metadata
def photo_metadata(exif_exe, file):
    with exiftool.ExifToolHelper(executable=exif_exe) as et:
        try:
            return et.get_metadata(file)[0]
        except exiftool.exceptions.ExifToolExecuteError:
            return [None]


# Photo class
class Photo:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.fullname = None
        self.size = None
        self.hash = None
        self.file_create_date = None
        self.file_modify_date = None
        self.exif_original_date = None
        self.qt_create_date = None
        # Currently unused but may want it later
        self.qt_media_create_date = None
        # Currently unused but may want it later
        self.qt_creation_date = None
        self.exif_tag = None
        self.directory_date = None

    # Store the file size
    def set_size(self, size):
        self.size = size

    # Store the file hash
    def set_hash(self, filehash):
        self.hash = filehash

    # Store the creation date
    def set_file_create_date(self, date):
        self.file_create_date = date

    # Store modified date
    def set_file_modify_date(self, date):
        self.file_modify_date = date

    # Store exif original date
    def set_exif_original_date(self, date):
        self.exif_original_date = date

    # Store QuickTime create date
    def set_qt_create_date(self, date):
        self.qt_create_date = date

    # Store QuickTime media creation date
    def set_qt_media_create_date(self, date):
        self.qt_media_create_date = date

    # Store QuickTime creation date
    def set_qt_creation_date(self, date):
        self.qt_creation_date = date

    # Find and store the various dates
    def extract_date(self, metadata):
        exif_tags = {'File:FileModifyDate': self.set_file_modify_date,
                     'File:FileCreateDate': self.set_file_create_date,
                     'EXIF:DateTimeOriginal': self.set_exif_original_date,
                     'QuickTime:CreateDate': self.set_qt_create_date,
                     'QuickTime:MediaCreateDate': self.set_qt_media_create_date,
                     'QuickTime:CreationDate': self.set_qt_creation_date}
        # Loop through each of the date tags and extract the date if it's valid or exists
        for tag in exif_tags.keys():
            if tag in metadata:
                date = metadata[tag][0:10]
                if date == '    :  :  ' or date == '0000:00:00':
                    continue
                date = datetime.datetime.strptime(date, '%Y:%m:%d')
                tag_dict[tag](date)
        return

    # Determine the likely year and month the photo was taken
    def find_date(self):
        # Preferred date for photos
        if self.exif_original_date is not None:
            date = self.exif_original_date
            self.exif_tag = 'EXIF:DateTimeOriginal'
        # If the file is a .mov then use QuickTime create date
        elif os.path.splitext(self.name)[1].lower() == '.mov' and self.qt_create_date is not None:
            date = self.qt_create_date
            self.exif_tag = 'QuickTime:CreateDate'
        # If neither of the above work then use the file create date if it's older than the modify date
        # this is because the modify date can be changed when the file is copied or moved
        elif self.file_create_date < self.file_modify_date:
            date = self.file_create_date
            self.exif_tag = 'File:FileCreateDate'
        # All else fails use the modify date
        else:
            date = self.file_modify_date
            self.exif_tag = 'File:FileModifyDate'

        self.directory_date = date.strftime('%Y_%m')
        return
