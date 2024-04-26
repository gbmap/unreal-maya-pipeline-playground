import unreal
import tkinter as tk
from tkinter import filedialog

def browse_for_file():
    tk.Tk().withdraw()
    return filedialog.askdirectory()

dir_import = browse_for_file()
print(dir_import)
if dir_import:
    unreal.log("Selected directory: {}".format(dir_import))
else:
    unreal.log("No file selected.")

