import os
import imagej
import pandas as pd

ij = imagej.init('/home/mitocab/Downloads/Fiji.app')
print(ij.getVersion())

ROOT = '/home/mitocab/Documents/Box-05282020'
FILE = 'BJ & SBG4-5/N3 5-2-19/No FCCP/SBG5/image 4/sbg5 p8 no fccp dish 6 r4 05-02-2019_cp_skel_1.tiff'
MACRO_PATH = '/home/mitocab/Downloads/Fiji.app/macros/MiNA-py/mina_analysis.py'
MACRO_EXT  = 'py'

image = ij.io().open(os.path.join(ROOT,FILE))

with open(MACRO_PATH) as macro:
    macro_body = macro.read()
    args = None
    result = ij.py.run_script(MACRO_EXT, macro_body, args)

print(result)
print('Success')
