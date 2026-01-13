#!/usr/bin/env python3

"""
Sync Google photos with a local directory

TODO: Sync local -> remote (leave this to Google Drive app?)
TODO: Tidy cache (either automatic or command line option) - just remove anything with a date N months before start month
TODO: When checking photos are present both locally and remotely don't just check filename (what do we check and would it help?)
TODO: Investigate access to remote photos by day - is it really too slow for practical use as the rclone web site says? - ANS: Looks feasible, but have to sync each day separately, doable though would be problems with local directories with suffixes after date - probably not worth it as month works OK.
"""

import os
import sys
import datetime
import logging
import argparse
import subprocess
import glob
import re
import shutil
import PIL
import imagehash

from collections import defaultdict

from dateutil.relativedelta import relativedelta
from PIL import Image, ExifTags

from skilleter_modules import colour

################################################################################

# Default locations for local storage of photos and videos

DEFAULT_PHOTO_DIR = os.path.expanduser('~/Pictures')
DEFAULT_VIDEO_DIR = os.path.expanduser('~/Videos')

# Default remote name to use with rclone

DEFAULT_RCLONE_REMOTE = 'GooglePhotos'

# File extensions

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.rw2', '.png', )
VIDEO_EXTENSIONS = ('.mp4', '.mov', )
IGNORE_EXTENSIONS = ('.ini', )

# Default number of months to sync

DEFAULT_MONTHS = 2

# Default number of months to keep in cache prior to current start date

DEFAULT_KEEP = 1

# Default cache location

DEFAULT_CACHE_DIR = os.path.expanduser('~/.cache/gphotosync')

# Enum of filetypes

FILETYPE_IMAGE = 0
FILETYPE_VIDEO = 1
FILETYPE_UNKNOWN = 2
FILETYPE_IGNORE = 3

# Regexes for matching date strings

YYYY_MM_DD_re = re.compile(r'^(\d{4}):(\d{2}):(\d{2})')
IMG_DATE_re = re.compile(r'(?:IMG|VID)[-_](\d{4})(\d{2})(\d{2})[-_.].*')

GENERAL_DATE_re = re.compile(r'(\d{4})[-_ ](\d{2})[-_ ](\d{2})')

YEAR_MONTH_PATH_re = re.compile(r'/(\d{4})/(\d{2})/')

YYYY_MM_re = re.compile(r'(\d{4})-(\d{2})')

DUP_RE = re.compile(r'(.*) \{aalq_f.*\}(.*)')

# Date format for YYYY-MM

DATE_FORMAT = '%Y-%m'

# If two pictures with the same name prefix have a hash differing by less than
# this then we don't hash the duplicates

MIN_HASH_DIFF = 15

################################################################################

def parse_yyyymm(datestr):
    """Convert a date string in the form YYYY-MM to a datetime.date"""

    date_match = YYYY_MM_re.fullmatch(datestr)

    if not date_match:
        colour.error(f'ERROR: Invalid date: {datestr}')

    return datetime.date(int(date_match.group(1)), int(date_match.group(2)), day=1)

################################################################################

