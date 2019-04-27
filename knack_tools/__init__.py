# -*- coding: utf-8 -*-

"""
knack_tools.py
v0.2

This is a library of tools that can be used to more easily 
& consistently work with data from Knack.

'data' organization:
    The outer level is a dictionary, each key is a UMID (as a string).

    Corresponding to each UMID is another dictionary of every column
    in the input file (except "Employer ID"). For example:

    data = {
      '93819370': {'Name: First':'Foo', 'Name: Last':'Bar'},
      '83927489': {'Name: First':'Josie', 'Name: Last':'Cat'}
    }

""" 


from Tkinter import *
from ScrolledText import ScrolledText
import tkFileDialog
import json
import unicodecsv as csv
# import csv
import os, time
from io import BytesIO
from copy import copy



# local modules
import selectors
from constants import *





###############################################################################
# Data Processing Functions
###############################################################################


def count_duespayers(data):
    ii = 0
    for p in data.values():
        if p['Member Status'] == 'Union Dues': ii += 1
    return ii

def count_nonpayers(data):
    ii = 0
    for p in data:
        if p['Member Status'] == 'Non-Payer': ii += 1
    return ii







###############################################################################
# File I/O
###############################################################################

def filterdata(data, selector_fn):
    """
    Given a dictionary of people, call 'selector_fn' for each person      
    and remove any entries that return 'None'
    """
    # First, decide whether or not to keep each row
    data = {id: selector_fn(data[id]) for id in data.keys()}

    # Then, remove the entries left empty by 'selector_fn'
    filtered_data = dict((k, v) for k, v in data.iteritems() if v)

    return filtered_data

 
def parsebyid(lines):
    """
    Given raw data, parse each line into a dictionary representing
    that person's data, then return a dictionary of each person,
    using UMIDs as the keys.
    """

    # Sanitize column labels and find the UMID column
    header = [elt.strip() for elt in lines[0]]
    id_index = header.index('Employee ID')

    # Remove '3550' prefix from everything
    for idx, line in enumerate(lines[1:]):
        lines[idx+1] = [remove_prefix(elt,'3550.') for elt in line]
    
    # Create dictionary for each person
    keys = header
    del keys[id_index]
    ids = []
    data = []
    for line in lines[1:]:
        ids = ids+[ line[id_index] ]
        del line[id_index]

        datum = dict(zip(keys,line))
        data = data+[ datum ]

    # Create overall dictionary of all the people
    # We end up with this structure:
    # data{umid}{column_label} => data for specific person.
    return [dict(zip(ids,data)), header, ids]


def remove_prefix(s,prefix):
    return s[len(prefix):] if s.startswith(prefix) else s

 
def parsestews(lines):
    """
    Given raw export of stews list,
    parse each line into a dictionary with departments as keys
    and a list of stewards' names as values.
    """

    # Sanitize column labels and find the Depatment column
    header = [elt.strip() for elt in lines[0]]

    # There's actually 2 "Department" columns in the Stewards list
    dept_index = [ii for ii, h in enumerate(header) if h=='Department'][-1]
    name_index = header.index('Name')

    # Create unduplicated list of all stewarded departments
    depts = list({line[dept_index] for line in lines[1:]})
    # Initialize dictionary with empty lists for each departmet
    stews = dict(zip(depts,[[]]*len(depts)))

    for line in lines[1:]:
        if not line[dept_index]:
            continue
        stews[line[dept_index]] = stews[line[dept_index]] + [line[name_index]]

    # Remove unassigned stewards (these are typ. ex-stews)
    del stews['']

    return stews


def parserosched(lines):
    """
    Given raw export of registrar's office schedule 
    (found at: http://ro.umich.edu/schedule/), parse each line
    into a dictionary with instructor of the form:
        {last_name: [row_data0 row_data1 ...]}
    where each 'row_data' represents a row with the same instructor
    last name and is encoded as a dictionary of the form:
        {column label: data}
    """

    # Sanitize column labels and find the Instructor column
    header = [elt.strip() for elt in lines[0]]
    lname_index = header.index('Instructor')

    # Parse the Instructor column
    lnames_byrow = []
    for line in lines[1:]:
        lnames_byrow = lnames_byrow + [line[lname_index].split(', ')]

    # Create unduplicated list of all instructors
    lnames = []
    for row in lnames_byrow:
        lnames = lnames + row
    lnames = list(set(lnames))

    # Initialize dictionary with empty lists for each last name
    d = dict(zip(lnames,[[]]*len(lnames)))
    # ...and the dictionary for an empty row
    column_labels = lines[0]; column_labels.pop(lname_index)
    mtrow = dict(zip(column_labels,[[]]*len(column_labels)))

    # Extract each line & assign it to the appropriate name
    for r, line in enumerate(lines[1:]):
        if not line[lname_index]:
            continue

        row_dict = copy(mtrow)
        for c, clabel in enumerate(column_labels):
            row_dict[clabel] = line[c]
        for name in lnames_byrow[r]:
            d[name] = d[name] + [row_dict]

    return d 



