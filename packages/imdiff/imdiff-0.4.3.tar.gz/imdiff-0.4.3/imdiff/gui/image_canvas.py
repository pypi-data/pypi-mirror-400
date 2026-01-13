import logging

import tkinter as tk

from PIL import Image, ImageTk

from ..util import Coordinates, Size
from .image_scaling import ImageScaling

log = logging.getLogger(__name__)


class ImageCanvas(tk.Canvas):
    def __init__(self, parent, label, border=5):
        super().__init__(parent)
        self.label = label
        self.border = border
        self.image = None
        self.scaling = ImageScaling()
        self.scaling_percent = None
        self.scaled_image = None
        self.image_id = None
        self.position = None
        self.is_draggable = False
        self.dragging_initial_position = None
        self.bind_events()

    def bind_events(self):
        self.bind('<Configure>', self.on_resize)
        self.bind('<Button1-Motion>', self.on_motion)
        self.bind('<ButtonRelease-1>', self.on_left_up)

    def on_resize(self, evt):
        log.debug(f'[{self.label}] on resize')
        self.update_image()

    def on_motion(self, evt):
        log.debug(f'[{self.label}] on motion')
        if self.image_id and self.is_draggable:
            cursor_pos = Coordinates((evt.x, evt.y))
            if self.dragging_initial_position is None:
                image_pos = Coordinates(self.coords(self.image_id))
                self.dragging_initial_position = image_pos - cursor_pos
            else:
                self.position = self.dragging_initial_position + cursor_pos
                self.after_idle(self.update_layout)

    def on_left_up(self, evt):
        log.debug(f'[{self.label}] on left up')
        self.dragging_initial_position = None

    def clear(self):
        self.delete('all')
        self.image_id = None
        self.scaled_image = None
        self.image = None

    def load_image(self, image):
        log.debug(f'[{self.label}] load image (setting to {image})')
        self.clear()
        self.image = image
        self.after_idle(self.update_image)

    def swap_image(self, image):
        """Swap displayed image without clearing canvas, to avoid flicker."""
        log.debug(f'[{self.label}] swap image (setting to {image})')
        if image is None:
            self.clear()
            return
        self.image = image
        # Reset scaled image to force recalculation
        self.scaled_image = None
        # Synchronously update display
        self.update_scaled_image()
        # Create PhotoImage before modifying canvas
        if self.scaled_image:
            new_tkimage = ImageTk.PhotoImage(self.scaled_image)
            if self.image_id:
                # Update existing canvas item - this is atomic and won't flicker
                self.itemconfig(self.image_id, image=new_tkimage)
            else:
                self.image_id = self.create_image(
                    self.border, self.border, image=new_tkimage, anchor='nw'
                )
            # Keep reference to prevent garbage collection
            self.tkimage = new_tkimage
            self.update_layout()

    def update_scaled_image(self):
        log.debug(f'[{self.label}] update scaled image (image: {self.image})')
        self.scaled_image_updated = False
        if self.image:
            if self.scaling.is_original_size and self.scaled_image != self.image:
                self.scaled_image = self.image
                self.scaling_percent = 100
                log.debug(f'[{self.label}] scale to original size')
                self.scaled_image_updated = True
            else:
                image_size = Size((self.image.width, self.image.height))
                canvas_size = Size((self.winfo_width(), self.winfo_height()))
                border_size = Size((2 * self.border, 2 * self.border))
                scaled_size = self.scaling.scaled(
                    image_size, canvas_size - border_size
                )
                if scaled_size.width > 0 and scaled_size.height > 0:
                    if self.scaled_image is None or scaled_size != Size(
                        (self.scaled_image.width, self.scaled_image.height)
                    ):
                        self.scaling_percent = int(
                            100 * scaled_size.width / image_size.width
                        )
                        self.scaled_image = self.image.resize(scaled_size)
                        log.debug(f'[{self.label}] scale to {self.scaling_percent}%')
                        self.scaled_image_updated = True
                else:
                    log.debug(f'[{self.label}] canvas size: {canvas_size}')
        else:
            self.clear()
            log.debug(f'[{self.label}] removed scaled image')

    def update_displayed_image(self):
        log.debug(
            f'[{self.label}] update displayed image (scaled image: {self.scaled_image}'
        )
        if self.image:
            if self.scaled_image and self.scaled_image_updated:
                self.tkimage = ImageTk.PhotoImage(self.scaled_image)
                if self.image_id:
                    self.itemconfig(self.image_id, image=self.tkimage)
                    log.debug(f'[{self.label}] updated displayed image')
                else:
                    self.image_id = self.create_image(
                        self.border, self.border, image=self.tkimage, anchor='nw'
                    )
                    log.debug(f'[{self.label}] displaying new image')
        else:
            self.clear()
            log.debug(f'[{self.label}] removed scaled image')

    def update_layout(self):
        log.debug(
            f'[{self.label}] update layout (image id: {self.image_id} scaled image: {self.scaled_image})'
        )
        if self.image_id and self.scaled_image:
            w = self.winfo_width()
            h = self.winfo_height()
            iw = self.scaled_image.width
            ih = self.scaled_image.height
            self.is_draggable = (w < iw) or (h < ih)
            if self.position is None:
                self.position = Coordinates(self.coords(self.image_id))
            self.position.x = (
                min(max(self.position.x, w - iw - self.border), self.border)
                if (w < iw)
                else ((w - iw) // 2)
            )
            self.position.y = (
                min(max(self.position.y, h - ih - self.border), self.border)
                if (h < ih)
                else ((h - ih) // 2)
            )
            if self.position != Coordinates(self.coords(self.image_id)):
                log.debug(f'[{self.label}] move to {self.position}')
                self.moveto(self.image_id, self.position.x, self.position.y)

    def update_image(self):
        log.debug(f'[{self.label}] update image {self.position}')
        self.after_idle(self.update_scaled_image)
        self.after_idle(self.update_displayed_image)
        self.after_idle(self.update_layout)

    def zoom(self, mode, factor=1, shrink=True, expand=True, pos=None):
        log.debug(f'[{self.label}] zoom {mode} {factor} {shrink} {expand} {pos}')
        if not (shrink or expand):
            mode = ImageScaling.Mode.Original
        self.scaling.mode = mode
        self.scaling.scaling_factor = factor
        self.scaling.shrink_if_larger = shrink
        self.scaling.expand_if_smaller = expand
        if pos is not None:
            self.position = pos
        self.update_image()

    def raise_to_front(self):
        self.tk.call('raise', self)