def parse_command_line():
    """Parse and validate the command line options"""

    parser = argparse.ArgumentParser(description='Sync photos from Google Photos')

    today = datetime.date.today()

    default_end_date = datetime.date(today.year, today.month, 1)

    parser.add_argument('--verbose', '-v', action='store_true', help='Output verbose status information')
    parser.add_argument('--dryrun', '-D', action='store_true', help='Just list files to be copied, without actually copying them')
    parser.add_argument('--picturedir', '-P', action='store', default=DEFAULT_PHOTO_DIR, help=f'Location of local picture storage directory (defaults to {DEFAULT_PHOTO_DIR})')
    parser.add_argument('--videodir', '-V', action='store', default=DEFAULT_VIDEO_DIR, help=f'Location of local video storage directory (defaults to {DEFAULT_VIDEO_DIR})')
    parser.add_argument('--start', '-s', action='store', default=None, help='Start date (in the form YYYY-MM, defaults to current month)')
    parser.add_argument('--end', '-e', action='store', default=None, help=f'End date (in the form YYYY-MM, defaults to {DEFAULT_MONTHS} before the start date)')
    parser.add_argument('--months', '-m', action='store', type=int, default=None, help='Synchronise this number of months of data (current month included)')
    parser.add_argument('--cache', '-c', action='store', default=DEFAULT_CACHE_DIR, help=f'Cache directory for Google photos (defaults to {DEFAULT_CACHE_DIR})')
    parser.add_argument('--rclone', '-r', action='store', default=DEFAULT_RCLONE_REMOTE, help=f'rclone remote name for Google photos (defaults to {DEFAULT_RCLONE_REMOTE})')
    parser.add_argument('--no-update', '-N', action='store_true', help='Do not update local cache')
    parser.add_argument('--keep', '-k', action='store', type=int, default=DEFAULT_KEEP, help=f'Keep this number of months before the start date in the cache (defaults to {DEFAULT_KEEP})')
    parser.add_argument('--skip-no-day', '-z', action='store_true', help='Don\'t sync files where the day of the month could not be determined')
    parser.add_argument('action', nargs='*', help='Actions to perform (report or sync)')

    args = parser.parse_args()

    # Set the start and end date based on parameters and defaults.
    # Use can specify between zero and up to 2 of start date, end date, and number of months

    if args.months and args.start and args.end:
        colour.error('You cannot specify a number of months and a start date AND an end date')

    # If nothing specified, then we sync the default number of months ending at this month

    if not args.start and not args.end and not args.months:
        args.months = DEFAULT_MONTHS

    if args.start:
        # If the start date has been specified then use the specified end data, or end date + months

        args.start = parse_yyyymm(args.start)

        if args.end:
            args.end = parse_yyyymm(args.end)
        else:
            args.end = args.start + relativedelta(months=args.months-1)

    else:
        # Otherwise, use the end date if specified and calculate the start date as being end_date - months

        if args.end:
            args.end = parse_yyyymm(args.end)
        else:
            args.end = default_end_date

        args.start = args.end - relativedelta(months=args.months-1)

    # Sanity check

    if args.end > default_end_date:
        colour.error(f'End date for synchronisation is in the future ({args.end})')

    # Configure debugging

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Report parameters if verbose

    logging.debug('Start:     %s', args.start)
    logging.debug('End:       %s', args.end)
    logging.debug('Months:    %d', args.months)
    logging.debug('Pictures:  %s', args.picturedir)
    logging.debug('Videos:    %s', args.videodir)
    logging.debug('Cache:     %s', args.cache)
    logging.debug('Keep:      %d', args.keep)
    logging.debug('rclone:    %s', args.rclone)
    logging.debug('No update: %d', args.no_update)
    logging.debug('Dry run:   %d', args.dryrun)

    args.local_dir = {'photo': args.picturedir, 'video': args.videodir}

    return args

################################################################################

def get_exif_data(image):
    """Return EXIF data for the image as a dictionary"""

    try:
        img = Image.open(image)

        img_exif = img.getexif()
    except OSError as exc:
        logging.info('Error reading EXIF data for %s - %s', image, exc)
        img_exif = None

    result = {}

    if img_exif is None:
        return result

    for key, val in img_exif.items():
        if key in ExifTags.TAGS:
            result[ExifTags.TAGS[key]] = val
        else:
            result[key] = val

    return result

################################################################################

def get_filetype(filename):
    """Return the type of a file"""

    _, ext = os.path.splitext(filename)

    ext = ext.lower()

    if ext in IMAGE_EXTENSIONS:
        return FILETYPE_IMAGE

    if ext in VIDEO_EXTENSIONS:
        return FILETYPE_VIDEO

    if ext in IGNORE_EXTENSIONS:
        return FILETYPE_IGNORE

    return FILETYPE_UNKNOWN

################################################################################

