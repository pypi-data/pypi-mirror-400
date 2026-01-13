#! /usr/bin/env python3

################################################################################
""" Thingy docker-purge command

    Copyright (C) 2017 John Skilleter

    Initial version - contains only basic error checking and limited debug output.
"""
################################################################################

import sys
import re
import argparse
import logging

from skilleter_modules import docker

################################################################################

def initialise():
    """ Parse the command line """

    parser = argparse.ArgumentParser(description='Purge docker instances and images')

    parser.add_argument('-s', '--stop', action='store_true', help='Stop Docker instances')
    parser.add_argument('-k', '--kill', action='store_true', help='Kill Docker instances')
    parser.add_argument('-r', '--remove', action='store_true', help='Remove Docker images')
    parser.add_argument('-l', '--list', action='store_true', help='List what would be done without doing it')
    parser.add_argument('-f', '--force', action='store_true', help='Forcibly kill/remove instances')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('images', nargs='*', help='List of Docker containers (regular expression)')

    args = parser.parse_args()

    # Configure logging

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.info('Debug logging enabled')

    # Default is to stop matching images

    if not args.stop and not args.kill and not args.remove:
        args.stop = True

    # Default is to match all containers

    if not args.images:
        args.images = '.*'
    else:
        args.images = '|'.join(args.images)

    logging.info('Arguments: %s', args)
    return args

################################################################################

def main(args):
    """ Main code """

    try:
        if args.stop or args.kill:
            for instance in docker.instances():
                if re.match(args.images, instance):

                    print(f'Stopping instance: {instance}')

                    if not args.list:
                        docker.stop(instance, force=args.force)

        if args.kill:
            for instance in docker.instances(all=True):
                if re.match(args.images, instance):

                    print(f'Removing instance: {instance}')

                    if not args.list:
                        docker.rm(instance)

        if args.remove:
            for image in docker.images():
                if re.match(args.images, image):

                    print(f'Removing image: {image}')

                    if not args.list:
                        docker.rmi(image, force=args.force)

    except docker.DockerError as exc:
        sys.stderr.write(str(exc))
        sys.exit(1)

################################################################################

def docker_purge():
    """Entry point"""

    try:
        config = initialise()
        main(config)

    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    docker_purge()