def importstews(filename):
    # Read in file
    lines = _readcsv(filename)

    # Process raw data
    data = parsestews(lines)
    return data


def importrosched(filename):
    # Read in file
    lines = _readcsv(filename)

    # Process raw data
    data = parserosched(lines)
    return data


def importcsv(filename):
    print "Processing data ..."
    # Read in file
    lines = _readcsv(filename)

    # Process raw data
    data, header, ids = parsebyid(lines)
    return data 


def _readcsv(filename):

    # dirname = os.path.dirname(filename)
    # os.chdir(dirname)

    with open(filename, "rb") as f:
        csvreader = csv.reader(f, encoding='utf-8-sig')
        lines = [line for line in csvreader]
    f.close()

    # No idea why csvreader isn't removing the quotes in first cell...
    lines[0][0] = lines[0][0].strip('"')
    return lines


def writecsv_byid(data_to_write, export_header, filename):
    if not export_header:
        return
    if export_header == 'all fields':
        ids = data_to_write.keys()
        export_header = data_to_write[ids[0]].keys()

    if not data_to_write:
        return

    ## Test a random person to see if all the columns are there.
    ## If not, warn the user and remove the column.
    person = data_to_write[data_to_write.keys()[0]]
    for idx,column_name in enumerate(export_header):
        if not column_name in person:
            warntxt = 'WARNING: The column "'+column_name+'" to be exported '+\
                      'does not exist in the data. It will be removed.'
            print(warntxt)
            del export_header[idx]


    print "Writing data ..."
    with open(filename, "wb") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['UMID']+export_header)
        for id in data_to_write.keys():
            try:
                row = [data_to_write[id][col] for col in export_header]
            except KeyError:
                print(id)
                print(data_to_write[id])
                raise
            csvwriter.writerow([id]+row)
    f.close()



def writecsv_summary(data_to_write, filename):
    print "Writing summary ..."
    with open(filename, "wb") as f:
        csvwriter = csv.writer(f)
        for row in data_to_write:
            csvwriter.writerow(row)
    f.close()






###############################################################################
# Importers/Exporters
###############################################################################

class GuiIO(Frame):
    """Creates Simple GUI to import, process, and export Knack data.""" 
    def __init__(   self, processing_fn, export_header, 
                    out_filename='./out.csv', master=None   ):
        Frame.__init__(self, master)
        self.status = StringVar()
        self.filename = StringVar()
        self.createWidgets()
        self.grid()
        self.processing_fn = processing_fn
        self.export_header = export_header
        self.out_filename = out_filename
    def createWidgets(self):
        #self.tokenprompt = Label(text = "Access token:")
        #self.tokenentry = Entry()
        self.filebutton = Button(   self, text="Select Input File",
                                    command=self.getfilename    )
        self.filenameprompt = Label(textvariable = self.filename)
        self.getunbutton = Button(  self, text="Process File!", 
                                    command=self.process )
        self.statusprompt = Label(textvariable = self.status)

        #self.tokenprompt.grid(row=0, column=0)
        #self.tokenentry.grid(row=0, column=1)
        self.filenameprompt.grid(row=1, column=0, columnspan=2)
        self.filebutton.grid(row=2, column=0)
        self.getunbutton.grid(row=3, column=0)
        self.statusprompt.grid(row=3, column=1)
    def getfilename(self):
        self.filename.set(tkFileDialog.askopenfilename())
    def process(self):
        self.status.set("Processing ...")

        # Read in file
        data = importcsv(self.filename.get())
        # Run processing function on data
        processed_data = self.processing_fn(data)
        # Write processed data
        writecsv_byid(processed_data, self.export_header, self.out_filename)

        self.status.set("Done!")

    # NOTE: "mainloop" function is inherited from the "Frame" class


