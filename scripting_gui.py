#!/bin/python2

import knack_tools as kt
from Tkinter import *
import tkFileDialog
import os
import importlib

# Defines columns to write to output file. Must match input file's header.
# Note: Since UMID is the db's key, it automatically exports as the 
# first column.
export_header = ['Name: First', 'Name: Last', 'Department', 'Member Status']


###############################################################################
# Import all scripts
###############################################################################
scripts = []

## Make a list of (and import) all script modules that exist in this folder.
_scripts = []
for filename in os.listdir(os.getcwd()+'/scripts/'):
    if not filename.endswith('.py'):
        ## Skip any files that aren't python scripts.
        continue

    ## Extract the name of the module
    this_filename = filename.split('.')[-2]
    if this_filename.startswith('__'):
        continue
    
    ## Import script as a module
    try:
        this_script = importlib.import_module('scripts.'+this_filename,'scripts')
    except:
        ## TO DO: Handle broken modules without breaking everything
        raise 

    ## Pull the things we need out of the module
    scripts += [kt.Script( this_script.name, this_script.description, 
                            this_script.processing_function  )]



###############################################################################
# Main Code
###############################################################################

class GuiIO(Frame):
    """
        Creates GUI and handles all data manipulation. When "Process File"
        button is pressed, the following procedure is triggered:
            1) import data from csv
            2) run selected processing script on data
            3) export results to csv
    """ 
    def __init__(self, available_scripts, master=None):
        ## Create the window
        self.win = kt.ScriptingWindow(self.process, available_scripts)


    def process(self):
        self.win.status.set("Processing ...")

        # Read in file
        data = kt.importcsv(self.win.getfilename_input())
        # Run processing function on data
        processing_fn  = self.win.get_processing_function()
        processed_data = processing_fn(data)
        # Write processed data
        kt.writecsv_byid(  processed_data, self.win.get_export_header(), 
                        self.win.getfilename_output()  )

        self.win.setstatus("Done!")


    def mainloop(self):
        self.win.mainloop()




###############################################################################
# Create & run GUI (must be @ end of file)
#   This is what actually starts the program
###############################################################################

# Create the object that defines the gui
gui = GuiIO(scripts)

# Run gui
gui.mainloop()  
