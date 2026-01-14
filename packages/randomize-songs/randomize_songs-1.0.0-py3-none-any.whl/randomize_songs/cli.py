from argparse import ArgumentParser
from pathlib import Path

from randomize_songs import __version__
from randomize_songs.main import run


def get_argparser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Randomize songs in a directory into multiple directories.",
        prog="randomize-songs",
    )

    parser.set_defaults(func=run)

    # optional
    parser.add_argument(
        "-n",
        default=255,
        dest="files_portion_size",
        metavar="Max number of files in each output directory",
        type=int,
    )

    # positional
    parser.add_argument(
        dest="source_dir_path",
        metavar="Source directory path",
        type=Path,
    )

    return parser
