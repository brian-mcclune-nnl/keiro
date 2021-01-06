"""A simple channel splitter script for cached conda packages.

"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys

from typing import List


def get_parser() -> argparse.ArgumentParser:
    """Gets a parser object for chuukaibutsu.

    Returns:
        The parser object.
    """

    parser = argparse.ArgumentParser(
        description='splits packages into channels.',
    )
    parser.add_argument(
        'pkgs_dirs',
        nargs='+',
        help='directory containing packages and urls.txt',
    )
    parser.add_argument(
        '-p',
        '--prefix',
        default=pathlib.Path.cwd().joinpath('local'),
        help='prefix for channels directories',
    )
    parser.add_argument(
        '-i',
        '--index',
        action='store_true',
        help='index the channels after distributing packages',
    )
    return parser


def distribute(
    pkgs_dirs: List[str],
    prefix: str,
    index: bool,
):
    """Distributes `pkgs_dirs` to channels in `prefix`.

    Optionally indexes channels once distribution is complete.

    Args:
        pkgs_dirs: The directories containing conda packages and urls files.
        prefix: The prefix to use when creating channel directories.
        index: ``True`` if channels should be indexed.
    """

    # Track channels directories as they are created
    channels = set()

    # Process all input packages directories
    for pkgs_dir in pkgs_dirs:
        pkgs_path = pathlib.Path(pkgs_dir)

        # Read the package directory urls.txt file
        urls = open(pkgs_path.joinpath('urls.txt')).read()
        for pkg in pathlib.Path(pkgs_dir).iterdir():
            if pkg.is_dir() or pkg.name in ('urls', 'urls.txt'):
                continue

            # Determine the channel and subdir for the pkg
            match = re.search(
                rf'^.*?/([\w\-]+)/([\w\-]+)/{pkg.name}$',
                urls,
                re.M,
            )
            if match is None:
                raise ValueError(f'{pkg.name} not found in urls.txt!')
            channel, subdir = match.groups()

            # Relocate the package, creating the path if necessary
            location = pathlib.Path(prefix).joinpath(channel, subdir)
            channels.add(location.parent)
            location.mkdir(parents=True, exist_ok=True)
            print(f'Copying {pkg.name} to {location}')
            shutil.copy(pkg, location)

    # Conditionally index channels
    if index:
        for channel in channels:
            subprocess.run(['conda', 'index', channel])


def main(argv: List[str] = sys.argv[1:]):
    """Runs chuukaibutsu.

    Args:
        argv: The arguments to main, defaulting to command line arguments.
    """

    # Parse arguments
    args = get_parser().parse_args(argv)

    # Distribute packages
    distribute(args.pkgs_dirs, args.prefix, args.index)


if __name__ == '__main__':
    main()
