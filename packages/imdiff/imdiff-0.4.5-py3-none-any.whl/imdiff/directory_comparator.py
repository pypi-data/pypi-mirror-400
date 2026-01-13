import collections
import difflib
import filecmp
import pathlib

from .list_files import is_image, list_files
from .image_comparator import ImageComparator

def dir_diff(leftdir, rightdir):
    leftdir = pathlib.Path(leftdir)
    rightdir = pathlib.Path(rightdir)
    if not leftdir.is_dir():
        raise FileNotFoundError(leftdir)
    if not rightdir.is_dir():
        raise FileNotFoundError(rightdir)

    rmse_threshold = 0.02

    dinfo = collections.defaultdict(list)
    for subpath, left, right in list_files(leftdir, rightdir):
        if not left.is_file():
            dinfo['missing'].append(subpath)
        elif not right.is_file():
            dinfo['new'].append(subpath)
        elif filecmp.cmp(left, right, shallow=False):
            dinfo['identical'].append(subpath)
        elif is_image(left) and is_image(right):
            icmp = ImageComparator(left, right)
            if isinstance(icmp.diff_info, str):
                dinfo[icmp.diff_info].append(subpath)
            else:
                assert isinstance(icmp.diff_info, float)
                if icmp.diff_info > rmse_threshold:
                    dinfo['different'].append(subpath)
                else:
                    dinfo['similar'].append(subpath)
        else:
            try:
                diff_output = list(difflib.unified_diff(
                    left.read_text().splitlines(),
                    right.read_text().splitlines(),
                    fromfile=str(left),
                    tofile=str(right),
                    lineterm=''))
                if diff_output:
                    dinfo['different'].append(subpath)
                else:
                    dinfo['identical'].append(subpath)
            except UnicodeDecodeError:
                dinfo['different'].append(subpath)


    return dinfo
