import difflib

from ..list_files import is_image, list_files
from ..image_comparator import ImageComparator
from ..gui import DirDiffMainWindow


def app(leftdir=None, rightdir=None):
    win = DirDiffMainWindow()
    win.load(leftdir, rightdir)
    win.mainloop()


def print_diff(leftdir=None, rightdir=None):
    ndiffs = 0
    assert leftdir.is_dir() and rightdir.is_dir(), 'Items must both be directories'

    rmse_threshold = 0.02

    for subpath, left, right in list_files(leftdir, rightdir):
        if not left.is_file():
            ndiffs += 1
            print(f'Only in {right.parent}: {subpath}')
        elif not right.is_file():
            ndiffs += 1
            print(f'Only in {left.parent}: {subpath}')
        elif is_image(left) and is_image(right):
            icmp = ImageComparator(left, right)
            if icmp.diff_info != 'identical':
                if isinstance(icmp.diff_info, str):
                    ndiffs += 1
                    print(f'{icmp.diff_info} (as image): {subpath}')
                elif icmp.diff_info > rmse_threshold:
                    ndiffs += 1
                    print(f'image difference NRMSE {icmp.diff_info:.4f}: {subpath}')
        else:
            diff_output = list(difflib.unified_diff(
                left.read_text().splitlines(),
                right.read_text().splitlines(),
                fromfile=str(left),
                tofile=str(right),
                lineterm=''))
            if diff_output:
                ndiffs += 1
                print('\n'.join(diff_output))
    return ndiffs
