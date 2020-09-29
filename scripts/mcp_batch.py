import sys, os, re, argparse
import imagej
import pandas as pd

MACRO_PATH  = os.path.realpath('../fiji/mcp_analysis.py')

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

    'rod_lens_mean',
    'rod_lens_med',
    'rod_lens_stdevp',
    
    'network_num_branches_count',
    'network_num_branches_mean',
    'network_branch_lens_mean',
    'network_lens_mean',
    'network_lens_median',
    'network_lens_stdevp',

    'all_branches',
    'all_branches_lens_mean',
    'all_branches_lens_med',
    'all_branches_lens_stdevp',

    'summed_branches_lens_mean',
    'summed_branches_lens_med',
    'summed_branches_lens_stdevp',
]

# Outputs that represent lengths (to convert to scale value)
# TODO can standard deviaiton be converted linearly?
LENGTH_OUTPUTS = [
    'rod_len_mean',
    'rod_len_med',
    'rod_len_stdevp',

    'network_branch_lens_mean',
    'network_lens_mean',
    'network_lens_median',
    'network_lens_stdevp',

    'all_branches_lens_mean',
    'all_branches_lens_med',
    'all_branches_lens_stdevp',

    'summed_branches_lens_mean',
    'summed_branches_lens_med',
    'summed_branches_lens_stdevp',
]

# Outputs that represent area (to convert to scale value ^ 2)
AREA_OUTPUTS = [
    'mitochondrial_footprint'
]

OUTPUT_FILTER = [
    'image_title',
    'mitochondrial_footprint',

    'punctate_count',
    'rod_count',
    'network_count',

    'rod_lens_mean',
    'rod_lens_med',
    'rod_lens_stdevp',

    'network_num_branches_count',
    'network_num_branches_mean',
    'network_branch_lens_mean',
    'network_lens_mean',
    'network_lens_median',
    'network_lens_stdevp',

    'all_branches',
    'all_branches_lens_mean',
    'all_branches_lens_med',
    'all_branches_lens_stdevp',

    'summed_branches_lens_mean',
    'summed_branches_lens_med',
    'summed_branches_lens_stdevp',
]

OUTPUT_TITLES = [
    'Image title',
    'Mitochondrial footprint',

    'Punctate count',
    'Rod count',
    'Network count',

    'Mean rod length',
    'Median rod length',
    'Stdev rod length',

    'Total network branch count',
    'Mean network branch count',
    'Mean network branch length',
    'Mean network length',
    'Median network length',
    'Stdev network length',

    'All branch count',
    'Mean length of all branches',
    'Median length of all branches',
    'Stdev length of all branches',
    
    'Mean network and rod length',
    'Median network and rod length',
    'Stdev network and rod length',
]


def main(fiji_exec_path, root_path, regex_str, output_path, pix_to_um_scale=1.0):
    ij = imagej.init(fiji_exec_path) # /home/mitocab/Fiji.app
    print(ij.getApp().getInfo(True))

    # Load mcp_analysis macro
    print('Reading MitoCellPhe macro file at:')
    print(f'    {MACRO_PATH}')

    with open(MACRO_PATH, 'r') as f:
        mcp_macro = f.read()

    mcp_args = {
        'root_directory': root_path,
        'regex_string'  : regex_str,
        'use_ridge_detection': False,
        'verbose': False,
    }

    # Print the number of matches with the regex you provided.
    rgx       = re.compile(regex_str)
    match_cnt = 0
    for subdir, dirs, files in os.walk(root_path):
        for file in files:
            if rgx.match(file):
                match_cnt += 1

    print('Calling MitoCellPhe macro with args...')
    print('    Root directory   :', root_path)
    print('    Regex string     :', regex_str)
    print('    Number of matches:', match_cnt)
    result = ij.py.run_script('py', mcp_macro, mcp_macro) # Run MitoCellPhe on the IJ module
    ij_out = ij.py.from_java(result.getOutputs())         # Get the outputs
    py_out = {} # Have to manually copy the IJ dictionary to Python, even though
                # it is already Python-ated (because it is a JavaMap and not a dict)
                # because Pandas won't take the raw Pyimagej casting of the dict.
    
    # Filter and sort the IJ output dictionary so that only
    # the columns we want are presented, and in the proper order.
    filtered_kvs  = list([kv for kv in ij_out.items() if kv[0] in OUTPUT_FILTER])     # key/value pairs
    sorted_kvs    = sorted(filtered_kvs, key = lambda kv: OUTPUT_FILTER.index(kv[0])) # sorted key/value pairs       

    for k, v in sorted_kvs:
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

            if k in LENGTH_OUTPUTS:
                print('K,v length before ', k, v)
                for i, _ in enumerate(v):
                    v[i] = float(v[i]) / pix_to_um_scale
                print('K,v length after ', k,v)
            elif k in AREA_OUTPUTS:
                print('K,v area before ', k, v)
                for i, _ in enumerate(v):
                    v[i] = float(v[i]) / (pix_to_um_scale**2)
                print('K,v area after ', k,v)
            
            py_out[title] = v
            print(title, ':\n', py_out[title])

    df = pd.DataFrame.from_dict(py_out)
    df.to_csv(output_path)



'''
Program execution starts here.
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MitoCellPhe batch processing')

    parser.add_argument('-f', '--fiji', required=True, type=str, 
                        help='Fiji install directory (i.e. "/home/user/Fiji.app")')
    parser.add_argument('-d', '--dir', required=True, type=str, 
                        help='Root directory with skeletons (i.e. "/home/user/Documents/skels"')
    parser.add_argument('-o', '--output', required=True, type=str, 
                        help='Output .csv file path (i.e. "/home/user/Documents/skelsout.csv')
    parser.add_argument('-r', '--regex', required=False, type=str, 
                        help='Regex to find skeleton files (i.e ".*_cp_skel_[0-9]*.*")', default='.*')
    parser.add_argument('-s', '--scale', required=False, type=float, 
                        help='1 pixel = ? micrometers scale (i.e. "4.61" pixels = 1 um)', default=1.0)

    args = vars(parser.parse_args())

    main(args['fiji'], args['dir'], args['regex'], args['output'], args['scale'])
