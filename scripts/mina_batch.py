import os
import sys
import contextlib
import imagej
import pandas as pd


'''
Initializes an Pyimagej handle with an image so that
macros can access this image.
'''
def init_ij(ij_handle, img_path):
    loader_macro="""
#@ String image_path
open(image_path)
"""
    ij_handle.py.run_macro(loader_macro, {'image_path': img_path})



'''
Main method of the program
'''
def main():
    ij = imagej.init('/home/mitocab/Downloads/Fiji.app')
    
    print(ij.getVersion())

    ROOT = '/home/mitocab/Documents/Box-05282020'
    FILE = 'BJ & SBG4-5/N3 5-2-19/No FCCP/SBG5/image 4/sbg5 p8 no fccp dish 6 r4 05-02-2019_cp_skel_1.tiff'
    MACRO_PATH = '/home/mitocab/Downloads/Fiji.app/macros/MiNA-py/mina_analysis.py'

    # The list of outputs returned from mina_analysis.py. If the code for
    # that script is updated with new outputs, please add them to this
    # output order at the column it should be presented in. Otherwise,
    # the new output will not be included in the results.
    output_order = [
        'image_title',
        'preprocessor_path',
        'postprocessor_path',
        'thresholding_op',
        'use_ridge_detection',
        'high_contrast',
        'low_contrast',
        'line_width',
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

    with open(MACRO_PATH, 'r') as f:
        mina_macro = f.read()

    mina_args = {
        'use_ridge_detection': ij.py.to_java(False)
    }
 
    # Load the image into the IJ module
    init_ij(ij, os.path.join(ROOT, FILE))       

    # Run MiNA on the IJ module
    result = ij.py.run_script("py", mina_macro, mina_args)  

    # Get the outputs
    output = ij.py.from_java(result.getOutputs())
    print('\nOutput parameters:')
    for key in output_order:
        print(key, ': ', output[key])

'''
Program execution starts here.
'''
if __name__ == '__main__':
    main()