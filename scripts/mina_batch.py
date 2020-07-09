import os, re, sys, contextlib
import logging
import imagej
import pandas as pd

# TODO convert to relpath or make it changable
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
    'rod_count',
    'network_count',
    'rod_len_mean',
    'rod_len_med',
    'rod_len_stdevp',
    'network_branches',
    'network_branches_mean',
    'all_branches',
    'all_branches_len_mean',
    'all_branches_len_med',
    'all_branches_len_stdevp',
    'summed_branches_lens_mean',
    'summed_branches_lens_med',
    'summed_branches_lens_stdevp',
]

OUTPUT_FILTER = [
    'image_title',
    'mitochondrial_footprint',
    'punctate_count',
    'rod_count',
    'network_count',
    'rod_len_mean',
    'rod_len_med',
    'rod_len_stdevp',
    'network_branches',
    'network_branches_mean',
    'all_branches',
    'all_branches_len_mean',
    'all_branches_len_med',
    'all_branches_len_stdevp',
    'summed_branches_lens_mean',
    'summed_branches_lens_med',
    'summed_branches_lens_stdevp',
]

OUTPUT_TITLES = [
    'Image title',
    'Mitochondrial footprint',
    '# of punctates',
    '# of rods',
    '# of networks',
    'Rod length mean',
    'Rod length median',
    'Rod length population stdev',
    '# of network branches',
    'Network branches length mean'
    '# of all branches (networks and rods)'
    'All branches length mean',
    'All branches length median',
    'All branches length population stdev',
    'All branched groups mean summed length',
    'All branched groups median summed length',
    'All branched groups population stdev summed length'
]


def main(root_path, regex_str, output_path):
    ij = imagej.init('/home/mitocab/Fiji.app')
    print(ij.getApp().getInfo(True))

    # Load mina_analysis macro
    print('Reading MiNAI macro file...')
    with open(MACRO_PATH, 'r') as f:
        mina_macro = f.read()

    mina_args = {
        'root_directory': root_path,
        'regex_string'  : regex_str,
        'use_ridge_detection': False,
        'verbose': False,
    }
    # print(len(mina_macro))

    print('Calling MiNAI macro with args...')
    print(f'    Root directory: {root_path}')
    print(f'    Regex string  : {regex_str}')
    result = ij.py.run_script('py', mina_macro, mina_args) # Run MiNA on the IJ module
    ij_out = ij.py.from_java(result.getOutputs())          # Get the outputs
    py_out = {} # Have to manually copy the IJ dictionary to Python, even though
                # it is already Python-ated (because it is a JavaMap and not a dict)
                # Pandas won't take the raw Pyimagej casting of the dict.
    
    sort_by_order = lambda kv: OUTPUT_FILTER.index(kv[0])
    for k, v in sorted(ij_out.items(), key=sort_by_order):
        # Format the items so that they are save-able into the CSV
        # (and to potentially re-cast them to their proper types)
        if k in OUTPUT_FILTER:
            idx   = OUTPUT_FILTER.index(k)
            title = OUTPUT_TITLES[idx]
            v = v.strip('[]').split(', ')
            for i in range(len(v)):
                if v[i].startswith("u'") or v[i].startswith('u"'):
                    v[i] = v[i][2:]
                v[i] = v[i].strip('\'\"')
            
            py_out[title] = v
            print(title, ':\n', py_out[title])

    df = pd.DataFrame.from_dict(py_out)
    df.to_csv(output_path)



'''
Program execution starts here.
'''
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python mina_batch.py [1] [2]')
        print('[1]: root directory with skeletons (i.e. "/home/mitocab/Documents/Box-05282020"')
        print('[2]: regex to find skeleton files  (i.e. ".*_cp_skel_[0-9]*.*"')
        print('[3]: output directory and name     (i.e. "/home/mitocab/Documents/output.csv"')
        sys.exit()

    root_path   = sys.argv[1]
    regex_str   = sys.argv[2]
    output_path = sys.argv[3]
    main(root_path, regex_str, output_path)
