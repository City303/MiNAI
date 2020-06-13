import os, re, sys, contextlib
import logging
import imagej
import pandas as pd
from tqdm import tqdm


'''
Initializes an Pyimagej handle with an image so that
macros can access this image.
'''
def load_image(ij_handle, img_path):
    loader_macro="""
#@ String image_path
open(image_path)
"""
    ij_handle.py.run_macro(loader_macro, {'image_path': img_path})


'''
Main method of the program

Params:
    ij: Pyimagej header
    path: path to image
'''
def eval_image(ij, path, verbose = False):
    MACRO_PATH = '/home/mitocab/Downloads/Fiji.app/macros/MiNA-py/mina_analysis.py'

    # The list of outputs returned from mina_analysis.py. If the code for
    # that script is updated with new outputs, please add them to this
    # output order at the column it should be presented in. Otherwise,
    # the new output will not be included in the results.
    #
    # The first entry is the key in outputs, and the second entry is the column header.
    output_order = [
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

    with open(MACRO_PATH, 'r') as f:
        mina_macro = f.read()

    mina_args = {
        'use_ridge_detection': ij.py.to_java(False),
        'verbose': ij.py.to_java(verbose)
    }

    load_image(ij, path) # Load the image into the IJ module       
    # print(dir(ij))
    # print(dir(ij.script()))
    # The end of execution of this script prints stuff to the console ([INFO]).
    # Python is unable to supress it since I think it is being written by Java.

    result = ij.py.run_script("py", mina_macro, mina_args) # Run MiNA on the IJ module
    output = ij.py.from_java(result.getOutputs())          # Get the outputs

    return output


def main():
    ROOT    = '/home/mitocab/Documents/Box-05282020'
    skel_re = re.compile('.*_cp_skel_[0-9]*.*')
    # FILE = 'BJ & SBG4-5/N3 5-2-19/No FCCP/SBG5/image 4/sbg5 p8 no fccp dish 6 r4 05-02-2019_cp_skel_1.tiff'

    ij = imagej.init('/home/mitocab/Downloads/Fiji.app')
    images = []

    for subdir, dirs, files in os.walk(ROOT):
        for file in files:
            if skel_re.match(file):
                images.append(os.path.join(ROOT, subdir, file))

    for i in tqdm(range(len(images))):
        output = eval_image(ij, images[i])

    print('\nOutput parameters:')
    for key, title in output_order:
        print(title, ': ', output[key])



'''
Program execution starts here.
'''
if __name__ == '__main__':
    main()