def find_files(directory_wildcards):
    """Return a list of all the files in the specified directory tree, which can contain wildcards,
       as 3 lists; pictures, videos and unknown."""

    image_list = {}
    video_list = {}
    unknown_list = []

    logging.info('Reading files in the directory tree(s) at %s', ', '.join(directory_wildcards))

    for directory_wildcard in directory_wildcards:
        directories = glob.glob(directory_wildcard)

        for directory in directories:
            for root, _, files in os.walk(directory):
                logging.debug('Reading %s', root)

                for file in files:
                    filepath = os.path.join(root, file)

                    file_type = get_filetype(filepath)

                    if file_type == FILETYPE_IMAGE:
                        try:
                            exif = get_exif_data(filepath)

                            image_list[filepath] = exif
                        except PIL.UnidentifiedImageError:
                            colour.write(f'[BOLD:WARNING:] Unable to get EXIF data from [BLUE:{filepath}]')
                            image_list[filepath] = {}

                    elif file_type == FILETYPE_VIDEO:
                        # TODO: Is there a way of getting EXIF-type data from video files? (https://thepythoncode.com/article/extract-media-metadata-in-python but does it include date info?)
                        video_list[filepath] = {}

                    elif file_type == FILETYPE_UNKNOWN:
                        unknown_list.append(filepath)

    logging.info('Read %s image files', len(image_list))
    logging.info('Read %s video files', len(video_list))
    logging.info('Read %s unknown files', len(unknown_list))

    return image_list, video_list, unknown_list

################################################################################

def get_media_date(name, info):
    """Try and determine the date for a given picture. Returns y, m, d or
       None, None, None"""

    # If the EXIF data has the date & time, just return that

    if 'DateTimeOriginal' in info:
        original_date_time = info['DateTimeOriginal']

        date_match = YYYY_MM_DD_re.match(original_date_time)
        if date_match:
            year = date_match.group(1)
            month = date_match.group(2)
            day = date_match.group(3)

            return year, month, day

    # No EXIF date and time, try and parse it out of the filename

    picture_name = os.path.basename(name)

    date_match = IMG_DATE_re.match(picture_name) or GENERAL_DATE_re.search(picture_name)

    if date_match:
        year = date_match.group(1)
        month = date_match.group(2)
        day = date_match.group(3)

        return year, month, day

    date_match = YEAR_MONTH_PATH_re.search(name)
    if date_match:
        year = date_match.group(1)
        month = date_match.group(2)
        day = '00'

        return year, month, day

    # A miserable failure

    return None, None, None

################################################################################

def sync_media_local(dryrun, skip_no_day, media_files, destination_dir):
    """Sync files from the cache to local storage"""

    # Iterate through the list of remote media_files to try work out the date and
    # time so that we can copy it the correct local location

    for media_file in media_files:
        year, month, day = get_media_date(media_file, media_files[media_file])

        # If specified, skip files where the day of the month could not be determined

        if skip_no_day and day == '00':
            day = None

        if year and month and day:
            destination_media_file_path = os.path.join(destination_dir, year, f'{year}-{month}-{day}', os.path.basename(media_file))

            if os.path.exists(destination_media_file_path):
                colour.write(f'[RED:WARNING]: Destination [BLUE:{destination_media_file_path}] already exists - file will not be overwritten!')
            else:
                destination_dir_name = os.path.dirname(destination_media_file_path)

                colour.write(f'Copying [BLUE:{media_file}] to [BLUE:{destination_dir_name}]')

                if not dryrun:
                    os.makedirs(destination_dir_name, exist_ok=True)

                    shutil.copyfile(media_file, destination_media_file_path)
        else:
            colour.write(f'[RED:ERROR]: Unable to determine where to copy [BLUE:{media_file}]')

################################################################################

def cache_directory(args, year, month):
    """Return the location of the cache directory for the specified year/month"""

    return os.path.join(args.cache, str(year), f'{month:02}')

################################################################################

