# Thingy

Licence: GPL v3

Author: John Skilleter v0.99

Collection of shell utilities and configuration stuff for Linux and MacOS. Untested on other operating systems.

Permanently (for the forseeable future!) in a beta stage - usable, with a few rough edges, and probably with bugs when used in way I'm not expecting!

The following commands are documented in detail in the help output that can be displayed by running the command with the '--help' option.

This README just contains a summary of the functionality of each command.

# General Commands

## borger

Wrapper for the borg backup utility to make it easier to use with a fixed set of options.

## console-colours

Display all available colours in the console.

## diskspacecheck

Check how much free space is available on all filesystems, ignoring read-only filesystems, /dev and tmpfs.

Issue a warning if any are above 90% used.

## docker-purge

Stop or kill docker instances and/or remove docker images.

### gphotosync

Utility for syncing photos from Google Photos to local storage

## moviemover

Search for files matching a wildcard in a directory tree and move them to an equivalent location in a different tree

## phototidier

Perform various tidying operations on a directory full of photos:

* Remove leading '$' and '_' from filenames
* Move files in hidden directories up 1 level
* If the EXIF data in a photo indicates that it was taken on date that doesn't match the name of the directory it is stored in (in YYYY-MM-DD format) then it is moved to the correct directory, creating it if necessary.

All move/rename operations are carried out safely with the file being moved having
a numeric suffix added to the name if it conflicts with an existing file.

## photodupe

## splitpics

Copy a directory full of pictures to a destination, creating subdiretories with a fixed number of pictures in each in the destination directory for use with FAT filesystems and digital photo frames.

## strreplace

Simple search and replace utility for those times when trying to escape characters in a regexp to use sed is more hassle than it is worth.

  strreplace [-h] [--inplace] search replace [infile] [outfile]

  positional arguments:
    search         Search text
    replace        Replacment text
    infile         Input file
    outfile        Output file

  options:
    -h, --help     show this help message and exit
    --inplace, -i  Do an in-place search and replace on the input file

## window-rename
