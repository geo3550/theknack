#!/bin/python2

import knack_tools as kt
from Tkinter import *
# from PIL import Image
import tkFileDialog
import os

# Defines columns to write to output file. Must match input file's header.
# Note: Since UMID is the db's key, it automatically exports as the 
# first column.
export_header = ['Name: First', 'Name: Last', 'Department', 'Member Status']

# Defines which department to look at.
depts = ['COE - Electrical & Computer Engineering (ECE)']


def data_processor(data):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """

    # Do some processing
    processed = kt.filterdata(data, 
                    lambda person: kt.selectors.bydept(person,depts)
                )

    # Summarize some results
    nm = kt.count_duespayers(processed)
    membership = nm/float(len(processed))
    print('\n')
    print('Membership in selected departments: %d%%' % (membership*100))
    print('\n')

    return processed



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
        processed_data = self.processing_fn(data)
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
        self.root.geometry("800x140")
        self.root.resizable(True, False)

        self.createWidgets()


    def createWidgets(self):


        ############################
        # Setup some things first
        ############################

        self.status   = StringVar()
        self.input_filename = StringVar()
        self.output_filename = StringVar()

        self.input_filename.set(os.getcwd()+'/data/all_fields-1.csv')
        self.output_filename.set(os.getcwd()+'/results/out.csv')

        ## Processing


        ## Script Selection
        self.scriptoptions = ['All Actives','By Dept.','By Degree']
        self.optionlables  = StringVar()
        # Set default option
        self.optionlables.set(self.scriptoptions[0])

        ## Folder Icon
        self.foldericon = PhotoImage(file="./icons/magnifier_17.png")


        ###################################################################
        # Positions of everything in the master frame (the window itself)
        ###################################################################

        ## Base Layer (everything builds on this)
        self.master.grid()
        self.master.columnconfigure(1, weight=1)

        ## 1st row
        lbl_script = Label(self.master, text="Script:")
        lbl_script.grid(row=0, column=0, sticky='w')

        self.scriptmenu = OptionMenu(   self.master, self.optionlables,
                                        *self.scriptoptions  )
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

        outbutton = Button(   self.master, text="Select Output File",
                              command=lambda: self._getfilename_output()    )
        outbutton.config(image=self.foldericon, width="17",height="17")
        outbutton.grid(row=2, column=2)


        ## 4th row
        self.procbutton = Button(  self.master, text="Process File!", 
                                    command=self.processor_callback )
        self.procbutton.grid(row=4, column=0, columnspan=3)


        ## 5th row
        self.statusprompt = Label(self.master, textvariable = self.status)
        self.statusprompt.grid(row=3,column=0, columnspan=3)
        



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


    def setstatus(self, status):
        self.status.set(status)



    def getfilename_output(self):
        """Returns the contents of the outut file dialog box"""
        return self.output_filename.get()


    def getfilename_input(self):
        """Returns the contents of the input file dialog box"""
        return self.input_filename.get()





###############################################################################
# Create & run GUI (must be @ end of file)
###############################################################################

# Create the object that defines the gui
gui = GuiIO(data_processor, export_header)

# Run gui
gui.mainloop()  
