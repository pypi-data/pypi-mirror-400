import tkinter as tk
import ttkbootstrap as ttk

from .image_scaling import ImageScaling
from .transient_menu import TransientMenu


class ZoomMenu(TransientMenu):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mode_var = tk.StringVar()
        self.mode_var.set('Original')
        self.scale_var = tk.IntVar()
        self.scale_var.set(100)

        self.radio_button_scaled = ttk.Radiobutton(
            value='Scaled', variable=self.mode_var
        )

        self.add_radiobutton(
            text='Fit to window',
            value='Fit',
            variable=self.mode_var,
            command=self.on_mode_change,
        )
        self.add_radiobutton(
            text='Fill window',
            value='Fill',
            variable=self.mode_var,
            command=self.on_mode_change,
        )
        self.add_spacer()
        self.add_radiobutton(
            text='50%', value='50', variable=self.mode_var, command=self.on_mode_change
        )
        self.add_radiobutton(
            text='100%',
            value='Original',
            variable=self.mode_var,
            command=self.on_mode_change,
        )
        self.add_radiobutton(
            text='200%',
            value='200',
            variable=self.mode_var,
            command=self.on_mode_change,
        )
        self.add_radiobutton(
            text='300%',
            value='300',
            variable=self.mode_var,
            command=self.on_mode_change,
        )
        self.add_spacer()
        self.add_scale(
            length=100,
            from_=30,
            to=300,
            variable=self.scale_var,
            command=self.on_scale_change,
        )

    def post(self, pos):
        scaling = self.parent.images['left'].scaling
        scaling_percent = self.parent.images['left'].scaling_percent
        self.mode_var.set('FitIfLarger')
        if scaling.mode == ImageScaling.Mode.Original:
            self.mode_var.set('Original')
            self.scale_var.set(100)
        elif scaling.mode == ImageScaling.Mode.Fit:
            if scaling.shrink_if_larger and scaling.expand_if_smaller:
                self.mode_var.set('Fit')
        elif scaling.mode == ImageScaling.Mode.Fill:
            if scaling.shrink_if_larger and scaling.expand_if_smaller:
                self.mode_var.set('Fill')
        else:
            assert scaling.mode == ImageScaling.Mode.Scaled
            self.mode_var.set('Scaled')
        if scaling_percent == 50:
            self.mode_var.set('50')
        if scaling_percent == 200:
            self.mode_var.set('200')
        if scaling_percent == 300:
            self.mode_var.set('300')
        self.scale_var.set(scaling_percent)
        super().post(pos)

    def on_mode_change(self):
        value = self.mode_var.get()
        if value == 'Fit':
            self.parent.zoom(ImageScaling.Mode.Fit, shrink=True, expand=True)
            self.after_idle(self.update_scale_var)
        elif value == 'Fill':
            self.parent.zoom(ImageScaling.Mode.Fill, shrink=True, expand=True)
            self.after_idle(self.update_scale_var)
        elif value == 'Original':
            self.parent.zoom(ImageScaling.Mode.Original)
            self.scale_var.set(100)
        elif value == '50':
            self.parent.zoom(ImageScaling.Mode.Scaled, factor=0.5)
            self.scale_var.set(50)
        elif value == '200':
            self.parent.zoom(ImageScaling.Mode.Scaled, factor=2)
            self.scale_var.set(200)
        elif value == '300':
            self.parent.zoom(ImageScaling.Mode.Scaled, factor=3)
            self.scale_var.set(300)

    def on_scale_change(self, value):
        self.parent.zoom(ImageScaling.Mode.Scaled, factor=self.scale_var.get() / 100)
        self.mode_var.set('Scaled')

    def update_scale_var(self):
        self.scale_var.set(self.parent.images['left'].scaling_percent)
