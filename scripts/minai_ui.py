import PySimpleGUI as sg
import webbrowser
import mina_batch
import os
import threading

def run_mina(fiji_dir, skeleton_dir, regex_str, out_folder, out_file, pix_um_scale):
    '''
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

    def mb_wrapper(fiji_dir, skeleton_dir, regex_str, out_path, pix_um_scale):
        mina_batch.main(fiji_dir, skeleton_dir, regex_str, out_path, pix_um_scale)

        # Display the "Done!" window
        layout = [ sg.Text('Batch processing done!') ]
        complete_window = sg.Window('MiNAI', layout)

        while True:
            event, vaules = about_window.read()
            print(event)
            if event == sg.WIN_CLOSED:
                break

    th = threading.Thread(
        target=mb_wrapper, 
        args=(fiji_dir, skeleton_dir, regex_str, os.path.join(out_folder, out_file), float(pix_um_scale)),
        daemon=True
    )
    th.start()

def open_docs():
    '''
    '''
    webbrowser.open('https://github.com/City303/MiNAI/wiki')

def about_window():
    '''
    '''
    layout = [ [sg.Text('MiNAI')],
               [sg.Text('By Benjamin Lowe, Carson Molder and some other people')]]
    about_window = sg.Window('About MiNAI', layout)

    while True:
        event, vaules = about_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            break


def help_fijidir():
    '''
    '''
    pass

def help_skeletonfolder():
    '''
    '''
    pass

def help_regexstr():
    '''
    '''
    pass

def help_outputdir():
    '''
    '''
    pass

def help_outputfile():
    '''
    '''
    pass

def help_pixumscale():
    '''
    '''
    pass


def main():
    TEXT_WIDTH = 18

    menu_def = [ ['&Help', ['&Documentation', '&About']]]

    layout = [ [sg.Menu(menu_def)],
               [sg.Text('Select FIJI directory',  size=(TEXT_WIDTH,1)), sg.Input(),              sg.FolderBrowse(),              sg.Button('?', key='?Fiji')] ,
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
