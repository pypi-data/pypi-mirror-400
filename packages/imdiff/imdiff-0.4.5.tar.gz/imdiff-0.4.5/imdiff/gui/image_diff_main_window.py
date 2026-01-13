import logging
import os
import platform
import sys

import tkinter as tk
import ttkbootstrap as ttk

from .image_frame import ImageFrame
from .status_bar import StatusBar


log = logging.getLogger(__name__)


class ImageDiffMainWindow(tk.Tk):
    def __init__(self, left_label='left', right_label='right'):
        super().__init__()
        self.title('Image Comparator')
        self.image_frame = ImageFrame(self)
        self.image_frame.add_standard_operate_buttons()
        self.status_bar = StatusBar(self)
        self.layout()
        self.bind_events()

    def layout(self):
        self.image_frame.grid(column=0, row=0, sticky='nsew')
        self.status_bar.grid(column=0, row=1,  sticky='sew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.wait_visibility()

        image_frame_minsize = self.image_frame.minsize()
        w = image_frame_minsize.width
        h = image_frame_minsize.height
        self.minsize(w, h)

    def bind_events(self):
        self.bind_all('<Control-q>', self.destroy)
        self.bind_all('<Control-c>', self.destroy)
        self.bind_all('<Escape>', self.destroy)
        self.bind_all('<Control-Delete>', self.image_frame.delete)
        self.bind_all('<Control-Left>', self.image_frame.copy_left_to_right)
        self.bind_all('<Control-Right>', self.image_frame.copy_right_to_left)

    def destroy(self, *evt):
        super().destroy()
        sys.exit()

    def load(self, left=None, right=None):
        self.image_frame.load_images(left, right)
        if comp := self.image_frame.comparator:
            self.after_idle(self.status_bar.update_labels, comp)
