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

macro="""
#@ String image_path
#@ String macro_path
#@output Object result

open(image_path)
result = runMacro(macro_path)
"""

args = {
    'image_path': none,
    'macro_path': MACRO_PATH
}
result = ij.py.run_script(macro, args)

print(result)
print('Success')
