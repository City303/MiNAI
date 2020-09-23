import PySimpleGUIQt as sg
import webbrowser
import mina_batch
import os
import threading
import pickle

# CONSTANT VARIABLE DECLARATION
TEXT_WIDTH = 16

#FUNCTION DECLARATION/IMPLEMENTATION

def run_mina(fiji_dir, skeleton_dir, regex_str, out_folder, out_file, pix_um_scale):
    '''Calls the mina_batch.py script with the given parameters,
    along with a callback to inform you the program has completed.

    Parameters:
        fiji_dir:     string
            - A path pointing to the install folder for FIJI (with the Jython plugin installed).
        skeleton_dir: string
            - A path pointing to where the mitochondrial skeletons can be found
        regex_str:    string
            - A Python regular expression filtering files in the skeleton_dir so that only
              the desired skeleton images will be parsed (assuming they all follow a common
              file name type)
        out_folder:   string
            - A path pointing to where the output csv file will be saved
        out_file:     string
            - A filename for the output file (should end in .csv)
        pix_um_scale: string or float
            - A value representing the amount of micrometer equal to one pixel.
    '''
    print('Fiji executable dir :', fiji_dir)
    print('Input directory     :', skeleton_dir)
    print('Regex string        :', regex_str)
    print('Output directory    :', out_folder)
    print('Output file         :', out_file)
    print('Where the outfile is:', os.path.join(out_folder, out_file))
    print('Pix to um scale     :', pix_um_scale)

    if pix_um_scale == '':
        pix_um_scale = 1.0
    else:
        pix_um_scale = float(pix_um_scale)

    def mb_wrapper(fiji_dir, skeleton_dir, regex_str, out_path, pix_um_scale):
        mina_batch.main(fiji_dir, skeleton_dir, regex_str, out_path, pix_um_scale)

        # Display the "Done!" window
        done_layout = [ [sg.Text('Batch processing done!')] ]
        done_window = sg.Window('Update', done_layout)

        while True:
            event, vaules = done_window.read()
            print(event)
            if event == sg.WIN_CLOSED:
                break

    th = threading.Thread(
        target=mb_wrapper, 
        args=(fiji_dir, skeleton_dir, regex_str, os.path.join(out_folder, out_file), pix_um_scale),
        daemon=True
    )
    th.start()

def open_docs():
    '''Opens the GitHub wiki so a user can read about how the program works.
    '''
    webbrowser.open('https://github.com/City303/MiNAI/wiki')

def about_window():
    '''Opens an about window to give credit to the authors / paper.
    '''
    about_layout = [ [sg.Text('MiNAI')],
                     [sg.Text('By Benjamin Lowe, Carson Molder and some other people')],
                     [sg.Button('Close')] ]
    about_window = sg.Window('About MiNAI', about_layout)

    while True:
        event, vaules = about_window.read()
        if event == sg.WIN_CLOSED or event == 'Close':
            break

    about_window.close()


def help_fijidir():
    '''Opens a window explaining what the FIJI executable directory is,
    and that Jython needs to be installed.
    '''
    help_layout = [ [sg.Text('Click "Browse" and select the folder Fiji is installed on your computer.')],
                    [sg.Text('For example, it may be:')],
                    [sg.Text('    Windows: C:\\Users\\{your username}\\Fiji.app\\')],
                    [sg.Text('    Linux:   /home/{your username}/Fiji.app/')],
                    [sg.Text('Also, make sure the Jython plugin is installed in your Fiji installation for MiNAI to work.')],
                    [sg.Button('Close', size=(15,0.9))] ]
    help_window = sg.Window('Help', help_layout)
    
    while True:
        event, vaules = help_window.read()
        print(event)
        if event == sg.WIN_CLOSED or event == 'Close':
            break
        
    help_window.close()
        
def help_skeletonfolder():
    '''Opens a window explaining what the skeleton folder is, what it
    should include, and why you should use the skeleton pipeline in
    CellProfiler to generate them.
    '''
   
    help_layout = [ [sg.Text('Help: Skeleton Folder', justification='center')],
                    [sg.Text('The skeleton folder is the root directory containing the skeletonized images.')],
                    [sg.Text('The program will search for skeleton images in ALL subdirectories (subfolders) of this folder.')],
                    [sg.Text('IF your skeleton folder contains other images (eg. original stain images, phase contrast images),')],
                    [sg.Text('then use the Regex string field to select the stain images.')],
                    [sg.Text('This will only work if your skeleton images have a consistent naming scheme that can be matched to a Regex pattern.')],
                    [sg.Button('Close', size=(15,0.9))] ]
    help_window = sg.Window('Help', help_layout)

    while True:
        event, vaules = help_window.read()
        print(event)
        if event == sg.WIN_CLOSED or event == 'Close':
            break

    help_window.close()

