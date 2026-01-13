import argparse
import pathlib

from ..version import __version__
from . import dir_diff, image_diff

def parse_args():
    parser = argparse.ArgumentParser(
        prog='imdiff',
        description="""Compare images one by one or directory by directory""",
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help="""Print diff result and exit. Disables the GUI. Exits with non-zero if
                there are differences.""",
    )
    parser.add_argument(
        'left',
        default='.',
        type=pathlib.Path,
        help="""Image or directory of images to compare.""",
    )
    parser.add_argument(
        'right',
        default='.',
        type=pathlib.Path,
        help="""Image or directory of images to compare.""",
    )
    args = parser.parse_args()
    return args

def main():
    #logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    if args.left.is_dir():
        assert args.right.is_dir(), \
            'Paths must be either both image files or both directories'
        if args.summary:
            ndiffs = dir_diff.print_diff(args.left, args.right)
            return int(ndiffs > 0)
        else:
            dir_diff.app(args.left, args.right)
    elif args.left.is_file():
        assert args.right.is_file(), \
            'Paths must be either both image files or both directories'
        if args.summary:
            ndiffs = image_diff.print_diff(args.left, args.right)
            return int(ndiffs > 0)
        else:
            image_diff.app(args.left, args.right)
    else:
        raise OSError(f'{args.left} is not a file or directory')
