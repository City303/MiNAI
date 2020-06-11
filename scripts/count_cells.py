import os
import re
import string
import pandas as pd

ROOT_DIR = '/home/mitocab/Documents/Box-05282020'

manual_re = re.compile('.*_skel_cell[0-9]*_ps.*')
cp_re     = re.compile('.*_cp_skel_[0-9]*.*')

manual_cnt = 0
cp_cnt     = 0

man_counts = {}
cp_counts  = {}


for subdir, dirs, files in os.walk(ROOT_DIR):
    subdir_key = subdir.replace(ROOT_DIR + '/', '')
    if subdir_key not in man_counts:
        man_counts[subdir_key] = 0
        cp_counts[subdir_key] = 0

    for file in files:
        if manual_re.match(file):
            man_counts[subdir_key] += 1
        elif cp_re.match(file):
            cp_counts[subdir_key] += 1

differences = {}
for key in man_counts:
    differences[key] = cp_counts[key] - man_counts[key]
    #if differences[key] == 50:
    #   print(key)

# print(differences)

diff_frame = pd.DataFrame(differences.values())
print(diff_frame.describe())

#print('Manual', man_counts)
#print('CellProfiler', cp_counts)

print('Manual totals', sum(man_counts.values()))
print('CellProfiler totals', sum(cp_counts.values()))