def help_regexstr():
    '''Opens a window explaining what the regular expression is, along
    with a link to the Python guide for them.
    '''
    help_layout = [ [sg.Text('')],
                    [sg.Text('')]]
    help_window = sg.Window('Help', help_layout)

    while True:
        event, vaules = help_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break

def help_outputdir():
    '''Opens a window explaining what the output directory is.
    '''
    help_layout = [ [sg.Text('')],
                    [sg.Text('')]]
    help_window = sg.Window('Help', help_layout)

    while True:
        event, vaules = help_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break

def help_outputfile():
    '''Opens a window explaining what the output file is.
    '''
    help_layout = [ [sg.Text('')],
                    [sg.Text('')]]
    help_window = sg.Window('Help', help_layout)

    while True:
        event, vaules = help_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break

def help_pixumscale():
    '''Opens a window explaining what the 1 px = ? um scale is.
    '''
    help_layout = [ [sg.Text('')],
                    [sg.Text('')]]
    help_window = sg.Window('Help', help_layout)

    while True:
        event, values = help_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break

def checkValues(values):
    '''
    Check the input fields for run to make sure they are valid..
    '''
    pass

def save_params(main_menu_values):
    save_layout = [ [sg.Text('Saves the config values')],
                    [sg.Text('Folder', size=(TEXT_WIDTH,1)), sg.Input(size=(2*TEXT_WIDTH, 0.85), key='-FOLDER-'), sg.FolderBrowse(size=(10,0.9))],
                    [sg.Text('Filename', size=(TEXT_WIDTH,1)), sg.Input(size=(2*TEXT_WIDTH, 0.85),key='-CONFIGFN-')],
                    [sg.Button('Save'), sg.Button('Cancel')] ]
    save_window = sg.Window('Save Parameters...', save_layout)

    while True:
        event, values = save_window.read()
        print(event)
        print(values)
        if (event == sg.WIN_CLOSED or event == 'Cancel'):
            break
        elif event == 'Save':
            #make a pickle of main_menu_values to file given by Filename
            #check valid filenames...
            create=True
            if(values['-FOLDER-'] == ''):
                sg.popup_error('Path to folder cannot be empty!')
                create=False
            elif(values['-CONFIGFN-'] == ''):
                sg.popup_error('Filename cannot be empty!')
                create=False
            elif(os.path.exists(values['-FOLDER-']) == False):
                 out = sg.popup_yes_no('Folder ' + str(repr(values['-FOLDER-'])) + ' does not exist.', 'Do you want to create it now?')
                 if(out == 'Yes'):
                     os.makedirs(os.path.join('~',values['-FOLDER-']))
                 else:
                     create=False
            elif(os.path.exists(os.path.join(values['-FOLDER-'], values['-CONFIGFN-'])) == True):
                 out = sg.popup_yes_no('File already exists.', 'Do you wish to overwrite?')
                 if(out == 'No'):
                     create=False
            if(create):
                pickle.dump(main_menu_values, open(os.path.join(values['-FOLDER-'],values['-CONFIGFN-']), "wb"))
                break

    save_window.close()

                                       
def load_params():
    load_layout = [ [sg.Text('Loads config values from file')],
                    [sg.Text('File Path', size=(TEXT_WIDTH,1)), sg.Input(size=(2*TEXT_WIDTH,0.85), key='-FILELOC-'), sg.FileBrowse(size=(10,0.9))],
                    [sg.Button('Load'), sg.Button('Cancel')] ]
    load_window = sg.Window('Load Parameters...', load_layout)
    new_values = None
    
    while True:
        event, values = load_window.read()
        print(event)
        print(values)
        if (event == sg.WIN_CLOSED or event == 'Cancel'):
            break
        elif event == 'Load':
            #load the pickle
            load=True
            if(values['-FILELOC-'] == ''):
                sg.popup_error('File location cannot be empty!')
                load=False
            elif(os.path.exists(values['-FILELOC-']) == False):
                 sg.popup_error('File does not exist!')
                 load=False
            if(load):
                 new_values = pickle.load(open(values['-FILELOC-'], "rb"))
                 break

    load_window.close()             
    return new_values
                 
                                       
