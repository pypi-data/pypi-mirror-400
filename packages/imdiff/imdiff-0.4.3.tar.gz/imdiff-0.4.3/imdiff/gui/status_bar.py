import tkinter as tk
import ttkbootstrap as ttk


class StatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.left_file = tk.StringVar()
        self.label_left_file = ttk.Entry(
            self, textvariable=self.left_file, justify=tk.LEFT, state='readonly'
        )

        self.right_file = tk.StringVar()
        self.label_right_file = ttk.Entry(
            self, textvariable=self.right_file, justify=tk.LEFT, state='readonly'
        )

        self.frame_diff_status = ttk.Frame(
            self, relief=tk.RIDGE, borderwidth=2, style='White.TFrame'
        )
        self.label_diff_status = tk.Text(
            self.frame_diff_status,
            width=20,
            height=2,
            borderwidth=6,
            highlightthickness=0,
            relief=tk.SOLID,
        )
        self.label_diff_status.tag_config('center', justify=tk.CENTER)

        self.layout()

    def layout(self):
        self.label_diff_status.grid(column=0, row=0)
        self.frame_diff_status.columnconfigure(0, weight=1)
        self.frame_diff_status.rowconfigure(0, weight=1)

        self.label_left_file.grid(column=0, row=0, sticky='nwe')
        self.label_right_file.grid(column=0, row=1, sticky='nwe')
        self.frame_diff_status.grid(column=1, row=0, rowspan=2, sticky='nsew')

        self.columnconfigure(0, weight=1)

    def set_diff_status(self, message):
        self.label_diff_status.replace(1.0, tk.END, message, 'center')
        if message.count('\n') == 1:
            self.label_diff_status.configure(height=2, pady=5)
        else:
            self.label_diff_status.configure(height=1, pady=17)

    def clear(self):
        self.left_file.set('')
        self.right_file.set('')
        self.set_diff_status('')

    def update_labels(self, comparator):
        if comparator:
            left = comparator.left_file
            self.left_file.set(str(left.resolve()) if left else '')
            self.label_left_file.xview_moveto(1)

            right = comparator.right_file
            self.right_file.set(str(right.resolve()) if right else '')
            self.label_right_file.xview_moveto(1)

            diff_info = comparator.diff_info
            if isinstance(diff_info, str):
                self.set_diff_status(diff_info)
            else:
                self.set_diff_status(f'Normalized RMSE:\n{diff_info:g}')
        else:
            self.clear()
