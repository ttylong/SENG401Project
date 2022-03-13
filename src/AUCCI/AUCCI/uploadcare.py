# testing uploadcare
import tkinter
from pyuploadcare import Uploadcare
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import re
import os

Uploadcare = Uploadcare(public_key =  '20a0df730e28f42bb662', secret_key = '8ad164c8ada8aaf4034f')

Tk().withdraw()
filename = str(askopenfilename())

if len(filename) > 0 or filename.lower().endswith(('.jpg', '.png')):
    print(filename)
    try:
        with open(filename, 'rb') as f:
            url = Uploadcare.upload(f)
            print(url)
    finally:
        f.close()
else:
    print("invalid input")
    exit(1)