def main():

    sg.set_options(font='Cantarell 12')

    menu_def = [['&File', ['&Save Parameters', '&Load Parameters', '&Quit']], ['&Help', ['&Documentation', '&About']]]
                 
    layout = [ [sg.Menu(menu_def)],
               [sg.Text('MiNAI Morphology Analysis Settings', justification='center')],
               # [sg.Button('Load Parameters', size=(24,0.85), key='-LOAD-'), sg.Button('Save Parameters', size=(24,0.85),key='-SAVE-')],
               [sg.Text('Select FIJI directory',  size=(TEXT_WIDTH,1)), sg.Input(size=(2*TEXT_WIDTH,0.85),key='-FIJIDIRin-'),    sg.FolderBrowse(size=(10,0.9),key='-FIJIDIRBrowse-'), sg.Button('?', key='?Fiji', size=(4,0.9))] ,
               [sg.Text('Select skeleton folder', size=(TEXT_WIDTH,1)), sg.Input(size=(2*TEXT_WIDTH,0.85), key='-SKELSELECTin-'),sg.FolderBrowse(size=(10,0.9), key='SKELSELECTBrowse-'), sg.Button('?', key='?SkeletonFolder', size=(4,0.9))],
               [sg.Text('Regex string',           size=(TEXT_WIDTH,1)), sg.InputText('.*', size=(2*TEXT_WIDTH,0.85),key='-REGEX-'),                             sg.Button('?', key='?Regex', size=(4,0.9))],
               [sg.Text('Select output folder',   size=(TEXT_WIDTH,1)), sg.Input(size=(2*TEXT_WIDTH,0.85),key='-OUTPUTFOLDERin-'),               sg.FolderBrowse(size=(10,0.9),key='-OUTPUTFOLDERBrowse-'), sg.Button('?', key='?OutputDir', size=(4,0.9))],
               [sg.Text('Output file name',       size=(TEXT_WIDTH,1)), sg.Input('output.csv', size=(2*TEXT_WIDTH,0.85),key='-OUTPUTFILENAMEin-'),                                 sg.Button('?', key='?OutputFile', size=(4,0.9))],
               [sg.Text('1 pix = ? um',           size=(TEXT_WIDTH,1)), sg.InputText(size=(2*TEXT_WIDTH,0.85), key='-SCALEin-'),           sg.Button('?', key='?Scale', size=(4,0.9)),   sg.Text('(optional)')],
               [sg.Button('Run', size=(15,0.9)), sg.Button('Quit', size=(15,0.9))] ]

    window = sg.Window('MiNAI', layout)

    while True:
        event, values = window.read()
        print(event, values)

        if event == 'Documentation':
            # Open web browser to GitHub docs
            open_docs()
        elif event == 'About':
            about_window()
        elif event == 'Save Parameters':
            save_params(values)
        elif event == 'Load Parameters':
            new_values = load_params()
            print('new_values from load:', new_values)
            if(new_values is not None):
                print('NEW_VALUES:')
                for key, val in new_values.items():
                    print('key', key, 'item', val)
                    if key == 0:
                        continue
                    window[key].update(val)
                #print('VALUES:')
                #for key,val in values.items():
                #    print('key', key, 'item', val)
                #values = new_values
        elif event == 'Run':
            #run_mina(fiji_dir, skeleton_dir, regex_str, out_folder, out_file, pix_um_scale)
            run_mina(values['-FIJIDIRin-'], values['-SKELSELECTin-'], values['-REGEX-'], values['-OUTPUTFOLDERin-'], values['-OUTPUTFILENAMEin-'], values['-SCALEin-'])
        elif event == '?Fiji':
            help_fijidir()
        elif event == '?SkeletonFolder':
            help_skeletonfolder()
        elif event == '?Regex':
            help_regexstr()
        elif event == '?OutputDir':
            help_outputdir()
        elif event == '?OutputFile':
            help_outputfile()
        elif event == '?Scale':
            help_pixumscale()

        elif event == sg.WIN_CLOSED or event == 'Quit':
            break
        
    window.close()

if __name__ == '__main__':
    main()
