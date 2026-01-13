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

"""Embed matplotlib in a Tkinter frame."""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
import matplotlib.backends.backend_tkagg as tkagg


class Plot(ttk.Frame):
    """Embed matplotlib in the Tkinter application window."""
    # ex: https://github.com/I2PC/scipion/blob/master/scipion-master/pyworkflow/matplotlib_image.py
    def __init__(self, master, **kwargs):
        if "figsize" in kwargs:
            self.figsize = kwargs["figsize"]
            del kwargs["figsize"]
        super(Plot, self).__init__(master)
        self.figure = Figure(figsize=self.figsize, frameon=False, dpi=100)
        self.canvas = tkagg.FigureCanvasTkAgg(self.figure, self)
        self.toolbar = None
        widget = self.canvas.get_tk_widget()
        widget.grid(row=0, column=0, sticky=tk.NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(**kwargs)

    def add_toolbar(self):
        # The next 2 lines are required to ensure the font module actually was loaded
        # to avoid an AttributeError from the NavigationToolbar2Tk class.
        import tkinter.font
        font = tkinter.font.nametofont('TkDefaultFont')
        font.configure(weight=tkinter.font.BOLD)
        self.toolbar = tkagg.NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.master = self.master
        self.toolbar.grid(row=1, column=0, sticky=tk.NSEW)

    def show(self):
        self.canvas.show()

    @property
    def widget(self):
        return self.canvas.get_tk_widget()

    def configure(self, **kwargs):
        return self.widget.configure(**kwargs)
