import os, re, sys, contextlib
import logging
import imagej
import pandas as pd


MACRO_PATH = '/home/mitocab/GitHub/MiNAI/fiji/mina_analysis.py'

OUTPUT_ORDER = [
        'image_title',
        'thresholding_op',
        'use_ridge_detection',
        'high_contrast',
        'low_contrast',
        'line_width',
        'min_line_length',
        'mitochondrial_footprint',
        'punctate_count',
        'punctate_len_mean',
        'punctate_len_med',
        'punctate_len_stdevp',
        'rod_count',
        'rod_len_mean',
        'rod_len_med',
        'rod_len_stdevp',
        'network_count',
        'network_branch_count',
        'network_len_mean',
        # 'network_len_med',
        # 'network_len_stdevp',
        'branch_len_mean',
        'branch_len_med',
        'branch_len_stdevp',
        'summed_branch_lens_mean',
        'summed_branch_lens_med',
        'summed_branch_lens_stdevp',
        'network_branches_mean',
        'network_branches_med',
        'network_branches_stdevp',
]


def main():
    ij = imagej.init('/home/mitocab/Fiji.app')
    print(ij.getApp().getInfo(True))

    # Load mina_analysis macro
    with open(MACRO_PATH, 'r') as f:
        mina_macro = f.read()

    mina_args = {
        #'root_directory': '/home/mitocab/Documents/BatchScriptTest',
        'root_directory': '/home/mitocab/Documents/Box-05282020',
        'regex_string': '.*_cp_skel_[0-9]*.*',
        'use_ridge_detection': False,
        'verbose': False,
    }
    # print(len(mina_macro))

    result = ij.py.run_script('py', mina_macro, mina_args) # Run MiNA on the IJ module
    ij_out = ij.py.from_java(result.getOutputs())          # Get the outputs
    py_out = {} # Have to manually copy the IJ dictionary to Python, even though
                # it is already Python-ated (because it is a JavaMap and not a dict)
                # Pandas won't take the raw Pyimagej casting of the dict.
    
    sort_by_order = lambda kv: OUTPUT_ORDER.index(kv[0])
    for k, v in sorted(ij_out.items(), key=sort_by_order):
        # Format the items so that they are save-able into the CSV
        # (and to potentially re-cast them to their proper types)
        v = v.strip('[]').split(', ')
        for i in range(len(v)):
            if v[i].startswith("u'") or v[i].startswith('u"'):
                v[i] = v[i][2:]
            v[i] = v[i].strip('\'\"')
        
        ij_out[k] = v
        py_out[k] = v
        print(k, ':\n', py_out[k])

    df = pd.DataFrame.from_dict(py_out)
    df.to_csv('/home/mitocab/Documents/output.csv')



'''
Program execution starts here.
'''
if __name__ == '__main__':
    main()