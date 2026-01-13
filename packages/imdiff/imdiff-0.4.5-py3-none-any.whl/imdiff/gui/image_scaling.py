import enum

from ..util import Size


class ImageScaling:
    class Mode(enum.Enum):
        Original = 0
        Scaled = 1
        Fit = 2
        Fill = 3

    def __init__(self):
        self._mode = ImageScaling.Mode.Original
        self._shrink_if_larger = True
        self._expand_if_smaller = False
        self._scaling_factor = 1.0

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = ImageScaling.Mode(mode)

    @property
    def shrink_if_larger(self):
        return self._shrink_if_larger

    @shrink_if_larger.setter
    def shrink_if_larger(self, value):
        self._shrink_if_larger = bool(value)

    @property
    def expand_if_smaller(self):
        return self._expand_if_smaller

    @expand_if_smaller.setter
    def expand_if_smaller(self, value):
        self._expand_if_smaller = bool(value)

    @property
    def scaling_factor(self):
        return self._scaling_factor

    @scaling_factor.setter
    def scaling_factor(self, value):
        self._scaling_factor = max(0.0, float(value))

    @property
    def is_fixed_size(self):
        return self._mode in {ImageScaling.Mode.Original, ImageScaling.Mode.Scaled}

    @property
    def is_original_size(self):
        return (
            self._mode == ImageScaling.Mode.Original
            or not (self._expand_if_smaller or self._shrink_if_larger)
            or (self._mode == ImageScaling.Mode.Scaled and self._scaling_factor == 1.0)
        )

    def scaled(self, original, frame):
        if self.mode == ImageScaling.Mode.Original:
            return original
        else:
            w, h = original
            fw, fh = frame
            is_larger = (w > fw) or (h > fh)
            if (is_larger and self.shrink_if_larger) or (
                not is_larger and self.expand_if_smaller
            ):
                if self.mode == ImageScaling.Mode.Scaled:
                    f = self.scaling_factor
                    return Size((int(f * w), int(f * h)))
                else:
                    assert self.mode in {ImageScaling.Mode.Fit, ImageScaling.Mode.Fill}
                    hr = fh / h
                    wr = fw / w
                    frame_is_narrower = (wr / hr) < 1.0
                    if (frame_is_narrower and self.mode == ImageScaling.Mode.Fit) or (
                        not frame_is_narrower and self.mode == ImageScaling.Mode.Fill
                    ):
                        return Size((fw, int(h * wr)))
                    else:
                        return Size((int(w * hr), fh))
            else:
                return original
