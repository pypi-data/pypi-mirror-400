import tkinter as tk
import ttkbootstrap as ttk


class TransientMenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.frame = ttk.Frame(self)
        self.frame.grid(column=0, row=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.bind('<KeyPress>', self.key_pressed)
        self.bind('<ButtonPress>', self.button_pressed)

        self.items = []

        self.resizable(False, False)
        self.overrideredirect(True)
        self.withdraw()

    def append_widget(self, widget, **kwargs):
        if len(self.items) == 0:
            self.add_spacer(height=3)
        kwargs.update(
            padx=kwargs.pop('padx', 5),
            sticky=kwargs.pop('sticky', 'nwe'),
        )
        widget.grid(column=0, row=len(self.items), **kwargs)
        self.items.append(widget)

    def add_radiobutton(self, *args, **kwargs):
        button = ttk.Radiobutton(self.frame, *args, **kwargs)
        self.append_widget(button)

    def add_scale(self, *args, **kwargs):
        kwargs['orient'] = kwargs.get('orient', tk.HORIZONTAL)
        scale = ttk.Scale(self.frame, *args, **kwargs)
        self.append_widget(scale, pady=8)

    def add_spacer(self, height=10):
        spacer = ttk.Frame(self.frame, height=height)
        spacer.grid(column=0, row=len(self.items), sticky='nwe')
        self.items.append(spacer)

    def key_pressed(self, evt):
        self.unpost()

    def button_pressed(self, evt):
        if (
            evt.x < 0
            or self.winfo_width() < evt.x
            or evt.y < 0
            or self.winfo_height() < evt.y
        ):
            self.unpost()

    def post(self, pos):
        self.geometry(f'+{pos.x}+{pos.y}')
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()
        self.focus_set()

    def unpost(self):
        self.grab_release()
        self.withdraw()
