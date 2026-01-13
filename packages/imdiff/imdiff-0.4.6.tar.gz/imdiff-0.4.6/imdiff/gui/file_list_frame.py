import concurrent.futures
import logging
import enum
import filecmp
import multiprocessing
import pathlib
import threading
import time
import queue
import subprocess
import sys

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk

from ..image_comparator import ImageComparator
from ..list_files import list_files, is_image
from ..util import Size, separate_thread


log = logging.getLogger(__name__)


class IterableQueue(queue.Queue):
    class Status(enum.Enum):
        Inactive = 0
        Filling = 1
        Complete = 2

    def __init__(self):
        self.status = IterableQueue.Status.Inactive
        super().__init__()

    def __iter__(self):
        return self

    def __next__(self):
        if self.status == IterableQueue.Status.Inactive:
            raise StopIteration
        while True:
            try:
                # Block briefly to avoid busy-waiting and allow UI updates to run
                return self.get(timeout=0.05)
            except queue.Empty:
                # When the producer marks the queue Complete and it's empty, stop
                if self.status == IterableQueue.Status.Complete:
                    self.status = IterableQueue.Status.Inactive
                    raise StopIteration


class FileListFrame(ttk.Frame):
    def __init__(self, parent, on_select=None, left_label='left', right_label='right'):
        super().__init__(parent)

        self.on_select_command = on_select
        self.left_label = left_label
        self.right_label = right_label

        self.files = {}
        self.file_entries = []
        self.executor = None
        self.file_queue = IterableQueue()
        self.file_processing_queue = IterableQueue()
        self.file_properties_queue = IterableQueue()
        self.text_file_queue = IterableQueue()
        self.leftdir = None
        self.rightdir = None


        self.button_choose_left_dir = ttk.Button(
            self, text=f'{self.left_label.capitalize()}...', command=self.askleftdir
        )
        self.button_choose_right_dir = ttk.Button(
            self, text=f'{self.right_label.capitalize()}...', command=self.askrightdir
        )
        self.button_text_diff = ttk.Button(
            self, text=f'Text Diff', command=self.textdiff
        )
        self.treeview_frame = tk.Frame(self)

        self.file_treeview = ttk.Treeview(self.treeview_frame, columns=('stat',))
        self.file_treeview.heading('#0', text='File (▲)')
        self.file_treeview.heading('stat', text='Stat')
        w = tk.font.Font().measure(' Stat (▲) ')
        self.file_treeview.column(
            'stat', width=w, minwidth=w, stretch=False, anchor='center'
        )

        self.file_treeview.tag_configure('identical', foreground='gray')
        self.file_treeview.tag_configure('missing', foreground='orange')
        self.file_treeview.tag_configure('not-found', foreground='violet')
        self.file_treeview.tag_configure('failed-to-load', foreground='violet')
        self.file_treeview.tag_configure('different-size', foreground='red')
        self.file_treeview.tag_configure('new', foreground='blue')
        self.file_treeview.tag_configure('different', foreground='red')
        self.file_treeview.tag_configure('similar', foreground='black')

        self.xscroll = ttk.Scrollbar(
            self.treeview_frame, orient=tk.HORIZONTAL, command=self.file_treeview.xview
        )
        self.yscroll = ttk.Scrollbar(
            self.treeview_frame, orient=tk.VERTICAL, command=self.file_treeview.yview
        )

        self.file_treeview['xscrollcommand'] = self.xscroll.set
        self.file_treeview['yscrollcommand'] = self.yscroll.set

        self.layout()
        self.bind_events()

    def layout(self):
        self.file_treeview.grid(column=0, row=0, sticky='nsew')
        self.xscroll.grid(column=0, row=1, columnspan=2, sticky='ew')
        self.yscroll.grid(column=1, row=0, sticky='ns')
        self.treeview_frame.columnconfigure(0, weight=1)
        self.treeview_frame.rowconfigure(0, weight=1)

        self.button_choose_left_dir.grid(column=0, row=0, padx=5, pady=5, sticky='nw')
        self.button_choose_right_dir.grid(column=1, row=0, padx=5, pady=5, sticky='nw')
        self.button_text_diff.grid(column=2, row=0, padx=5, pady=5, sticky='ne')
        self.treeview_frame.grid(column=0, row=1, columnspan=3, sticky='nsew')

        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)

    def bind_events(self):
        self.file_treeview.bind('<<TreeviewSelect>>', self.on_select)
        self.file_treeview.unbind_class('Treeview', '<Down>')
        self.file_treeview.unbind_class('Treeview', '<Up>')
        self.file_treeview.unbind_class('Treeview', '<Right>')

    def on_down(self, evt, add=False):
        if sel := self.file_treeview.selection():
            curitem = sel[-1]
            if nextitem := self.file_treeview.next(curitem):
                if add:
                    self.file_treeview.selection_add(nextitem)
                else:
                    self.file_treeview.selection_set(nextitem)
                self.file_treeview.focus(nextitem)
                self.file_treeview.see(nextitem)
        return 'break'

    def on_up(self, evt, add=False):
        if sel := self.file_treeview.selection():
            curitem = sel[0]
            if previtem := self.file_treeview.prev(curitem):
                if add:
                    self.file_treeview.selection_add(previtem)
                else:
                    self.file_treeview.selection_set(previtem)
                self.file_treeview.focus(previtem)
                self.file_treeview.see(previtem)
        return 'break'

    def on_select(self, evt=None):
        if file_path := self.file_treeview.focus():
            if self.on_select_command and self.files and file_path in self.files:
                self.on_select_command(self.files[file_path])
            self.after_idle(self.update_file_item, file_path)
        else:
            self.on_select_command(None)
        return 'break'

    def minsize(self):
        widgets = (
            self.button_choose_left_dir,
            self.button_choose_right_dir,
            self.yscroll,
        )
        w = sum([w.winfo_width() for w in widgets])
        return Size((w + 600, 400))

    def askleftdir(self):
        if topdir := filedialog.askdirectory(initialdir=self.leftdir):
            self.leftdir = pathlib.Path(topdir)
            self.load_files()

    def askrightdir(self):
        if topdir := filedialog.askdirectory(initialdir=self.rightdir):
            self.rightdir = pathlib.Path(topdir)
            self.load_files()

    def textdiff(self):
        subprocess.Popen(('meld', self.leftdir, self.rightdir))

    def signal_shutdown(self):
        self.file_queue.status = IterableQueue.Status.Inactive
        self.file_processing_queue.status = IterableQueue.Status.Inactive
        self.file_properties_queue.status = IterableQueue.Status.Inactive
        self.text_file_queue.status = IterableQueue.Status.Inactive
        if executor := self.executor:
            executor.shutdown(wait=False, cancel_futures=True)

    def clear_file_list(self):
        self.files = {}
        self.file_entries = []
        for item in self.file_treeview.get_children():
            self.file_treeview.delete(item)

    @separate_thread
    def queue_files(self):
        assert self.file_queue.status == IterableQueue.Status.Filling
        assert self.text_file_queue.status == IterableQueue.Status.Filling
        if self.leftdir and self.rightdir:
            for file_path, left, right in list_files(self.leftdir, self.rightdir):
                if is_image(left) or is_image(right):
                    file_cmp = ImageComparator(left, right)
                    self.files[file_path] = file_cmp
                    self.file_queue.put(file_path)
                elif self.text_file_queue.status == IterableQueue.Status.Filling:
                    if left.is_file() and right.is_file():
                        self.text_file_queue.put(file_path)
            self.file_queue.status = IterableQueue.Status.Complete
            self.text_file_queue.status = IterableQueue.Status.Complete

    def append_file_entry(self, file_path):
        self.file_entries.append(file_path)
        self.after_idle(lambda: self.file_treeview.insert('', 'end', file_path, text=file_path))

    @separate_thread
    def append_files_to_list(self):
        assert self.file_processing_queue.status == IterableQueue.Status.Filling

        BATCH_SIZE = 200
        batch = []

        def flush_batch(items):
            for p in items:
                self.file_treeview.insert('', 'end', p, text=p)

        for file_path in self.file_queue:
            self.file_entries.append(file_path)
            self.file_processing_queue.put(file_path)  # stream to processing queue
            batch.append(file_path)
            if len(batch) >= BATCH_SIZE:
                self.after(0, flush_batch, batch[:])
                batch.clear()

        if batch:
            self.after(0, flush_batch, batch[:])

        self.file_processing_queue.status = IterableQueue.Status.Complete
        self.after_idle(lambda: self.file_treeview.heading('#0', command=lambda: self.sort_filepaths(0, True)))
        self.after_idle(lambda: self.file_treeview.heading('stat', command=lambda: self.sort_stat(False)))

    @staticmethod
    def get_diff_info(file_path, comparator):
        category_chars = {
            'identical': '=',
            'missing': '-',
            'new': '+',
            'different-size': 'S',
            'failed-to-load': 'L',
            'not-found': 'F',
        }

        diff_info = comparator.diff_info

        if diff_info == 'failed-to-load':
            comparator.clear()
            diff_info = comparator.diff_info

        try:
            category = category_chars[diff_info]
        except KeyError:
            assert isinstance(diff_info, float)
            nrmse = diff_info
            diff_info = 'similar' if nrmse < 0.02 else 'different'
            category = '~' if nrmse < 0.02 else 'D'

        return file_path, category, diff_info, comparator

    @separate_thread
    def process_files(self):
        while self.file_processing_queue.status == IterableQueue.Status.Filling:
            self.update_idletasks()
        assert self.file_processing_queue.status == IterableQueue.Status.Complete
        assert self.file_properties_queue.status == IterableQueue.Status.Filling
        with concurrent.futures.ProcessPoolExecutor() as executor:
            self.executor = executor
            try:
                jobs = []
                for file_path in self.file_processing_queue:
                    jobs.append(executor.submit(
                        FileListFrame.get_diff_info, file_path, self.files[file_path]))
                for job in concurrent.futures.as_completed(jobs):
                    file_path, category, diff_info, icmp = job.result()
                    self.files[file_path] = icmp
                    self.file_properties_queue.put((file_path, category, diff_info))
                self.file_properties_queue.status = IterableQueue.Status.Complete
            finally:
                self.executor = None

    @separate_thread
    def process_text_files(self):
        assert self.text_file_queue.status == IterableQueue.Status.Filling
        for file_path in self.text_file_queue:
            left = self.leftdir / file_path
            right = self.rightdir / file_path
            if not filecmp.cmp(left, right):
                self.button_text_diff.configure(bootstyle='danger')
                self.text_file_queue.status = IterableQueue.Status.Complete
                break

    def set_file_properties(self, file_path, category, diff_info):
        try:
            self.file_treeview.set(file_path, 'stat', category)
            self.file_treeview.item(file_path, tags=(diff_info,))

        except tk.TclError as e:
            log.debug(f'exception caught while setting file properties: {e}')

    @separate_thread
    def update_properties(self):
        for item in self.file_properties_queue:
            file_path, category, diff_info = item
            self.set_file_properties(file_path, category, diff_info)
        def _remove_status_label(self=self):
            if hasattr(self, 'status_label'):
                self.status_label.destroy()
        self.after(0, _remove_status_label)

    def load_files(self):
        self.clear_file_list()
        # Minimal status indicator
        if not hasattr(self, 'status_var'):
            self.status_var = tk.StringVar(value='')
            self.status_label = ttk.Label(self.treeview_frame, textvariable=self.status_var, anchor='w')
            self.status_label.grid(column=0, row=2, columnspan=2, sticky='sew')
        self.status_var.set('Loading...')
        self.file_queue.status = IterableQueue.Status.Filling
        self.text_file_queue.status = IterableQueue.Status.Filling
        self.queue_files()
        self.file_processing_queue.status = IterableQueue.Status.Filling
        self.append_files_to_list()
        self.file_properties_queue.status = IterableQueue.Status.Filling
        self.process_files()
        self.update_properties()
        self.process_text_files()

    def select_next(self):
        select_next = None
        if sel := self.file_treeview.selection():
            curitem = sel[-1]
            select_next = (
                self.file_treeview.next(curitem)
                or self.file_treeview.prev(curitem)
            )
        if select_next:
            self.file_treeview.selection_add(select_next)
            self.file_treeview.focus(select_next)
            self.file_treeview.see(select_next)
        else:
            self.file_treeview.selection_set()
        self.on_select()

    def delete_entry(self, file_path):
        del self.files[file_path]
        self.file_entries.remove(file_path)
        try:
            if sel := self.file_treeview.selection():
                curitem = sel[-1]
                if curitem == file_path:
                    self.select_next()
            self.file_treeview.delete(file_path)
        except tk.TclError:
            log.debug(f'ignoring attempt to delete nonexistant entry: {file_path}')

    def delete(self, file_path):
        if comparator := self.files.get(file_path, None):
            left_file, right_file = comparator.left_file, comparator.right_file
            log.info(f'DELETE: {left_file} {right_file}')
            comparator.delete_files()
        self.delete_entry(file_path)

    @separate_thread
    def update_file_item(self, file_path):
        if file_path not in self.files:
            try:
                file_path = str(pathlib.Path(file_path).relative_to(self.rightdir))
            except ValueError:
                try:
                    file_path = str(pathlib.Path(file_path).relative_to(self.leftdir))
                except ValueError:
                    assert not file_path.is_absolute()

        if (
            not (self.leftdir / file_path).exists()
            and not (self.rightdir / file_path).exists()
        ):
            self.delete(file_path)
            return

        res = FileListFrame.get_diff_info(file_path, self.files[file_path])
        file_path, category, diff_info, icmp = res
        self.files[file_path] = icmp
        self.set_file_properties(file_path, category, diff_info)

    def sort_filepaths(self, nparts, reverse):
        tv = self.file_treeview
        l = [(pathlib.Path(tv.item(k)['text']), k) for k in tv.get_children()]
        maxparts = max(len(p.parts) for p, _ in l)

        def transform_key(key, nparts=nparts):
            p = key[0].parts
            if -len(p) <= nparts < len(p):
                return (str(pathlib.Path(*p[nparts:])), str(pathlib.Path(*p[:nparts])))
            else:
                return (str(p),)

        l.sort(key=transform_key, reverse=reverse)
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        tv.column('#0', anchor=(tk.E if nparts < 0 else tk.W))
        if reverse:
            next_args = (-maxparts if nparts == (maxparts - 1) else (nparts + 1), False)
        else:
            next_args = (nparts, True)
        tv.heading(
            '#0',
            text=f'File ({"▼" if reverse else "▲"}{nparts or ""})',
            command=lambda: self.sort_filepaths(*next_args),
        )
        tv.heading('stat', text='Stat')

    def sort_stat(self, reverse):
        tv = self.file_treeview
        colindex = tv['columns'].index('stat')
        try:
            l = [(tv.item(k)['values'][colindex], k) for k in tv.get_children()]
        except IndexError:
            # do not sort if we are in the proccess of updating the diffs
            return

        def transform_key(key):
            return ('F', 'L', 'D', 'S', '+', '~', '-', '=').index(key[0])

        l.sort(key=transform_key, reverse=reverse)
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        tv.heading('#0', text='File')
        tv.heading(
            'stat',
            text=f'Stat ({"▼" if reverse else "▲"})',
            command=lambda: self.sort_stat(not reverse),
        )
