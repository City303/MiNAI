import PySimpleGUI as sg
import webbrowser
import mina_batch
import os
import threading

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
                     [sg.Text('By Benjamin Lowe, Carson Molder and some other people')]]
    about_window = sg.Window('About MiNAI', about_layout)

    while True:
        event, vaules = about_window.read()
        if event == sg.WIN_CLOSED:
            break


def help_fijidir():
    '''Opens a window explaining what the FIJI executable directory is,
    and that Jython needs to be installed.
    '''
    help_layout = [ [sg.Text('Click "Browse" and navigate to where Fiji is installed on your computer.')],
                    [sg.Text('For example, it may be:')],
                    [sg.Text('    Windows: C:\\Users\\{your username}\\Fiji.app')],
                    [sg.Text('    Linux: /home/{your username}/fiji.app')],
                    [sg.Text('Also, make sure the Jython plugin is installed in your Fiji installation for MiNAI to work.')]]
    help_window = sg.Window('Help', help_layout)
    
    while True:
        event, vaules = help_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break

def help_skeletonfolder():
    '''Opens a window explaining what the skeleton folder is, what it
    should include, and why you should use the skeleton pipeline in
    CellProfiler to generate them.
    '''
    help_layout = [ [sg.Text('')],
                    [sg.Text('')]]
    help_window = sg.Window('Help', help_layout)

    while True:
        event, vaules = about_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break

def help_regexstr():
    '''Opens a window explaining what the regular expression is, along
    with a link to the Python guide for them.
    '''
    help_layout = [ [sg.Text('')],
                    [sg.Text('')]]
    help_window = sg.Window('Help', help_layout)

    while True:
        event, vaules = about_window.read()
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
        event, vaules = about_window.read()
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
        event, vaules = about_window.read()
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
        event, vaules = about_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break


def main():
    TEXT_WIDTH = 18

    menu_def = [ ['&Help', ['&Documentation', '&About']]]

    layout = [ [sg.Menu(menu_def)],
               [sg.Text('Select FIJI directory',  size=(TEXT_WIDTH,1)), sg.Input(),             sg.FolderBrowse(),              sg.Button('?', key='?Fiji')] ,
               [sg.Text('Select skeleton folder', size=(TEXT_WIDTH,1)), sg.Input(),             sg.FolderBrowse(),            sg.Button('?', key='?SkeletonFolder')],
               [sg.Text('Regex string',           size=(TEXT_WIDTH,1)), sg.InputText('.*'),                                   sg.Button('?', key='?Regex')],
               [sg.Text('Select output folder',   size=(TEXT_WIDTH,1)), sg.Input(),             sg.FolderBrowse(),            sg.Button('?', key='?OutputDir')],
               [sg.Text('Output file name',       size=(TEXT_WIDTH,1)), sg.Input('output.csv'),                               sg.Button('?', key='?OutputFile')],
               [sg.Text('1 pix = ? um',           size=(TEXT_WIDTH,1)), sg.InputText(),         sg.Button('?', key='?Scale'), sg.Text('(optional)')],
               [sg.Button('Run'), sg.Button('Quit')] ]

    window = sg.Window('MiNAI', layout)

    while True:
        event, values = window.read()
        print(event, values)

        if event == 'Documentation':
            # Open web browser to GitHub docs
            open_docs()
        elif event == 'About':
            about_window()
        elif event == 'Run':
            run_mina(values[1], values[2], values[3], values[4], values[5], values[6])
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

if __name__ == '__main__':
    main()
