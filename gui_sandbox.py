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

## Make a list of (and import) all script modules that exist in this folder.
processing_functions = []
_scripts = []
for filename in os.listdir(os.getcwd()+'/scripts/'):
    if filename.endswith('.py'): 
        this_filename = filename.split('.')[-2]
        if this_filename.startswith('__'):
            continue
        
        try:
            this_script = importlib.import_module('scripts.'+this_filename,'scripts')
        except:
            ## TO DO: Handle broken modules without breaking everything
            raise 
        _scripts              += [this_script]
        processing_functions  += [this_script.processing_function]


## Make corresponding lists of meta-data for each script.
script_names = []
script_descriptions = []
for script in _scripts:
    script_names += [script.name]
    script_descriptions += [script.description]




###############################################################################
# Importers/Exporters
###############################################################################

class GuiIO(Frame):
    """Creates GUI for importing, processing, and exporting Knack data.""" 
    def __init__(self, processing_fn, export_header, master=None):
        
        ## Define functions that process data
        self.processing_fn = processing_fn
        self.export_header = export_header

        ## Create the window
        self.win = Window(self.process)


    def process(self):
        self.win.status.set("Processing ...")

        # Read in file
        data = kt.importcsv(self.win.getfilename_input())
        # Run processing function on data
        processing_fn  = self.win.get_processing_function()
        processed_data = processing_fn(data)
        # Write processed data
        kt.writecsv_byid(  processed_data, self.export_header, 
                        self.win.getfilename_output()  )

        self.win.setstatus("Done!")


    def mainloop(self):
        self.win.mainloop()



###############################################################################
# The GUI
###############################################################################

class Window(Frame):
    """Creates and manipulates the GUI"""

    def __init__(self, processor_callback, master=None):
        
        self.processor_callback = processor_callback

        ## This just builds the window 
        self.root = Tk()
        Frame.__init__(self, master)
        self.initWindow()


    def initWindow(self):
        self.master.title("sandbox")
        self.root.geometry("800x250")

        self.createWidgets()


    def createWidgets(self):


        ############################
        # Setup some things first
        ############################

        ## These are strings we use to control other things.
        ## Note that these are tkinter string objects, so
        ## to retrieve the values, we have to use "var.get()"
        self.status   = StringVar()
        self.input_filename = StringVar()
        self.output_filename = StringVar()
        self.helptext = StringVar()

        ## Default text for said strings
        self.input_filename.set(os.getcwd()+'/data/all_fields-1.csv')
        self.output_filename.set(os.getcwd()+'/results/out.csv')
        self.helptext.set(script_descriptions[0])

        ## Keep track of which script is currently selected
        self.processing_function = processing_functions[0]

        ## Script selection drop down
        self.scriptoptions = script_names
        self.selected_script  = StringVar()
        ## This sets default option for the drop down
        self.selected_script.set(self.scriptoptions[0])

        ## Folder Icon
        self.foldericon = PhotoImage(file="./icons/magnifier_17.png")


        ###################################################################
        # Position everything in the master frame (the window itself)
        ###################################################################

        ## Base Layer (everything builds on this)
        self.master.grid()
        ## This makes it so the column with all the text boxes
        ## stretches when you resize the main window
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(3, weight=1)


        ## 1st row
        lbl_script = Label(self.master, text="Script:")
        lbl_script.grid(row=0, column=0, sticky='w')
        
        self.scriptmenu = OptionMenu(   self.master, self.selected_script,
                                        *self.scriptoptions, command=self._update_script  )
        self.scriptmenu.grid(row=0, column=1, sticky="we")


        ## 2nd row
        lbl_input  = Label(self.master, text="Input File:")
        lbl_input.grid(row=1, column=0, sticky='w')

        self.input_entry = Entry(   self.master, 
                                    textvariable=self.input_filename  )
        self.input_entry.grid(row=1, column=1, sticky="we")

        inbutton = Button(  self.master,
                            command=lambda: self._getfilename_input()  )
        inbutton.config(image=self.foldericon, width="17", height="17")
        inbutton.grid(row=1, column=2)


        ## 3rd row
        lbl_output = Label(self.master, text="Output File:")
        lbl_output.grid(row=2, column=0, sticky='w')

        self.output_entry = Entry(  self.master,
                                    textvariable=self.output_filename  )
        self.output_entry.grid(row=2, column=1, sticky="we")

        outbutton = Button(   self.master,
                              command=lambda: self._getfilename_output()    )
        outbutton.config(image=self.foldericon, width="17",height="17")
        outbutton.grid(row=2, column=2)


        ## 4th row
        helptext_frame = LabelFrame(  self.master, 
                                      text="Description of Selected Script"  )
        helptext_frame.grid(row=3, column=1, sticky='nsew')
        helptext_frame.columnconfigure(0,weight=1)
        helptext_frame.rowconfigure(0,weight=1)
        
        helptext_lbl = Label(  helptext_frame, justify="left", 
                               textvariable=self.helptext  )
        helptext_lbl.grid(sticky="nw", padx=5, pady=5)


        # 5th row
        self.statusprompt = Label(self.master, textvariable = self.status)
        self.statusprompt.grid(row=4, column=0, columnspan=3)


        ## 6th row
        self.procbutton = Button(  self.master, text="Process File!", 
                                    command=self.processor_callback )
        self.procbutton.grid(row=5, column=0, columnspan=3, pady=10)
        



    def _getfilename_input(self):
        """
            Internal function. 
            This gets called when the input file search button is pressed.
        """
        self.input_filename.set(tkFileDialog.askopenfilename())


    def _getfilename_output(self):
        """
            Internal function. 
            This gets called when the output file search button is pressed.
        """
        self.output_filename.set(tkFileDialog.askopenfilename())

    def _update_script(self, new_script_name):
        """
            Internal function.
            This gets called whenever a different script gets selected
            (in the drop-down menu) 
        """
        ## Figure out which script got selected
        for idx,name in enumerate(script_names):
            if name==new_script_name:
                new_index = idx

        ## Update everything with the new script's information
        self.processing_function = processing_functions[new_index]
        self.helptext.set(script_descriptions[new_index])


    def setstatus(self, status):
        self.status.set(status)



    def getfilename_output(self):
        """Returns the contents of the outut file dialog box"""
        return self.output_filename.get()


    def getfilename_input(self):
        """Returns the contents of the input file dialog box"""
        return self.input_filename.get()


    def get_processing_function(self):
        """Returns the selected script's processing function"""
        return self.processing_function





###############################################################################
# Create & run GUI (must be @ end of file)
###############################################################################

# Create the object that defines the gui
gui = GuiIO(None, export_header)
# gui = GuiIO(data_processor, export_header)

# Run gui
gui.mainloop()  
