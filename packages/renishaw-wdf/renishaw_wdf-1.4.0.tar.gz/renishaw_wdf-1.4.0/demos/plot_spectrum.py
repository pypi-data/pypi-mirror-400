# Copyright (c) 2023 Renishaw plc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Demonstrate plotting Wdf file spectra using Matplotlib.
"""

import sys
import os
import argparse
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkfiledialog
from tkinter import messagebox as tkmessagebox
from plotutil import Plot

# allow demos to load the wdf package from the parent folder (not required for normal installation)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wdf import (Wdf, WdfFlags, WdfBlockId)

if sys.platform == 'win32':
    # Fix for tiny menus on high dpi display
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)

DEF_TITLE = "Wdf Spectrum Plot"


class App(ttk.Frame):
    """Application class."""
    def __init__(self, master, options, **kwargs):
        self.options = options
        super(App, self).__init__(master, **kwargs)
        self.master.wm_minsize(800, 600)
        self.master.wm_title(DEF_TITLE)
        self.create_ui()
        self.create_menu()
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def create_ui(self):
        upper = ttk.Frame(self)
        label = ttk.Label(upper, text="Spectrum: ")
        self.scale = ttk.Scale(
            upper, from_=0, to=1, command=self.on_index_changed)
        label.grid(row=0, column=0, sticky=tk.NSEW)
        self.scale.grid(row=0, column=1, sticky=tk.NSEW)
        upper.grid_rowconfigure(0, weight=1)
        upper.grid_columnconfigure(1, weight=1)

        self.plot = Plot(self, figsize=(6, 4), background="grey80")

        upper.grid(row=0, column=0, sticky=tk.NSEW)
        self.plot.grid(row=1, column=0, sticky=tk.NSEW)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_menu(self):
        menu = tk.Menu(self.master)
        fileMenu = tk.Menu(menu, tearoff=False)
        optMenu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label='File', menu=fileMenu)
        menu.add_cascade(label='Options', menu=optMenu)
        fileMenu.add_command(label='Open ...', command=self.on_file_open)
        fileMenu.add_command(label='Exit', command=self.on_file_exit)
        optMenu.add_command(label="Add toolbar", command=self.plot.add_toolbar)
        self.master.configure(menu=menu)

    def on_index_changed(self, value: str) -> None:
        self.after_idle(self.draw_spectrum, self.options.filename, int(float(value)))

    def on_file_open(self):
        filetypes = (("WiRE Data Files", "*.wdf"), ("All files", "*.*"))
        filename = tkfiledialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.plot.figure.clear()
            self.options.filename = filename
            self.load(filename)

    def on_file_exit(self):
        self.master.destroy()

    def load(self, filename: str):
        with Wdf(filename) as wdf:
            self.scale.configure(to=wdf.hdr.ncollected - 1)
            self.scale.set(0)
        self.after_idle(self.draw_spectrum, filename, 0)

    def draw_spectrum(self, filename: str, index: int):
        """Plot spectrum."""
        print(f"index: {type(index)} {index}")
        name = os.path.basename(filename)
        self.master.wm_title(f"{name} - {DEF_TITLE}")
        title = f'{name} acquisition {index}'
        with Wdf(filename) as wdf:
            track = 0
            if (wdf.hdr.flags & WdfFlags.Multitrack
                    and self.wdf.hdr.ntracks == self.wdf.hdr.nspectra):
                track = index

            fig = self.plot.figure
            fig.clear()
            fig.set_tight_layout(True)

            ax = fig.add_subplot(1, 1, 1)
            ax.set_title(title)
            ax.plot(wdf.xlist(track), wdf[index])

        self.plot.canvas.draw()


def main(args=None):
    """Main program entry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename')
    options = parser.parse_args(args)

    root = tk.Tk()
    app = App(root, options)
    if options.filename:
        app.after_idle(app.load, options.filename)

    try:
        root.mainloop()
    except Exception as e:
        tkmessagebox.showerror('Error', e)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
