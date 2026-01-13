import logging
import platform

import tkinter as tk
import ttkbootstrap as ttk

from ..image_comparator import ImageComparator
from ..util import Coordinates, Size
from .image_canvas import ImageCanvas
from .image_scaling import ImageScaling
from .zoom_menu import ZoomMenu

from ..util import separate_thread


log = logging.getLogger(__name__)


class ImageFrame(ttk.Frame):
    def __init__(
        self, parent, update_item=None, left_label='left', right_label='right'
    ):
        super().__init__(parent)
        self.update_item_command = update_item
        self.left_label = tk.StringVar(value=left_label)
        self.right_label = tk.StringVar(value=right_label)

        self.high_contrast = tk.BooleanVar()
        self.high_contrast.set(False)

        self.zoom_menu = ZoomMenu(self)
        self.button_zoom_100 = ttk.Radiobutton(
            self,
            text='1:1',
            variable=self.zoom_menu.mode_var,
            value='Original',
            command=self.zoom_original,
        )
        self.button_zoom_fit_if_larger = ttk.Radiobutton(
            self,
            text='Fit if larger',
            variable=self.zoom_menu.mode_var,
            value='FitIfLarger',
            command=self.zoom_fit_if_larger,
        )
        self.button_zoom_menu = ttk.Button(
            self, text='Zoom...', command=self.post_zoom_menu
        )
        self.button_high_contrast = ttk.Checkbutton(
            self,
            text='High constrast',
            variable=self.high_contrast,
            command=self.show_diff,
        )

        self.image_layout_style = tk.IntVar()
        self.image_layout_style.set(3)
        self.button_layout1 = ttk.Radiobutton(
            self,
            text='1',
            variable=self.image_layout_style,
            value=1,
            command=self.layout_images,
        )
        self.button_layout2 = ttk.Radiobutton(
            self,
            text='2',
            variable=self.image_layout_style,
            value=2,
            command=self.layout_images,
        )
        self.button_layout3 = ttk.Radiobutton(
            self,
            text='3',
            variable=self.image_layout_style,
            value=3,
            command=self.layout_images,
        )

        self.image_frame = ttk.Frame(self)
        self.canvases = {
            'left': ImageCanvas(self.image_frame, 'left'),
            'right': ImageCanvas(self.image_frame, 'right'),
            'diff': ImageCanvas(self.image_frame, 'diff'),
        }
        self.images = {
            'left': None,
            'right': None,
            'diff': None,
        }

        self.current_top_image = 'left'

        self.comparator = None
        self.button_zoom_fit_if_larger.invoke()

        self.operate_buttons = []

        self.layout()
        self.bind_events()

    def add_operate_buttons(self, *buttons):
        self.operate_buttons.extend(buttons)
        self.layout()

    def add_standard_operate_buttons(
        self, delete_fn=None, copy_left_fn=None, copy_right_fn=None
    ):
        self.left_text_label = ttk.Label(self, textvariable=self.left_label)
        self.right_text_label = ttk.Label(self, textvariable=self.right_label)
        self.add_operate_buttons(
            ttk.Button(self, text='Delete', bootstyle='danger',
                       command=delete_fn or self.delete),
            self.left_text_label,
            ttk.Button(self, text='⟵',
                       command=copy_right_fn or self.copy_right_to_left),
            ttk.Button(self, text='⟶',
                       command=copy_left_fn or self.copy_left_to_right),
            self.right_text_label,
        )

    def layout(self):
        buttons = (
            self.button_zoom_100,
            self.button_zoom_fit_if_larger,
            self.button_zoom_menu,
            self.button_high_contrast,
            self.button_layout1,
            self.button_layout2,
            self.button_layout3,
        )
        for col, button in enumerate(buttons):
            button.grid(column=col, row=0, padx=5, pady=5, sticky='w')

        for col, button in enumerate(self.operate_buttons):
            button.grid(column=len(buttons) + 1 + col, row=0, padx=5, pady=5, sticky='e')

        self.image_frame.grid(
            column=0,
            row=1,
            columnspan=len(buttons) + 1 + len(self.operate_buttons),
            sticky='nsew',
        )
        self.image_frame.rowconfigure(0, weight=1)

        self.layout_images()

        self.columnconfigure(len(buttons), weight=1)
        self.rowconfigure(1, weight=1)

    def layout_images(self):
        if platform.system() == 'Linux':
            mouse_wheel_seqs = ('<Button-4>', '<Button-5>', '<MouseWheel>',)
        else:
            mouse_wheel_seqs = ('<MouseWheel>',)

        n = self.image_layout_style.get()
        if n == 3:
            self.canvases['left'].grid(column=0, row=0, sticky='nsew')
            self.canvases['right'].grid(column=1, row=0, sticky='nsew')
            self.canvases['diff'].grid(column=2, row=0, sticky='nsew')

            self.image_frame.columnconfigure(0, weight=1)
            self.image_frame.columnconfigure(1, weight=1)
            self.image_frame.columnconfigure(2, weight=1)

            for seq in mouse_wheel_seqs:
                self.image_frame.unbind(seq)
                for canvas in self.canvases.values():
                    canvas.unbind(seq)

        elif n == 2:
            # Use single 'left' canvas for swapping left/right, plus diff canvas
            self.canvases['left'].grid(column=0, row=0, sticky='nsew')
            self.canvases['right'].grid_forget()
            self.canvases['diff'].grid(column=1, row=0, sticky='nsew')

            self.image_frame.columnconfigure(0, weight=1)
            self.image_frame.columnconfigure(1, weight=1)
            self.image_frame.columnconfigure(2, weight=0)

            if self.current_top_image not in ('left', 'right'):
                self.current_top_image = 'left'
            self.canvases['left'].swap_image(self.images[self.current_top_image])

            for seq in mouse_wheel_seqs:
                self.image_frame.bind(seq, self.on_mouse_wheel)
                for canvas in self.canvases.values():
                    canvas.bind(seq, self.on_mouse_wheel, add='+')

        else:
            assert n == 1
            # Use single 'left' canvas for swapping all three images
            self.canvases['left'].grid(column=0, row=0, sticky='nsew')
            self.canvases['right'].grid_forget()
            self.canvases['diff'].grid_forget()

            self.image_frame.columnconfigure(0, weight=1)
            self.image_frame.columnconfigure(1, weight=0)
            self.image_frame.columnconfigure(2, weight=0)

            self.canvases['left'].swap_image(self.images[self.current_top_image])

            for seq in mouse_wheel_seqs:
                self.image_frame.bind(seq, self.on_mouse_wheel)
                for canvas in self.canvases.values():
                    canvas.bind(seq, self.on_mouse_wheel, add='+')

    def bind_events(self):
        for key in self.canvases.keys():
            for otherkey in set(self.canvases.keys()) - {key}:
                self.canvases[key].bind(
                    '<Button1-Motion>', self.canvases[otherkey].on_motion, add='+'
                )
                self.canvases[key].bind(
                    '<ButtonRelease-1>', self.canvases[otherkey].on_left_up, add='+'
                )

    def on_mouse_wheel(self, evt):
        if evt.type == tk.EventType.MouseWheel:
            mouse_wheel_up = evt.delta > 0
        else:
            mouse_wheel_up = evt.num == 5

        n = self.image_layout_style.get()
        if n == 2:
            # Toggle between left and right
            if self.current_top_image == 'left':
                self.current_top_image = 'right'
            else:
                self.current_top_image = 'left'
        else:
            assert n == 1
            # Cycle through left -> right -> diff -> left (or reverse)
            cycle = ['left', 'right', 'diff']
            current_idx = cycle.index(self.current_top_image)
            if mouse_wheel_up:
                next_idx = (current_idx + 1) % 3
            else:
                next_idx = (current_idx - 1) % 3
            self.current_top_image = cycle[next_idx]

        self.canvases['left'].swap_image(self.images[self.current_top_image])

    def minsize(self):
        width = (
            self.button_zoom_100.winfo_width()
            + self.button_zoom_fit_if_larger.winfo_width()
            + self.button_zoom_menu.winfo_width()
            + self.button_high_contrast.winfo_width()
        )
        height = self.button_zoom_100.winfo_height()
        return Size((width + 400, height + 600))

    def zoom_original(self):
        self.zoom(ImageScaling.Mode.Original)

    def zoom_fit_if_larger(self):
        self.zoom(ImageScaling.Mode.Fit, factor=1, shrink=True, expand=False)

    def zoom(self, mode, factor=1, shrink=True, expand=True):
        for canvas in self.canvases.values():
            canvas.zoom(mode, factor=factor, shrink=shrink, expand=expand)

    def post_zoom_menu(self):
        pos = Coordinates(
            (self.button_zoom_menu.winfo_rootx(), self.button_zoom_menu.winfo_rooty())
        )
        pos.y += self.button_zoom_menu.winfo_height()
        self.zoom_menu.post(pos)

    def show_diff(self):
        if self.high_contrast.get():
            if self.comparator:
                self.images['diff'] = self.comparator.high_contrast_diff
                self.canvases['diff'].scaled_image = None
                self.canvases['diff'].load_image(self.images['diff'])
        else:
            if self.comparator:
                self.images['diff'] = self.comparator.diff
                self.canvases['diff'].scaled_image = None
                self.canvases['diff'].load_image(self.images['diff'])
        # In mode 1, if diff is currently shown on the left canvas, update it
        n = self.image_layout_style.get()
        if n == 1 and self.current_top_image == 'diff':
            self.canvases['left'].swap_image(self.images[self.current_top_image])

    @separate_thread
    def load_comparator(self, comparator):
        self.comparator = comparator
        self.images['left'] = self.comparator.left
        self.images['right'] = self.comparator.right
        self.show_diff()
        # In modes 1 and 2, update the displayed image on the left canvas
        n = self.image_layout_style.get()
        if n in (1, 2):
            self.canvases['left'].swap_image(self.images[self.current_top_image])
        else:
            for loc in ('left', 'right', 'diff'):
                self.canvases[loc].load_image(self.images[loc])

    def load_images(self, left, right):
        comparator = ImageComparator(left, right)
        self.load_comparator(comparator)

    def clear(self):
        for canvas in self.canvases.values():
            self.after_idle(canvas.clear)

    def delete(self):
        if self.comparator:
            left_file, right_file = (
                self.comparator.left_file,
                self.comparator.right_file,
            )
            log.info(f'DELETE: {left_file} {right_file}')
            self.comparator.delete_files()
            self.comparator = None
            self.clear()
            if self.update_item_command:
                self.update_item_command(left_file, self.comparator)

    def copy_left_to_right(self):
        if self.comparator:
            left_file, right_file = (
                self.comparator.left_file,
                self.comparator.right_file,
            )
            log.info(f'COPY: {left_file} -> {right_file}')
            self.comparator.copy_left_to_right()
            if self.comparator.right:
                self.images['right'] = self.comparator.right
                if self.high_contrast:
                    self.images['diff'] = self.comparator.high_contrast_diff
                else:
                    self.images['diff'] = self.comparator.diff
                self.canvases['right'].load_image(self.images['right'])
                self.canvases['diff'].load_image(self.images['diff'])
                # In modes 1 and 2, update the displayed image on the left canvas
                n = self.image_layout_style.get()
                if n in (1, 2) and self.current_top_image in ('right', 'diff'):
                    self.canvases['left'].swap_image(self.images[self.current_top_image])
                else:
                    for loc in ('right', 'diff'):
                        self.canvases[loc].swap_image(self.images[loc])
            if self.update_item_command:
                self.update_item_command(right_file, self.comparator)

    def copy_right_to_left(self):
        if self.comparator:
            left_file, right_file = (
                self.comparator.left_file,
                self.comparator.right_file,
            )
            log.info(f'COPY: {right_file} -> {left_file}')
            self.comparator.copy_right_to_left()
            if self.comparator.left:
                self.images['left'] = self.comparator.left
                if self.high_contrast:
                    self.images['diff'] = self.comparator.high_contrast_diff
                else:
                    self.images['diff'] = self.comparator.diff
                self.canvases['diff'].load_image(self.comparator.diff)
                # In modes 1 and 2, update the displayed image on the left canvas
                n = self.image_layout_style.get()
                if n in (1, 2) and self.current_top_image in ('left', 'diff'):
                    self.canvases['left'].swap_image(self.images[self.current_top_image])
                else:
                    for loc in ('left', 'diff'):
                        self.canvases[loc].swap_image(self.images[loc])
            if self.update_item_command:
                self.update_item_command(left_file, self.comparator)
