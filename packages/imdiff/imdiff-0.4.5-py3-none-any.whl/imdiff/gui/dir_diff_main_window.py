import logging
import os
import platform
import sys

import tkinter as tk
import ttkbootstrap as ttk

from .file_list_frame import FileListFrame
from .image_frame import ImageFrame
from .status_bar import StatusBar


log = logging.getLogger(__name__)


class DirDiffMainWindow(ttk.Window):
    def __init__(self, left_label='left', right_label='right'):
        super().__init__(title='Image Comparator', themename='sandstone')
        self.pane_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=8)
        self.file_list_frame = FileListFrame(
            self.pane_window,
            on_select=self.on_select,
            left_label=left_label,
            right_label=right_label,
        )
        self.image_frame = ImageFrame(self.pane_window, update_item=self.update_item)
        self.image_frame.add_standard_operate_buttons(
            self.delete,
            self.copy_left_to_right,
            self.copy_right_to_left,
        )
        self.status_bar = StatusBar(self)
        self.layout()
        self.bind_events()

    def layout(self):
        self.pane_window.add(self.file_list_frame)
        self.pane_window.add(self.image_frame)
        self.pane_window.grid(column=0, row=0, sticky='nsew')
        self.status_bar.grid(column=0, row=1, sticky='sew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        file_list_frame_minsize = self.file_list_frame.minsize()
        image_frame_minsize = self.image_frame.minsize()

        self.pane_window.paneconfigure(
            self.file_list_frame, minsize=file_list_frame_minsize.width
        )

        w = file_list_frame_minsize.width + image_frame_minsize.width
        h = max(file_list_frame_minsize.height, image_frame_minsize.height)
        self.minsize(w, h)

    def bind_events(self):
        self.bind_all('<Control-q>', self.destroy)
        self.bind_all('<Down>', self.file_list_frame.on_down)
        self.bind_all(
            '<Shift-Down>', lambda evt: self.file_list_frame.on_down(evt, add=True)
        )
        self.bind_all('<Up>', self.file_list_frame.on_up)
        self.bind_all(
            '<Shift-Up>', lambda evt: self.file_list_frame.on_up(evt, add=True)
        )
        self.bind_all('<Control-Delete>', self.delete)
        self.bind_all('<Control-Left>', self.copy_right_to_left)
        self.bind_all('<Control-Right>', self.copy_left_to_right)

    def destroy(self, *evt):
        self.file_list_frame.signal_shutdown()
        super().destroy()
        sys.exit()

    def on_select(self, comparator):
        self.after_idle(self.image_frame.clear)
        self.after_idle(self.status_bar.clear)
        self.update_idletasks()
        if comparator:
            self.after_idle(self.image_frame.load_comparator, comparator)
            self.after_idle(self.status_bar.update_labels, comparator)

    def update_item(self, file_path, comparator):
        self.after_idle(self.file_list_frame.update_file_item, file_path)
        self.after_idle(self.status_bar.update_labels, comparator)

    def load(self, leftdir=None, rightdir=None):
        self.file_list_frame.leftdir = leftdir
        self.file_list_frame.rightdir = rightdir
        if leftdir and rightdir:
            # find first unique path component starting from the end
            for i in range(len(leftdir.parts)):
                try:
                    l = leftdir.parts[-i]
                    r = rightdir.parts[-i]
                    if l != r:
                        self.image_frame.left_label.set(l)
                        self.image_frame.right_label.set(r)
                        break
                except IndexError:
                    # just give up, defaults to "left" and "right"
                    break


            self.file_list_frame.after_idle(self.file_list_frame.load_files)

    def delete(self, evt=None):
        for file_path in self.file_list_frame.file_treeview.selection():
            self.file_list_frame.delete(file_path)

    def copy_left_to_right(self, evt=None):
        for file_path in self.file_list_frame.file_treeview.selection():
            if comparator := self.file_list_frame.files.get(file_path, None):
                if comparator is self.image_frame.comparator:
                    self.image_frame.copy_left_to_right()
                else:
                    left_file, right_file = comparator.left_file, comparator.right_file
                    log.info(f'COPY: {left_file} -> {right_file}')
                    comparator.copy_left_to_right()
                    self.update_item(file_path, comparator)

    def copy_right_to_left(self, evt=None):
        for file_path in self.file_list_frame.file_treeview.selection():
            if comparator := self.file_list_frame.files.get(file_path, None):
                if comparator is self.image_frame.comparator:
                    self.image_frame.copy_right_to_left()
                else:
                    left_file, right_file = comparator.left_file, comparator.right_file
                    log.info(f'COPY: {right_file} -> {left_file}')
                    comparator.copy_right_to_left()
                    self.update_item(file_path, comparator)
