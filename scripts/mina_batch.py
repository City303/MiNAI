import os, re, sys, contextlib
import logging
import imagej
import pandas as pd
from tqdm import tqdm

OUTPUT_ORDER = [
    ('image_title', 'Image title'),
    #('preprocessor_path', 'Preprocessor path'),
    #('postprocessor_path', 'Postprocessor path'),
    ('thresholding_op', 'Thresholding method'),
    ('use_ridge_detection', 'Ridge detection?'),
    ('high_contrast', 'High contrast'),
    ('low_contrast', 'Low constrast'),
    ('line_width', 'Line width'),
    ('mitochondrial_footprint', 'Mitochondrial footprint'),
    ('punctate_count', 'Number of punctates'),
    ('rod_count', 'Number of rods'),
    ('network_count', 'Number of networks'),
    #('punctate_len_mean', 'Mean punctate length'),
    #('punctate_len_med', 'Median punctate length'),
    #('punctate_len_stdevp', 'Stdev punctate length'),
    ('rod_len_mean', 'Mean rod length'),
    # ('rod_len_med', 'Median rod length'),
    # ('rod_len_stdevp', 'Stdev rod length'),
    ('network_branch_count', 'Network branch count'),
    ('network_len_mean', 'Mean network length'),
    # 'network_len_med',
    # 'network_len_stdevp',
    ('branch_len_mean', 'Mean branch length'),
    # ('branch_len_med', 'Median branch length'),
    # ('branch_len_stdevp', 'Stdev branch length'),
    ('summed_branch_lens_mean', 'Mean summed branch lengths'),
    #('summed_branch_lens_med', 'Median summed branch lengths'),
    #('summed_branch_lens_stdevp', 'Stdev summed branch lengths'),
    ('network_branches_mean', 'Mean network branches'),
    #('network_branches_med', 'Median network branches'),
    #('network_branches_stdevp', 'Stdev network branches'),
]

MACRO_PATH = '/home/mitocab/GitHub/MiNAI/fiji/mina_analysis.py'


def main():
    ij = imagej.init('/home/mitocab/Fiji.app')
    print(ij.getApp().getInfo(True))

    # Load mina_analysis macro
    with open(MACRO_PATH, 'r') as f:
        mina_macro = f.read()

    mina_args = {
        'root_directory': ij.py.to_java('/home/mitocab/Documents/Box-05282020'),
        'regex_string': ij.py.to_java('.*_cp_skel_[0-9]*.*'),
        'use_ridge_detection': False,
        'verbose': True,
    }
    print(len(mina_macro))

    result = ij.py.run_script('py', mina_macro, mina_args) # Run MiNA on the IJ module
    output = ij.py.from_java(result.getOutputs())          # Get the outputs
    print(output)

    df = pd.DataFrame.from_dict(output)
    df.to_csv('/home/mitocab/Documents/output.csv')



'''
Program execution starts here.
'''
if __name__ == '__main__':
    main()