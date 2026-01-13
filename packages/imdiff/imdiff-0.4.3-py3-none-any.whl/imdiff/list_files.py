import os
import pathlib

from PIL import Image

from .image_comparator import ImageComparator


# Get list of image file extensions from PIL
IMAGE_EXTENTIONS = {ex.lower() for ex, f in Image.registered_extensions().items() if f in Image.OPEN}
IMAGE_EXTENTIONS |= {'.bmp', '.png', '.jpg', '.ps', '.eps', '.cps', '.tif', '.tiff'}


def is_image(file_path):
    return file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENTIONS


def list_files(left_topdir, right_topdir, subdir=pathlib.Path('.')):
    if not (left_topdir.is_dir() and right_topdir.is_dir()):
        return
    def _scan_dir(p):
        dirs, files = set(), set()
        try:
            with os.scandir(p) as it:
                for entry in it:
                    name = entry.name
                    if name.startswith('.'):
                        # skip hidden files
                        continue
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            dirs.add(name)
                        elif entry.is_file(follow_symlinks=False):
                            files.add(name)
                    except OSError:
                        # Ignore entries that cannot be accessed
                        continue
        except FileNotFoundError:
            pass
        return dirs, files

    stack = [pathlib.Path(subdir)]
    while stack:
        rel = stack.pop()
        leftdir = left_topdir / rel
        rightdir = right_topdir / rel

        left_dirs, left_files = _scan_dir(leftdir) if leftdir.is_dir() else (set(), set())
        right_dirs, right_files = _scan_dir(rightdir) if rightdir.is_dir() else (set(), set())

        files = left_files | right_files
        for fname in sorted(files):
            yield str(rel / fname), leftdir / fname, rightdir / fname

        subdirs = left_dirs | right_dirs
        # Push in reverse-sorted order to process in ascending order (depth-first)
        for dname in sorted(subdirs, reverse=True):
            stack.append(rel / dname)


def list_image_files(left_topdir, right_topdir, subdir=pathlib.Path('.')):
    for subpath, left, right in list_files(left_topdir, right_topdir, subdir):
        if is_image(left) or is_image(right):
            yield subpath, ImageComparator(left, right)
