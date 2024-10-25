# **************************************************************************
# *
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk) [1]
# *
# * [1] MRC Laboratory of Molecular Biology, MRC-LMB
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'gsharov@mrc-lmb.cam.ac.uk'
# *
# **************************************************************************

import importlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from typing import Optional

from perfectem import __version__
from perfectem.config import SERIALEM_PORT, SERIALEM_IP


class Application:
    def __init__(self, tests: dict, microscopes: dict) -> None:
        """ Check serialEM import and initialise vars. """
        self.root = tk.Tk()
        self.root.title(f"PerfectEM v{__version__}")
        self.root.resizable(False, False)

        try:
            self.cameras = self.get_cameras()
        except Exception as e:
            self._handle_error(e)

        self.tests = tests
        self.microscopes = microscopes

        self.scope_var = tk.StringVar()
        self.camera_var = tk.StringVar()
        self.test_var = tk.StringVar()

    def _handle_error(self, error: Exception) -> None:
        """ Handle SerialEM failure gracefully. """
        self.root.overrideredirect(True)
        self.root.withdraw()
        self.show_message(msgtype="error",
                          text="This program must be run on the computer "
                               f"with SerialEM Python module.\n\n{str(error)}")
        exit(1)

    def create_widgets(self) -> None:
        """ Create the main GUI. """
        content = ttk.Frame(self.root)
        content.grid(column=0, row=0)
        content.columnconfigure(0, weight=1, uniform="tag")
        content.columnconfigure(1, weight=2, uniform="tag")

        self._create_combobox(content, "Microscope",
                              self.scope_var,
                              list(self.microscopes.keys()),
                              0)
        self._create_combobox(content, "Camera",
                              self.camera_var,
                              self.cameras,
                              1)
        self._create_combobox(content, "Performance test",
                              self.test_var,
                              list(self.tests.values()),
                              2)

        # Help button
        help_btn = ttk.Button(content, text="?", width=1, cursor='hand2',
                              command=lambda: self.show_help(self.test_var))
        help_btn.grid(column=3, row=2, padx=5, pady=0)

        # Run button
        args_btn = self.scope_var, self.camera_var, self.test_var
        run_btn = ttk.Button(content, text="Run!", cursor='hand2',
                             command=lambda: self.run(*args_btn))
        run_btn.grid(column=0, row=3, pady=5, columnspan=4)

        self.root.focus_set()
        self.root.mainloop()

    @staticmethod
    def _create_combobox(parent, label_text, variable, values, row) -> None:
        """Helper to create a label and combobox pair."""
        label = ttk.Label(parent, text=label_text)
        label.grid(column=0, row=row, padx=5, pady=5)

        combo = ttk.Combobox(parent, textvariable=variable, state='readonly', values=values)
        combo.grid(column=1, row=row, padx=5, pady=5,
                   sticky="we" if row == 2 else "w",
                   columnspan=2)
        combo.current(0)

    @staticmethod
    def show_message(msgtype: Optional[str] = "info", text: Optional[str] = None) -> None:
        """ Show a message dialog. """
        if msgtype == "info":
            messagebox.showinfo(message=text)
        elif msgtype == "error":
            messagebox.showerror(message=text)

    def show_help(self, test_var: tk.StringVar) -> None:
        """ Show the test description help. """
        index = list(self.tests.values()).index(test_var.get())
        module = importlib.import_module("perfectem.scripts")
        func = getattr(module, list(self.tests.keys())[index])

        self.show_message(text=func.__doc__)

    def get_cameras(self):
        """ Connect to SerialEM and get the camera list. """
        import serialem as sem
        sem.ConnectToSEM(SERIALEM_PORT, SERIALEM_IP)
        self.cameras = []
        camera_num = 1
        while True:
            name = sem.ReportCameraName(camera_num)
            if name == "NOCAM":
                break
            else:
                self.cameras.append(name)
                camera_num += 1
        sem.Exit(1)

        return self.cameras

    def run(self,
            scopeVar: tk.StringVar,
            cameraVar: tk.StringVar,
            testVar: tk.StringVar) -> None:
        """ Execute selected test. """
        scope, camera, test = scopeVar.get(), cameraVar.get(), testVar.get()
        if not scope or not camera or not test:
            self.show_message(msgtype="error", text="Please select a microscope and camera.")
            return

        func_name = ""
        for item in self.tests.items():
            if item[1] == test:
                func_name = item[0]
                break

        self.root.destroy()
        module = importlib.import_module("perfectem.scripts")
        func_object = getattr(module, func_name)
        func_object(scope_name=scope,
                    camera_num=self.cameras.index(camera)+1,
                    **self.microscopes[scope][func_name]).run()