def local_directory(args, mediatype, year, month):
    """Return the location of the local picture directory for the specified year/month"""

    return os.path.join(args.local_dir[mediatype], str(year), f'{year}-{month:02}')

###############################################################################

def update_cache(args, year, month):
    """Update the local cache for the specified year and month"""

    cache_dir = cache_directory(args, year, month)

    os.makedirs(cache_dir, exist_ok=True)

    # Sync Google photos for the specified year and month into it

    if not args.no_update:
        cmd = ['rclone', 'sync', '--progress', f'{args.rclone}:media/by-month/{year}/{year}-{month:02}/', cache_dir]

        colour.write('[GREEN:%s]' % '-'*80)
        colour.write(f'[BOLD:Caching photos for] [BLUE:{month:02}/{year}]')

        try:
            logging.info('Running %s', ' '.join(cmd))

            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            colour.error(f'[RED:ERROR]: Failed to sync Google photos for month [BLUE:{month}] of year [BLUE:{year}]')

################################################################################

def media_sync(dryrun, skip_no_day, media, media_files, local_dir):
    """Given a media type and list of local and remote files of the type, check
       for out-of-sync files and sync any missing remote files to local storage"""

    # Get the list of local and remote names of the specified media type
    # TODO: Could be a problem if we have multiple files with the same name (e.g. in different months)

    names = {'local': {}, 'remote': {}}

    for name in media_files['local']:
        names['local'][os.path.basename(name)] = name

    for name in media_files['remote']:
        names['remote'][os.path.basename(name)] = name

    # Find matches and remove them

    matching = 0
    for name in names['local']:
        if name in names['remote']:
            matching += 1

            del media_files['remote'][names['remote'][name]]
            del media_files['local'][names['local'][name]]

    if matching:
        colour.write(f'    [BOLD:{matching} {media} files are in sync]')
    else:
        colour.write(f'    [BOLD:No {media} files are in sync]')

    if media_files['local']:
        colour.write(f'    [BOLD:{len(media_files["local"])} local {media} files are out of sync]')
    else:
        colour.write(f'    [BOLD:No local {media} files are out of sync]')

    if media_files['remote']:
        colour.write(f'    [BOLD:{len(media_files["remote"])} remote {media} files are out of sync]')
        sync_media_local(dryrun, skip_no_day, media_files['remote'], local_dir)
    else:
        colour.write(f'    [BOLD:No remote {media} files are out of sync]')

    colour.write('')

################################################################################

# TODO: Tidy this up!
def remove_duplicates(media_files):
    """Look for remote files which have an original and multiple
       copies and remove the copies from the list of files to consider using the
       imagehash library to detect duplicate or near-duplicate files.
    """

    print('Checking for duplicate files')

    # Originals can have upper or lower case extensions, copies only tend to have lower
    # case, so build a lower case to original lookup table

    names = {name.lower():name for name in media_files}

    duplicates = defaultdict(list)

    # Build a list of duplicates for each filename in the list - i.e. files with the same
    # prefix and a suffix matching DUP_RE, indexed by the base filename (without the suffix)

    for entry in names:
        orig_match = DUP_RE.fullmatch(entry)
        if orig_match:
            original = orig_match.group(1) + orig_match.group(2)

            duplicates[original].append(entry)

    # Now use the imagehash library to check each list of maybe-duplicate files
    # to build a list of actual duplicates (or at least nearly-indistinguishable images)
    # TODO: Better to build list of all hashes, then find near-duplicates

    actual_duplicates = set()
    for entry, dupes in duplicates.items():
        # If the base file (no suffix) exists use that as the base, otherwise
        # use the first duplicate (we can have a situation where we have duplicates
        # and no original).

        hash_list = defaultdict(list)

        # Start with the base file, it it exists

        if entry in names:
            try:
                base_hash = str(imagehash.average_hash(Image.open(names[entry])))

                hash_list[base_hash].append(names[entry])
            except OSError:
                pass

        # Calculate the hash of each of the potential duplicates and if they
        # are close enough to the base hash, then add them to the real duplicate list

        for entry in dupes:
            filename = names[entry]
            try:
                dupe_hash = str(imagehash.average_hash(Image.open(filename)))

                hash_list[dupe_hash].append(filename)
            except OSError:
                colour.write(f'[BOLD:WARNING]: Unable to read {filename}')

        # Remove entries with identical hash values

        for dupes in hash_list:
            for dupe in hash_list[dupes][1:]:
                actual_duplicates.add(dupe)
            hash_list[dupes] = hash_list[dupes][0]

        # Look for adjaced entries in the sorted list of hash values that differ by less then the minimum
        # and remove the duplicates

        hash_values = sorted(hash_list.keys())
        logging.debug(f'Hash values for duplicates: {hash_values}')

        for i in range(len(hash_values)-1):
            if int(hash_values[i+1], 16) - int(hash_values[i], 16) < MIN_HASH_DIFF:
                actual_duplicates.add(hash_list[hash_values[i+1]])

    # Remove all the entries in the real duplicates list

    for entry in actual_duplicates:
        logging.info(f'Removing {os.path.basename(entry)} as a (near-)duplicate')
        del media_files[entry]