class AutomaticIO():
    """Imports, processes, and exports Knack data from given file.""" 
    class m:
        """Dummy class to make the interface similar to GuiIO"""
        def title(self,txt): pass


    def __init__(   self, in_filename, processing_fn, export_header, 
                    out_filename='out.csv', master=None  ):
        print(os.getcwd())
        self.filename = in_filename
        self.out_filename = out_filename
        self.processing_fn = processing_fn
        self.export_header = export_header
        self.master = self.m()


    def mainloop(self):
        # Read in file
        data = importcsv(self.filename)
        _data = data
        # Run processing function on data
        processed_data = self.processing_fn(data)
        # Write processed data
        writecsv_byid(processed_data, self.export_header, self.out_filename)
  


###############################################################################
# The Scripting GUI Window
###############################################################################

class ScriptingWindow(Frame):
    """Builds out what you see on the screen."""

    def __init__(self, available_scripts, title='Knack Scripts', master=None):
        self.avail_scripts = available_scripts
        self.title = title

        ## This just builds the window 
        self.root = Tk()
        Frame.__init__(self, master)
        self.initWindow()


    def initWindow(self):
        self.master.title(self.title)
        self.root.geometry("920x420")

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
        self.input_filename.set(os.getcwd()+'/data/all_actives-4-26-19.csv')
        self.output_filename.set(os.getcwd()+'/results/out.csv')

        ## Keep track of which script is currently selected
        self.processing_function = self.avail_scripts[0].processing_function

        ## Script selection drop down
        self.scriptoptions = [script.name for script in self.avail_scripts]
        self.selected_script  = StringVar()
        ## This sets default option for the drop down
        self.selected_script.set(self.scriptoptions[0])

        ## Folder Icon
        self.foldericon = PhotoImage(file=os.getcwd()+"/icons/magnifier_17.png")


        ###################################################################
        # Position everything in the master frame (the window itself)
        ###################################################################

        ## Base Layer (everything builds on this)
        self.master.grid()
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        ###########
        # First frame separates the 
        # checkboxes from everything else.
        frame1 = Frame(self.master)
        frame1.grid(sticky='nsew')
        ## This makes it so this frame
        ## stretches when you resize the main window
        frame1.columnconfigure(0, weight=1)
        frame1.rowconfigure(0, weight=1)


        ###########
        # Second layer of frames form the 
        # base for the checkboxes and
        # everything else, respectively.
        frame_primary    = Frame(frame1)
        frame_checkboxes = LabelFrame(frame1, text="Data to Export")

        frame_primary.grid(row=0, column=0, sticky='nsew')
        frame_checkboxes.grid(row=0, column=1, sticky='nsew')

        ## Stretch the column with all the text boxes
        frame_primary.columnconfigure(1, weight=1)
        ## Stretch the row with the script description
        frame_primary.rowconfigure(3, weight=1)



        ###########
        # Build primary frame

        ## 1st row
        lbl_script = Label(frame_primary, text="Script:")
        lbl_script.grid(row=0, column=0, sticky='w')
        
        self.scriptmenu = OptionMenu(   frame_primary, self.selected_script,
                                        *self.scriptoptions, 
                                        command=self._update_script  )
        self.scriptmenu.grid(row=0, column=1, sticky="we")


        ## 2nd row
        lbl_input  = Label(frame_primary, text="Input File:")
        lbl_input.grid(row=1, column=0, sticky='w')

        self.input_entry = Entry(   frame_primary, 
                                    textvariable=self.input_filename  )
        self.input_entry.grid(row=1, column=1, sticky="we")

        inbutton = Button(  frame_primary,
                            command=lambda: self._getfilename_input()  )
        inbutton.config(image=self.foldericon, width="17", height="17")
        inbutton.grid(row=1, column=2)


        ## 3rd row
        lbl_output = Label(frame_primary, text="Output File:")
        lbl_output.grid(row=2, column=0, sticky='w')

        self.output_entry = Entry(  frame_primary,
                                    textvariable=self.output_filename  )
        self.output_entry.grid(row=2, column=1, sticky="we")

        outbutton = Button(   frame_primary,
                              command=lambda: self._getfilename_output()    )
        outbutton.config(image=self.foldericon, width="17",height="17")
        outbutton.grid(row=2, column=2)


        ## 4th row
        helptext_frame = LabelFrame(  frame_primary, 
                                      text="Description of Selected Script"  )
        helptext_frame.grid(row=3, column=1, sticky='nsew')
        helptext_frame.columnconfigure(0,weight=1)
        helptext_frame.rowconfigure(0,weight=1)
       
        self.helptext_lbl = ScrolledText(  helptext_frame, wrap=WORD  )
        self.helptext_lbl.insert(INSERT,self.avail_scripts[0].description)
        self.helptext_lbl.config(state=DISABLED)
        self.helptext_lbl.grid(sticky="nsew", padx=5, pady=5)


        # 5th row
        self.statusprompt = Label(frame_primary, textvariable = self.status)
        self.statusprompt.grid(row=4, column=0, columnspan=3)


        ## 6th row
        self.procbutton = Button(  frame_primary, text="Process File!", 
                                    command=self.run_script )
        self.procbutton.grid(row=5, column=0, columnspan=3, pady=10)
       

        ###########
        # Build checkbox frame

        ## Each element: [header_text, is_checked_by_default]
        common_data = [
            ['Individual',           True ],
            ['Name: First',          False],
            ['Name: Last',           False],
            ['Department',           True ],
            ['Secondary Department', False],
            ['Employer Unique Name', False],
            ['Employment Status',    False],
            ['Member Status',        True ],
            ['Preferred Email',      True ],
            ['Secondary Email',      True ],
            ['Assessment',           True ],
            ['Last Assessment Date', True ],
            ['Hire Date',            False],
            ['FTE',                  False]
        ]

        checkboxes = []
        self.checkbox_strings = []
        self.checkbox_values  = []
        for idx,export_elt in enumerate(common_data):
            ## Set default checkbox state
            this_value = IntVar()
            if export_elt[1]:
                this_value.set(1)
            else:
                this_value.set(0)

            ## Build checkbox
            this_box = Checkbutton( frame_checkboxes, text=export_elt[0], 
                                    variable=this_value )
            this_box.grid(row=idx, column=0, sticky='w')

            ## Save stuff for later
            self.checkbox_strings += [export_elt[0]]
            self.checkbox_values  += [this_value]
            checkboxes += [this_box]

        lblstr = 'Custom Entry:\n(comma separated, e.g. "Building,Office #")'
        user_header_lbl = Label(frame_checkboxes, text=lblstr)
        user_header_lbl.grid()

        self.user_header_text = StringVar()
        user_header = Entry(  frame_checkboxes, 
                              textvariable=self.user_header_text  )
        user_header.grid(sticky='we')




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
        script_names = [script.name for script in self.avail_scripts]
        for idx,name in enumerate(script_names):
            if name==new_script_name:
                new_index = idx

        ## Update everything with the new script's information
        self.processing_function = self.avail_scripts[new_index].\
                                        processing_function
        
        ## Need to update the textbox explicitly, since it doesn't
        ## support linking to a StringVar
        self.helptext_lbl.config(state=NORMAL)
        self.helptext_lbl.delete(1.0,END)
        self.helptext_lbl.insert(  INSERT, 
                        self.avail_scripts[new_index].description  )
        self.helptext_lbl.config(state=DISABLED)


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


    def get_export_header(self):
        """Returns a list of all headers that are selected with checkboxes"""

        ## Get headers from checkboxes
        export_header = []
        checkbox_values = [check.get() for check in self.checkbox_values]
        for idx,checkbox_value in enumerate(checkbox_values):
            if checkbox_value==1:
                export_header += [self.checkbox_strings[idx]]

        ## Get user-added headers
        user_str = self.user_header_text.get()
        if user_str:
            export_header += user_str.split(',')

        return export_header


    def run_script(self):
        """This is the top-level processing function. 

              It is called when the "Process File" button is pressed
              and does the following:
                1) import data from csv
                2) run selected processing script on data
                3) export results to csv
        """
        self.status.set("Processing ...")

        try:
            # Read in file
            data = importcsv(self.getfilename_input())
            # Run processing function on data
            processing_fn  = self.get_processing_function()
            processed_data = processing_fn(data)
            # Write processed data
            writecsv_byid(  processed_data, self.get_export_header(), 
                            self.getfilename_output()  )
        except:
            self.setstatus("Processing Error :-( (see command prompt)")
            raise
            

        self.setstatus("Done!")



