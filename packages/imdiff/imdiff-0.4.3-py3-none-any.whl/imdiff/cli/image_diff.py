import difflib

from ..list_files import is_image
from ..image_comparator import ImageComparator
from ..gui import ImageDiffMainWindow


def app(left=None, right=None):
    win = ImageDiffMainWindow()
    win.load(left, right)
    win.mainloop()


def print_diff(left, right):
    ndiffs = 0
    assert left.is_file() and right.is_file(), 'Items must both be files'

    rmse_threshold = 0.02
    if is_image(left) and is_image(right):
        icmp = ImageComparator(left, right)
        if icmp.diff_info != 'identical':
            ndiffs += 1
            if icmp.diff_info == 'missing':
                print(f'Only in {left.parent}: {left.name}')
            elif icmp.diff_info == 'new':
                print(f'Only in {right.parent}: {right.name}')
            elif isinstance(icmp.diff_info, str):
                print(f'Images {left} and {right} differ ({icmp.diff_info})')
            elif icmp.diff_info > rmse_threshold:
                print(f'Images {left} and {right} differ NRMSE: {icmp.diff_info}')
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
