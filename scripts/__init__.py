import os
import sys
from traceback import print_tb

class Script():
    """Simple container that holds all the info associated with a script."""
    def __init__(self, name, description, processing_function):
        self.name                = name
        self.description         = description
        self.processing_function = processing_function


def import_scripts():
    """
    Returns a list of Script objects corresponding to all available scripts 
    in the "scripts" directory.
    """
    ## Make a list of (and import) all script modules that exist in this folder
    scripts = []
    for filename in os.listdir(os.getcwd()+'/scripts/'):
        if not filename.endswith('.py'):
            ## Skip any files that aren't python scripts.
            continue

        ## Extract the name of the module
        this_filename = filename.split('.')[-2]
        if this_filename.startswith('__'):
            continue
        try:
            ## Import script as a module
            ##   We have to use __import__ here because, for some reason,
            ##   import_module can't find the modules in the 'scripts' package 
            ##   (in python 2.7, at least)
            this_script = __import__(this_filename, globals(), locals(), [],-1)
            # this_script = importlib.import_module(this_filename)
        except:
            print(  'WARNING: The script "'+this_filename+
              '" is not valid and will be ignored. There was a problem with '+
              'importing the module; the error given was:')
            print(sys.exc_info()[0])
            print_tb(sys.exc_info()[2])
            print('\n')
            continue

        try:
            ## Pull the things we need out of the module
            if this_script.description[0]=='\n':
                this_script.description = this_script.description[1:-1]
            scripts += [Script( this_script.name, this_script.description, 
                                    this_script.processing_function  )]
        except AttributeError:
            print(  'WARNING: The script "'+this_filename+
              '" is not valid and will be ignored. All scripts must contain '+
              'a function called "processing_function", and two strings '+
              'called "name" and "description".'  )
            continue

    return scripts