################################################################################

def gphoto_sync(args, year, month):
    """Synchronise a month's worth of photos"""

    colour.write('[GREEN:%s]' % '-'*80)
    colour.write(f'[BOLD:Reading files for {month:02}/{year}]')

    # List of directories to search for media associated with this month/year

    cache_dirs = [cache_directory(args, year, month)]
    local_dirs = [local_directory(args, 'photo', year, month)+'*',
                  local_directory(args, 'video', year, month)+'*']

    # Read the pictures and their EXIF data to get the dates

    media_files = {'photo': {}, 'video': {}}
    unknown_files = {}

    media_files['photo']['remote'], media_files['video']['remote'], unknown_files['remote'] = find_files(cache_dirs)
    media_files['photo']['local'], media_files['video']['local'], unknown_files['local'] = find_files(local_dirs)

    for media in ('photo', 'video'):
        remove_duplicates(media_files[media]['remote'])

    colour.write('[GREEN:%s]' % '-'*80)
    colour.write(f'[BOLD:Syncing files for {month:02}/{year}]')

    for media in ('photo', 'video'):
        media_sync(args.dryrun, args.skip_no_day, media, media_files[media], args.local_dir[media])

################################################################################

def clear_cache(cache_dir, keep, start):
    """Clear cache entries more than keep months before the start date"""

    start_name = (start - relativedelta(months=keep)).strftime(DATE_FORMAT)

    for year_dir in glob.glob(os.path.join(cache_dir, '*')):
        if os.path.isdir(year_dir):
            for month_dir in glob.glob(os.path.join(year_dir, '*')):
                if os.path.isdir(month_dir):
                    entry_date = os.path.basename(year_dir) + '-' + os.path.basename(month_dir)

                    if entry_date < start_name:
                        logging.info('Removing obsolete cache entry %s', month_dir)
                        shutil.rmtree(month_dir)

################################################################################

def main():
    """Entry point"""

    # Handle the command line

    args = parse_command_line()

    # Clear old entries from the cache

    if not args.no_update and not args.dryrun:
        clear_cache(args.cache, args.keep, args.start)

    # Update the cache

    for year in range(args.start.year, args.end.year+1):
        start_month = args.start.month if year == args.start.year else 1
        end_month = args.end.month if year == args.end.year else 12

        for month in range(start_month, end_month+1):
            update_cache(args, year, month)

    # Perform the sync

    for year in range(args.start.year, args.end.year+1):
        start_month = args.start.month if year == args.start.year else 1
        end_month = args.end.month if year == args.end.year else 12

        for month in range(start_month, end_month+1):
            gphoto_sync(args, year, month)

################################################################################

def gphotosync():
    """Entry point"""
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    gphotosync()
